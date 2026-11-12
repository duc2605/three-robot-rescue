"""Additional map contracts; does not start ROS or Gazebo."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

ROOT=Path(__file__).resolve().parents[1]


def test_third_world_has_physics_traffic_and_replay():
    world=ET.parse(ROOT/'worlds/street_intersection.sdf').getroot().find('world')
    assert world.get('name')=='street_intersection'
    plugins={p.get('name') for p in world.findall('plugin')}
    assert {'rescue::StreetTraffic','rescue::ReplayRecorder'}<=plugins
    assert 'rescue::SocialScenarioMotion' not in plugins
    plugin=next(p for p in world.findall('plugin') if p.get('name')=='rescue::StreetTraffic')
    assert len(plugin.findall('vehicle'))==12
    assert len(plugin.findall('agent'))==8
    assert {p.findtext('kind') for p in plugin.findall('agent')}=={'walker','runner','cane','dog','walk_to_run'}
    for vehicle in plugin.findall('vehicle'):
        assert len(vehicle.findall('point'))>=4
        assert float(vehicle.findtext('initial_s'))<float(vehicle.findtext('stop_s'))
    models={m.get('name'):m for m in world.findall('model')}
    for actor in plugin.findall('agent'):
        name=actor.findtext('name')
        assert models[name].findall('link/collision')
        assert all(name+'_limb_'+str(i) in models for i in range(4))
    switch=next(e for e in plugin.findall('agent') if e.findtext('kind')=='walk_to_run')
    assert float(switch.findtext('running_speed'))>float(switch.findtext('speed'))
    assert float(switch.findtext('run_after_distance'))>0
    assert models['cane_walker'].find("link/collision[@name='walking_cane_collision']") is not None


def test_map_geometry_and_scene_bounds_match():
    config=yaml.safe_load((ROOT/'map/street_intersection.yaml').read_text())
    pgm=(ROOT/'map'/config['image']).read_bytes().split(b'\n',3)
    assert pgm[:3]==[b'P5',b'800 800',b'255']
    assert len(pgm[3])==800*800
    assert config['origin']==[-40.,-40.,0.]
    scene=json.loads((ROOT/'config/street_intersection_scene.json').read_text())
    assert scene['bounds']==[-40,-40,40,40]
    assert not scene['map_contains_people']
    # All three initial robots are in known free space, outside buildings.
    for x,y in ((10.,-12.),(11.,-12.),(10.5,-11.2)):
        col=int((x+40)/.1);row=int((40-y)/.1)
        assert pgm[3][row*800+col]==254


def test_only_new_bridge_world_and_distinct_routes():
    entries=yaml.safe_load((ROOT/'config/gz_bridge/street_intersection_bridge.yaml').read_text())
    assert any(e['gz_topic_name']=='/world/street_intersection/dynamic_pose/info' for e in entries)
    assert not any('social_static' in e['gz_topic_name'] or 'social_dynamic' in e['gz_topic_name'] for e in entries)
    scene=json.loads((ROOT/'config/street_intersection_scene.json').read_text())
    assert {v['turn'] for v in scene['vehicles']}=={'straight','left','right'}
    assert {v['approach'] for v in scene['vehicles']}==set(range(4))


def test_signal_heads_are_supported_and_face_the_approach():
    import math
    world=ET.parse(ROOT/'worlds/street_intersection.sdf').getroot().find('world')
    models={m.get('name'):m for m in world.findall('model')}
    plugin=next(p for p in world.findall('plugin') if p.get('name')=='rescue::StreetTraffic')
    assert len(plugin.findall('pedestrian_signal'))==8
    for head in plugin.findall('signal'):
        index=int(head.findtext('approach'));yaw=float(head.findtext('yaw'))
        assert abs(yaw-index*math.pi/2)<1e-9
        x,y=map(float,head.findtext('xy').split())
        stop=(-10*math.cos(yaw)+2.5*math.sin(yaw),-10*math.sin(yaw)-2.5*math.cos(yaw))
        toward=(stop[0]-x,stop[1]-y)
        assert (-math.cos(yaw)*toward[0]-math.sin(yaw)*toward[1])/math.hypot(*toward)>.8
        support=models[f'traffic_pole_{index}']
        for color in ('red','yellow','green'):
            bulb=models[f'signal_{index}_{color}']
            pose=list(map(float,bulb.findtext('pose').split()))
            pole=list(map(float,support.findtext('pose').split()))
            assert pose[:2]==pole[:2] and abs(pose[5]-yaw)<1e-9
            assert bulb.find('link/pose') is None
    for index,head in enumerate(plugin.findall('pedestrian_signal')):
        x,y=map(float,head.findtext('xy').split());yaw=float(head.findtext('yaw'))
        assert (-math.cos(yaw))*(-x)+(-math.sin(yaw))*(-y)>0
        assert models[f'pedestrian_pole_{index}'].findall('link/collision')
        for label in ('walk','wait'):
            assert len(models[f'pedestrian_{index}_{label}'].findall('link/visual'))>=6


def test_pedestrian_route_asset_blocks_junction_shortcuts():
    config=yaml.safe_load((ROOT/'map/street_pedestrian.yaml').read_text())
    data=(ROOT/'map'/config['image']).read_bytes().split(b'\n',3)[3]
    def free(x,y):
        return data[int((40-y)/.1)*800+int((x+40)/.1)]>200
    assert not free(0,0)
    assert not free(3,0)
    assert free(8,0) and free(-8,0)
    assert free(0,8) and free(0,-8)
    assert free(10.5,-11.2)


def test_vehicle_stop_position_accounts_for_front_and_painted_line():
    world=ET.parse(ROOT/'worlds/street_intersection.sdf').getroot().find('world')
    plugin=next(p for p in world.findall('plugin') if p.get('name')=='rescue::StreetTraffic')
    for vehicle in plugin.findall('vehicle'):
        gap=26.-.07-(float(vehicle.findtext('stop_s'))+1.33)
        assert abs(gap-.15)<1e-8
    assert [int(head.findtext('axis')) for head in plugin.findall('pedestrian_signal')]==[0]*4+[1]*4


def test_opposing_vehicle_heads_start_green_together():
    world=ET.parse(ROOT/'worlds/street_intersection.sdf').getroot().find('world')
    models={m.get('name'):m for m in world.findall('model')}
    for approach in range(4):
        green=float(models[f'signal_{approach}_green'].findtext('pose').split()[2])
        red=float(models[f'signal_{approach}_red'].findtext('pose').split()[2])
        assert (green>0)==(approach%2==0)
        assert (red>0)==(approach%2==1)
    scene=json.loads((ROOT/'config/street_intersection_scene.json').read_text())
    assert scene['signals']['vehicle_approach_pairs']==[[0,2],[1,3]]
