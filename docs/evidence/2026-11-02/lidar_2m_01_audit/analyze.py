"""Read a bounded snapshot of the user's replay; never publish commands."""
import collections
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'recordings/lidar_2m_01'


def snapshot(path):
    with path.open('rb') as stream:
        blob = stream.read(path.stat().st_size)
    blob = blob[:blob.rfind(b'\n')+1]
    return [json.loads(line) for line in blob.splitlines() if line.strip()], {
        'path': str(path.relative_to(ROOT)), 'complete_bytes': len(blob),
        'sha256_complete_prefix': hashlib.sha256(blob).hexdigest()}


frames, provenance = snapshot(SOURCE / 'world_frames.jsonl')
controllers = {}
metadata = [provenance]
for name in ['robot1', 'robot2', 'robot3']:
    rows, meta = snapshot(SOURCE / f'stop_{name}.jsonl')
    metadata.append(meta)
    controllers[name] = [r for r in rows if r.get('kind') == 'controller']
contacts = collections.defaultdict(list)
for frame in frames:
    for contact in frame.get('contacts', []):
        if 'ground_plane' not in [contact['a'], contact['b']]:
            contacts[tuple(sorted([contact['a'], contact['b']]))].append((frame['epoch'], contact))
episodes = []
for pair, rows in contacts.items():
    combined = []
    for epoch, contact in rows:
        if (combined and epoch == combined[-1]['epoch']
                and contact['first_t'] <= combined[-1]['last_t'] + .1):
            combined[-1]['last_t'] = max(combined[-1]['last_t'], contact['last_t'])
        else:
            combined.append({'pair': pair, 'epoch': epoch,
                             'first_t': contact['first_t'], 'last_t': contact['last_t'],
                             'first_contact': contact})
    episodes.extend(combined)
episodes.sort(key=lambda e: (e['epoch'], e['first_t']))


def near_row(name, seconds):
    return min(controllers[name], key=lambda r: abs(r['t']-seconds))


def near_frame(seconds):
    return min(frames, key=lambda r: abs(r['t']-seconds))


def position(name, seconds):
    return next(o['p'][:2] for o in near_frame(seconds)['objects'] if o['name'] == name)


def compact(name, seconds):
    row = near_row(name, seconds)
    selected = row.get('selected_lidar_tracks', [])
    yaw = row['pose'][2]
    vx, vy = row['command'][:2]
    return {**{k: row.get(k) for k in [
        'robot', 't', 'reason', 'command', 'pose', 'astar', 'astar_age',
        'rejected_checks', 'state_age_sim', 'scan_age_sim', 'state_age_wall',
        'scan_age_wall', 'compute_elapsed_wall_ms', 'peer_prediction_ages',
        'selected_lidar_tracks', 'tracks', 'limits', 'safety_status']},
        'command_world_xy': [vx*math.cos(yaw)-vy*math.sin(yaw),
                             vx*math.sin(yaw)+vy*math.cos(yaw)],
        'frame_positions': {n: position(n, row['t']) for n in
                            ['robot1', 'robot2', 'robot3', 'patrol_person',
                             'tv_viewer_a_walking', 'tv_viewer_a_returning']}}

checkpoints = [compact(name, t) for name, times in [
    ('robot2', [29., 29.7, 30., 30.5, 31., 31.5, 32.1]),
    ('robot3', [78., 79., 80., 81., 82., 83., 84., 84.5, 85.]),
    ('robot1', [90., 91., 91.5, 92., 92.5, 93., 93.9, 139., 147., 147.3, 147.5, 147.6]),
    ('robot3', [147., 147.3, 147.5, 147.6])]
    for t in times]
config = json.loads((SOURCE/'diagnostics_config.json').read_text())
source_matches = {name: hashlib.sha256(Path(entry['path']).read_bytes()).hexdigest() == entry['sha256']
                  for name, entry in config['sources'].items()}
