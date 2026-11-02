"""Evaluate data completeness and geometry without modifying navigation."""
import importlib.util
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from replay_data import make_scene,shapes,hull
from view_replay import complete_frames,export


def test_scene_has_every_authored_model_actor_and_three_robot_envelopes():
    scene=make_scene(ROOT)
    world=ET.parse(ROOT/'social_navigation_sim/worlds/social_dynamic.sdf').getroot().find('world')
    names={e.get('name') for tag in ['model','actor'] for e in world.findall(tag)}
    assert names|{'robot1','robot2','robot3'}==set(scene['objects'])
    assert scene['objects']['tv_viewer_a_walking']['kind']=='human'
    assert scene['objects']['pair_a']['proxy']=='pair_a_contact'
    assert scene['objects']['pair_a_contact']['facing_source']=='pair_a'
    assert abs(scene['objects']['pair_a_contact']['facing_offset']+3.141592653589793/2)<1e-5
    assert scene['objects']['robot3']['radius']==.15


def test_shape_projection_preserves_link_offset_and_height():
    model=ET.fromstring('<model><link><pose>1 2 3 0 0 0</pose><collision><pose>0 0 1 0 0 0</pose><geometry><box><size>2 4 2</size></box></geometry></collision></link></model>')
    shape=shapes(model)[0]
    assert set(shape['polygon'])=={(0.,0.),(2.,0.),(2.,4.),(0.,4.)}
    assert shape['z']==[3.,5.] and shape['collision']
    assert hull([(0,0),(1,0),(1,1),(0,1),(.5,.5)])==[(0,0),(1,0),(1,1),(0,1)]


def test_plugin_survives_both_worlds_and_regeneration_is_idempotent():
    sys.path.insert(0,str(ROOT/'social_navigation_sim/scripts'))
    from replay_plugin_config import add_replay_plugin
    for name in ['social_static','social_dynamic']:
        world=ET.parse(ROOT/f'social_navigation_sim/worlds/{name}.sdf').getroot().find('world')
        add_replay_plugin(world);add_replay_plugin(world)
        assert len([p for p in world.findall('plugin') if p.get('name')=='rescue::ReplayRecorder'])==1


def test_partial_live_frame_is_not_parsed_and_old_session_is_rejected(tmp_path):
    with pytest.raises(ValueError):complete_frames(tmp_path/'world_frames.jsonl')
    p=tmp_path/'world_frames.jsonl';p.write_text('{"t":1,"objects":[]}\n{"t":')
    assert complete_frames(p)==[{'t':1,'objects':[]}]


def test_export_is_standalone_and_does_not_close_script_from_a_name(tmp_path):
    (tmp_path/'scene.json').write_text(json.dumps({'objects':{'</script>':{}},'bounds':[-1,-1,1,1]}))
    (tmp_path/'world_frames.jsonl').write_text('{"t":1,"epoch":0,"objects":[]}\n')
    result=tmp_path/'replay.html';export(tmp_path,result)
    text=result.read_text()
    assert '__REPLAY_DATA__' not in text
    assert '\\u003c/script>' in text
    assert 'canvas' in text and 'Lưu ảnh PNG' in text


def test_goal_history_export_and_incomplete_line(tmp_path):
    from view_replay import complete_goals
    assert complete_goals(tmp_path)==[]
    (tmp_path/'scene.json').write_text('{"objects":{},"bounds":[-1,-1,1,1]}')
    (tmp_path/'world_frames.jsonl').write_text('{"t":1,"epoch":0,"objects":[]}\n')
    goal={'t':.5,'epoch':0,'sequence':1,'xy':[.2,.3]}
    (tmp_path/'goals.jsonl').write_text(json.dumps(goal)+'\n'+ '{"unfinished":')
    assert complete_goals(tmp_path)==[goal]
    export(tmp_path,tmp_path/'replay.html')
    assert '"goals": [{"t": 0.5' in (tmp_path/'replay.html').read_text()


def test_backup_excludes_live_recording_data(tmp_path):
    from create_backup import create_backup,verify_backup
    (tmp_path/'source.txt').write_text('source')
    (tmp_path/'recordings/live').mkdir(parents=True)
    (tmp_path/'recordings/live/data.jsonl').write_text('runtime')
    folder=create_backup(tmp_path,'exclude_runtime_test')
    manifest=verify_backup(folder)
    assert 'source.txt' in manifest['file_sha256']
    assert not any(name.startswith('recordings/') for name in manifest['file_sha256'])
