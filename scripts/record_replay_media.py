#!/usr/bin/env python3
"""Run ROS launch and record real X11 Gazebo/RViz windows for replay."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

from replay_media import update_media, build_camera_videos


def window_candidates(text):
    result = {}
    for line in text.splitlines():
        match = re.search(r'(0x[0-9a-fA-F]+)\s+"([^"\n]*)"', line)
        if not match:
            continue
        ident, title = match.groups()
        title = title.lower()
        # Prefer the real application title, never the browser's replay frame.
        if title.strip() == 'gazebo' or title.startswith('gazebo '):
            result.setdefault('gazebo', ident)
        if 'rviz' in title and ('rviz' == title.strip() or '.rviz' in title or 'rviz2' in title):
            result.setdefault('rviz', ident)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('Missing command after --')
    folder = args.session.resolve()
    media = folder/'media'
    media.mkdir(exist_ok=True)
    ffmpeg, xwininfo = shutil.which('ffmpeg'), shutil.which('xwininfo')
    available = bool(ffmpeg and xwininfo and os.environ.get('DISPLAY'))
    update_media(folder, state='recording' if available else 'unavailable', streams=[], clock=[],
                 window_error=None if available else 'Cần ffmpeg, xwininfo và phiên X11 để ghi cửa sổ Gazebo/RViz.',
                 camera_state='recording')
    if not available:
        print('Video Gazebo/RViz chưa bật: cần ffmpeg, xwininfo và DISPLAY/X11.', flush=True)
    stopped = False
    stop_requested = None
    process = subprocess.Popen(command, start_new_session=True)
    captures = {}
    streams = []
    clock = []
    offset = 0
    partial = b''
    origin = time.monotonic()
    last_manifest = last_probe = 0.
    def stop(signum, frame):
        nonlocal stopped, stop_requested
        stopped = True
        if stop_requested is None:
            stop_requested = time.monotonic()
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGINT)
            except ProcessLookupError:
                pass
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        while process.poll() is None:
            now = time.monotonic()-origin
            if stopped and time.monotonic()-stop_requested > 20:
                break
            path = folder/'world_frames.jsonl'
            if path.exists():
                if path.stat().st_size < offset:
                    offset, partial = 0, b''
                with path.open('rb') as source:
                    source.seek(offset)
                    chunk = source.read(1024*1024)
                    offset += len(chunk)
                parts = (partial+chunk).split(b'\n')
                partial = parts.pop()
                if parts:
                    latest = json.loads(parts[-1])
                    clock.append(dict(wall=now, t=latest['t'], epoch=latest.get('epoch', 0)))
            if available and not stopped and now-last_probe >= 2.:
                last_probe = now
                try:
                    output = subprocess.run([xwininfo, '-root', '-tree'], capture_output=True, text=True, timeout=3)
                except (OSError, subprocess.TimeoutExpired):
                    output = subprocess.CompletedProcess([], 1, stdout='')
                for kind, ident in window_candidates(output.stdout).items():
                    if kind in captures:
                        continue
                    name = kind+'.mp4'
                    log = (media/(kind+'.log')).open('wb')
                    encoder = subprocess.Popen([
                        ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'warning', '-y',
                        '-f', 'x11grab', '-framerate', '8', '-window_id', ident,
                        '-i', os.environ['DISPLAY'], '-an',
                        '-vf', 'scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2',
                        '-c:v', 'libx264', '-threads', '1', '-preset', 'ultrafast', '-crf', '29',
                        '-pix_fmt', 'yuv420p', '-g', '16',
                        '-movflags', '+frag_keyframe+empty_moov+default_base_moof', str(media/name)],
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=log, start_new_session=True)
                    captures[kind] = (encoder, log)
                    streams.append(dict(kind=kind, file=name, wall_start=time.monotonic()-origin,
                                        timebase='wall', note='Video cửa sổ X11 thực; đồng bộ gần đúng theo clock mẫu.'))
            for kind, (encoder, _) in captures.items():
                stream = next(s for s in streams if s['kind'] == kind)
                if encoder.poll() is not None and 'wall_end' not in stream:
                    stream['wall_end'] = now
                    video = media/stream['file']
                    stream['state'] = ('recorded' if encoder.returncode == 0 else 'partial') if video.is_file() and video.stat().st_size > 0 else 'error'
            if now-last_manifest >= 1.:
                last_manifest = now
                update_media(folder, streams=streams, clock=clock)
            time.sleep(.2)
    finally:
        if process.poll() is None:
            stop(signal.SIGINT, None)
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        for kind, (encoder, log) in captures.items():
            was_running = encoder.poll() is None
            if was_running:
                encoder.send_signal(signal.SIGINT)
            try:
                encoder.wait(timeout=8)
            except subprocess.TimeoutExpired:
                encoder.kill()
                encoder.wait()
            log.close()
            stream = next(s for s in streams if s['kind'] == kind)
            stream.setdefault('wall_end', time.monotonic()-origin)
            video = media/stream['file']
            stream.setdefault('state', 'recorded' if video.is_file() and video.stat().st_size > 0 else 'error')
        update_media(folder, streams=streams, clock=clock, state='finished')
        try:
            print('Đang chuẩn bị video camera cho replay…', flush=True)
            build_camera_videos(folder)
        except Exception as error:
            update_media(folder, camera_state='error', camera_error=str(error)[-500:])
    return process.returncode


if __name__ == '__main__':
    raise SystemExit(main())
