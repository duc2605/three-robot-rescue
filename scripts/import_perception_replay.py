#!/usr/bin/env python3
"""Attach original NK-078 camera/social evidence to its replay, without inventing frames."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'social_navigation_sim/scripts'))
from replay_perception import social_regions


def attach(session,evidence):
    # The old observer did not store epochs. Never guess across a clock reset.
    epochs=set()
    with (session/'world_frames.jsonl').open() as stream:
        for line in stream:
            try:epochs.add(json.loads(line)['epoch'])
            except ValueError:continue
    if epochs!={0}:raise ValueError('This historical import requires a single recorded epoch0')
    events=evidence/'social_events.jsonl';rows=[]
    for line in events.read_text().splitlines():
        e=json.loads(line);topic=e['topic']
        if topic=='/social_navigation/markers':
            markers=[];stamps=[]
            for m in e['data']['markers']:
                if m['ns']!='camera_social_regions':continue
                h=m['header'];stamps.append(h['stamp']['sec']+h['stamp']['nanosec']*1e-9)
                markers.append(dict(id=m['id'],type=m['type'],action=m['action'],frame=h['frame_id'],
                    points=[[p['x'],p['y']] for p in m['points']],text=m['text'],color=[m['color'][k] for k in ['r','g','b','a']]))
            rows.append(dict(t=e['t'],stamp=max(stamps) if stamps else e['t'],epoch=0,kind='social',regions=social_regions(markers),source='imported_original_nk078_social_markers'))
        elif topic=='/social_navigation/status':
            rows.append(dict(t=e['t'],stamp=e['t'],epoch=0,kind='social_status',text=e['data']))
    images=sorted(evidence.glob('detection_*.jpg'))
    for image in images:
        t=float(image.stem.removeprefix('detection_'))
        rows.append(dict(t=t,stamp=None,capture_known=False,epoch=0,kind='camera',source='detection',
            sparse_snapshot=True,image='data:image/jpeg;base64,'+base64.b64encode(image.read_bytes()).decode()))
    rows.sort(key=lambda r:r['t'])
    with (session/'perception.jsonl').open('x') as stream:
        for row in rows:stream.write(json.dumps(row,allow_nan=False,separators=(',',':'))+'\n')
    metadata={'source':str(evidence),'source_event_sha256':hashlib.sha256(events.read_bytes()).hexdigest(),
        'images':[{ 'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in images],
        'rows':len(rows),'note':'Derived attachment from original records. Six sparse received-time snapshots; capture time unavailable. No interpolated camera frames or fabricated zones.'}
    (session/'perception_import.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(f'Attached {len(images)} original snapshots and {len(rows)-len(images)} original social records')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session',type=Path,required=True);parser.add_argument('--evidence',type=Path,required=True)
    args=parser.parse_args();attach(args.session,args.evidence)
