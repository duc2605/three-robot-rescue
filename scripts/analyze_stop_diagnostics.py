#!/usr/bin/env python3
"""Summarize manually enabled stop diagnostics and match physics contacts."""
import argparse
from collections import Counter
import json
from pathlib import Path


def rows(path):
    with path.open('rb') as stream:
        for line in stream:
            if not line.endswith(b'\n'):
                break
            if line.strip():
                yield json.loads(line)


def analyze(folder):
    streams = {}
    summary = {'directory':str(folder), 'streams':{}, 'physics_contact_context':[],
               'limits':['Counters count first rejected checks, not unique paths or collision impacts.',
                         'Diagnostic windows may be missing or capped; absence is not evidence of safety.',
                         'Sim-time alignment is approximate callback timing; no raw images or full scans stored.']}
    for path in sorted(folder.glob('stop_*.jsonl')):
        data = [r for r in rows(path) if r.get('kind')]
        streams[path.stem.removeprefix('stop_')] = data
        reasons = Counter(r.get('reason') for r in data)
        compute = [r['compute_elapsed_wall_ms'] for r in data if r.get('compute_elapsed_wall_ms') is not None]
        summary['streams'][path.name] = {'samples':len(data), 'reasons':dict(reasons),
            'max_compute_elapsed_wall_ms':max(compute,default=None),
            'nonzero_command_with_team_pose_stall':sum(bool(r.get('measured_team_pose_stall_under_command')) for r in data),
            'max_dropped_records':max((r.get('dropped_records',0) for r in data),default=0)}
    contact_file = folder/'world_frames.jsonl'
    intervals = {}
    if contact_file.exists():
        for frame in rows(contact_file):
            for c in frame.get('contacts',[]):
                if 'ground_plane' in (c['a'],c['b']):
                    continue
                key = (frame['epoch'],*sorted((c['a'],c['b'])))
                intervals.setdefault(key,[]).append((c['first_t'],c['last_t']))
    for (epoch,a,b),values in intervals.items():
        episodes = []
        for first,last in sorted(values):
            if episodes and first-episodes[-1][1] <= .1:
                episodes[-1][1] = max(last,episodes[-1][1])
            else:
                episodes.append([first,last])
        for first,last in episodes:
            context = {}
            for name in ['coordinator',a,b]:
                if name != 'coordinator' and not name.startswith('robot'):
                    continue
                candidates = [r for r in streams.get(name,[]) if r['epoch']==epoch and first-1 <= r['t'] <= first+.5]
                before = [r for r in candidates if r['t'] <= first]
                after = [r for r in candidates if r['t'] > first]
                context[name] = (before[-2:]+after[:1]) or {'missing':'No saved diagnostic sample within -1/+0.5 sim s of contact onset'}
            summary['physics_contact_context'].append({'epoch':epoch,'pair':[a,b],'first_t':first,'last_t':last,'context':context})
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session',type=Path,required=True)
    args = parser.parse_args()
    if not args.session.is_dir():parser.error('Recording directory does not exist')
    print(json.dumps(analyze(args.session.resolve()),ensure_ascii=False,indent=2))