zeros = [r for r in controllers['robot1'] if 147. <= r['t'] <= 147.600001]
payload = {
    'session': str(SOURCE.relative_to(ROOT)), 'frame_count': len(frames),
    'frame_time': [frames[0]['t'], frames[-1]['t']], 'source_snapshot': metadata,
    'source_matches': source_matches, 'goals': snapshot(SOURCE/'goals.jsonl')[0],
    'contact_episodes': episodes, 'non_ground_pair_count': len(contacts),
    'controller_summary': {name: {
        'sample_time': [rows[0]['t'], rows[-1]['t']],
        'reason_counts': dict(collections.Counter(r['reason'] for r in rows)),
        'camera_used': sorted(set(r.get('avoidance_use_camera') for r in rows)),
    } for name, rows in controllers.items()},
    'zero_command_motion': {'robot': 'robot1', 'interval': [147., 147.6],
        'samples': len(zeros), 'all_saved_commands_zero': all(not any(r['command']) for r in zeros),
        'root_xy_start': position('robot1', 147.), 'root_xy_end': position('robot1', 147.6),
        'root_xy_displacement': math.dist(position('robot1', 147.), position('robot1', 147.6)),
        'limit': 'Internal saved commands only; no wheel velocity/effort or proof of the physical cause.'},
    'limits': ['Observed contacts confirm engine contact, not just disk overlap.',
               'No pixel or full raw rays were recorded; perception cannot be fully rerun.',
               'A* proposal is not the issued MPC trajectory.',
               'No new navigation changes or simulation startup/shutdown in this audit.',
               'The older 90s test did not certify this different longer run.']}
(OUT/'analysis.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
(OUT/'checkpoints.json').write_text(json.dumps(checkpoints, ensure_ascii=False, indent=2)+'\n')
windows = [(29., 33.1), (77., 87.), (89., 96.5), (137., 141.5), (145.5, 148.5),
           (189.5, 194.), (198.5, 203.), (243., frames[-1]['t'])]
with gzip.open(OUT/'contact_windows.jsonl.gz', 'wt') as stream:
    for f in frames:
        if any(a <= f['t'] <= b for a, b in windows):
            stream.write(json.dumps(f)+'\n')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
for ax, (start, end, names, title) in zip(axes.flat, [
    (29., 33., ['robot2', 'tv_viewer_a_walking'], 'Follower 1: incorrect motion estimate, late escape'),
    (78., 87., ['robot3', 'patrol_person'], 'Leader: retreats along approach, then moves sideways'),
    (90., 96., ['robot1', 'tv_viewer_a_returning'], 'Follower 2: pauses, short escape, blocked rollouts'),
    (146.5, 148., ['robot1', 'robot3'], 'Robot-robot: motion continues during zero command')]):
    colors = {'robot1': '#d84343', 'robot2': '#2675c6', 'robot3': '#079965',
              'tv_viewer_a_walking': '#e69a22', 'tv_viewer_a_returning': '#a4832c', 'patrol_person': '#8a53b4'}
    for name in names:
        values = [(f['t'], next(o['p'][:2] for o in f['objects'] if o['name'] == name))
                  for f in frames if start <= f['t'] <= end]
        ax.plot([p[0] for _, p in values], [p[1] for _, p in values], color=colors[name], label=name)
        for t in range(math.ceil(start), math.floor(end)+1):
            p = position(name, t); q = position(name, t+.2)
            ax.annotate('', q, p, arrowprops={'arrowstyle': '->', 'color': colors[name]})
            ax.annotate(str(t), p, xytext=(4, 4), textcoords='offset points', fontsize=8, color=colors[name])
    for e in episodes:
        if start <= e['first_t'] <= end and set(e['pair']) == set(names):
            for n in names:
                ax.scatter(*position(n, e['first_t']), marker='x', c='red', s=65)
    ax.set(title=title, xlabel='World X (m)', ylabel='World Y (m)')
    ax.set_aspect('equal', adjustable='datalim'); ax.grid(alpha=.3); ax.legend(fontsize=8)
fig.suptitle('lidar_2m_01 — red crosses: first recorded physics contact; arrows: actual root motion')
fig.tight_layout(); fig.savefig(OUT/'contact_trajectories.png', dpi=150); plt.close(fig)
print(json.dumps({'frame_time': payload['frame_time'], 'pairs': len(contacts), 'episodes': len(episodes),
                  'source_matches': source_matches, 'zero_command_motion': payload['zero_command_motion']}, indent=2))
