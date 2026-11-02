"""Opt-in bounded stop windows. No ROS subscriptions or navigation decisions."""
from collections import deque
import json
import math
import os
from pathlib import Path
import queue
import threading
import time


def finite_json(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): finite_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_json(v) for v in value]
    return value


class StopDiagnostics:
    """3 wall seconds before / 5 after a stop ends, at most 10 samples/s.

    Trigger on commanded zero, empty reference, or a fresh team pose that
    fails to move under command. Replay verifies actual motion. Windows extend
    throughout a continued hold, then retain five wall seconds after recovery. Bounded queue drops diagnostic records rather than blocking.
    """
    def __init__(self, directory, name, wall_clock=time.monotonic):
        self.path = Path(directory) / ('stop_' + name + '.jsonl')
        self.wall_clock = wall_clock
        self.ring = deque(maxlen=40)
        self.since = None
        self.until = -math.inf
        self.cooldown = -math.inf
        self.last_wall = -math.inf
        self.last_sim = None
        self.epoch = 0
        self.sequence = 0
        self.queue = queue.Queue(maxsize=256)
        self.dropped = 0
        self.error = None
        self.closed = False
        self.thread = threading.Thread(target=self._write, daemon=True)
        self.thread.start()

    @classmethod
    def from_environment(cls, name):
        directory = os.environ.get('SOCIAL_STOP_DIAGNOSTICS_DIRECTORY')
        return cls(directory, name) if directory else None

    def _enqueue(self, record):
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            self.dropped += 1

    def observe(self, sim, context, stopped):
        if self.error or self.closed:
            return
        wall = self.wall_clock()
        if self.last_sim is not None and sim < self.last_sim:
            self.epoch += 1
            self.ring.clear()
            self.since = None
            self.until = self.cooldown = -math.inf
            self.last_wall = -math.inf
        self.last_sim = sim
        if wall - self.last_wall < .1 - 1e-9:
            return
        self.last_wall = wall
        self.sequence += 1
        record = finite_json(dict(context, t=sim, epoch=self.epoch, wall_unix=time.time(),
                      wall_monotonic=wall, sequence=self.sequence,
                      commanded_stop=bool(stopped) if context.get('kind') != 'coordinator' else None,
                      dropped_records=self.dropped))
        while self.ring and wall-self.ring[0]['wall_monotonic'] > 3.:
            self.ring.popleft()
        pose = context.get('pose')
        pose_stalled = False
        if not stopped and pose is not None and context.get('state_age_sim', math.inf) < .5:
            older = [entry for entry in self.ring if entry.get('pose') is not None
                     and .5 <= sim-entry['t'] <= 1.5]
            if older:
                old = older[-1]['pose']
                pose_stalled = (math.dist(pose[:2],old[:2]) < .015
                                and abs(math.atan2(math.sin(pose[2]-old[2]),
                                                   math.cos(pose[2]-old[2]))) < .03)
        record['measured_team_pose_stall_under_command'] = pose_stalled
        self.ring.append(record)
        if stopped or pose_stalled:
            if self.since is None:
                self.since = wall
        else:
            self.since = None
        if wall <= self.until:
            if stopped or pose_stalled:
                self.until = wall + 5.
            self._enqueue(record)
        elif (stopped or pose_stalled) and wall-self.since >= .5 and wall >= self.cooldown:
            self.until = wall + 5.
            self.cooldown = wall + 10.
            self._enqueue(dict(event='stop_window', t=sim, epoch=self.epoch,
                               wall_unix=time.time(), pre_wall_seconds=3,
                               post_wall_seconds=5, trigger=context.get('diagnostic_trigger', 'team_pose_stall_under_command' if pose_stalled else 'commanded_stop_or_empty_reference')))
            for entry in self.ring:
                self._enqueue(entry)

    def _write(self):
        output = None
        size = 0
        try:
            while True:
                item = self.queue.get()
                if item is None:
                    break
                text = json.dumps(finite_json(item), ensure_ascii=False, allow_nan=False)+'\n'
                size += len(text.encode())
                if size > 20*1024*1024:
                    self.error = '20 MiB diagnostic limit reached; recording disabled'
                    break
                if output is None:
                    output = self.path.open('x')
                output.write(text)
                output.flush()
        except Exception as error:
            self.error = str(error)
        finally:
            if output is not None:
                output.close()

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            self.queue.put(None, timeout=.5)
        except queue.Full:
            return
        self.thread.join(timeout=1.)
