"""Sparse goal selections for opt-in replay; never changes navigation goals."""
import json
import math
import os
from pathlib import Path


class GoalHistory:
    def __init__(self, directory):
        self.path = Path(directory)/'goals.jsonl'
        self.previous = None
        self.epoch = 0
        self.sequence = 0
        self.goal = None

    @classmethod
    def from_environment(cls):
        directory = os.environ.get('SOCIAL_REPLAY_DIRECTORY')
        return cls(directory) if directory else None

    def update_clock(self, now):
        if self.previous is not None and now < self.previous:
            self.epoch += 1
            if self.goal is not None:
                self._write(now, 'retained_after_clock_reset')
        self.previous = now

    def select(self, now, xy):
        if not all(math.isfinite(v) for v in xy):
            return
        self.update_clock(now)
        self.goal = tuple(xy)
        self._write(now, 'selected_goal')

    def _write(self, now, source):
        self.sequence += 1
        record = dict(t=now,epoch=self.epoch,sequence=self.sequence,xy=self.goal,
                      source=source,meaning='Selected map goal; route feasibility not guaranteed')
        with self.path.open('a') as output:
            output.write(json.dumps(record,allow_nan=False)+'\n')
