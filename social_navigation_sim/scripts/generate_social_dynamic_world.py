#!/usr/bin/env python3
"""Derive an opt-in kinematic scenario without modifying social_static assets.

Postures change between seated, standing and drinking pause. Translation has
physical collision bodies; articulated walk / sit-to-stand animation is not
simulated. All schedules are ground truth, isolated from sensor perception.
"""
import copy
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from scene_geometry import Scene, element, pose, values, PIXELS, ORIGIN, RESOLUTION
from map_geometry import collision_shapes, rasterize
from scenario_motion import route


def generate(package, watch_seconds=12., walk_speed=.35, patrol_speed=.4):
    if (not all(math.isfinite(v) for v in (watch_seconds, walk_speed, patrol_speed))
            or watch_seconds < 0 or not .1 <= walk_speed <= .8 or not .1 <= patrol_speed <= .8):
        raise ValueError('Use nonnegative watch time and walking speeds between .1 and .8 m/s')
    scene = Scene()
    scene.root = ET.parse(package/'worlds/social_static.sdf').getroot()
    scene.world = scene.root.find('world')
    scene.world.set('name', 'social_dynamic')
    manifest = json.loads((package/'config/social_static_scene.json').read_text())
    scene.people, scene.obstacles = manifest['people'], manifest['obstacles']
    scene.box('bed_frame', -3.9, -.25, 2.15, .95, .35, (.3, .23, .16, 1), annotate=True)
    scene.box('bed_mattress', -3.9, -.25, 2.05, .9, .15, (.65, .75, .84, 1),
              base=.35, annotate=True)
    scene.person('sleeping_person', -3.9, -.25, 0., 'lying_still_script', 'sleeping')
    sleeper = scene.world.find("model[@name='sleeping_person']")
    link = sleeper.find('link')
    visual = link.find('visual')
    visual.find('pose').text = values((-.85, 0., .72, math.pi/2, 0., math.pi/2))
    collision = link.find('collision')
    collision.find('pose').text = values((0., 0., .71, 0., 0., 0.))
    collision.remove(collision.find('geometry'))
    element(element(element(collision, 'geometry'), 'box'), 'size', '1.85 .65 .45')
    scene.people[-1].update(posture='lying', height=.95)
    scene.box('water_dispenser', 5.65, 2.15, .5, .55, 1.0, (.7, .8, .85, 1), annotate=True)
    scene.box('water_bottle', 5.65, 2.15, .25, .3, .4, (.2, .55, .85, 1),
              base=1., annotate=True)

    viewer = next(p for p in scene.people if p['name'] == 'tv_viewer_a')
    chair = (viewer['x'], viewer['y'])
    yaw = viewer['yaw']
    # Leave the chair through its open front, pass east of the TV, then water.
    outward = (chair[0]+.85*math.cos(yaw), chair[1]+.85*math.sin(yaw))
    points = [chair, outward, (-.8, -2.5), (1.6, -2.5), (1.6, 2.15), (5., 2.15)]
    watch_end, stand_end = watch_seconds, watch_seconds+2.
    outgoing = route(stand_end, points, walk_speed, yaw)
    drink_start, drink_end = outgoing[-1][0], outgoing[-1][0]+6.
    returning = route(drink_end, list(reversed(points)), walk_speed, 0.)
    sit_start, cycle = returning[-1][0], returning[-1][0]+2.
    scene.person('tv_viewer_a_walking', *chair, yaw, 'walking_to_or_from_water', 'tv_group')
    scene.person('tv_viewer_a_drinking', *points[-1], 0., 'drinking_pause_script', 'tv_group')
    scene.person('patrol_person', -5.6, -4.8, 0., 'walking_patrol_script', 'patrol')
    patrol = route(0., [(-5.6, -4.8), (4.85, -4.8), (4.85, 4.6), (1.6, 4.6),
                       (1.6, -2.), (-2., -2.), (-5.6, -4.8)], patrol_speed)
    # Close the heading as well as the position at the loop boundary.
    patrol_end = patrol[-1][0]+abs((patrol[-1][4]+math.pi) % (2*math.pi)-math.pi)/.75
    patrol.append([patrol_end, -5.6, -4.8, 0., 0.])

    def motion(model, start, end, period, keys):
        return dict(model=model, start=start, end=end, period=period, keyframes=keys)

    motions = [
        motion('tv_viewer_a', 0., stand_end, cycle,
               [[0., *chair, 0., yaw], [watch_end, *chair, 0., yaw], [stand_end, *chair, .35, yaw]]),
        motion('tv_viewer_a_walking', stand_end, drink_start, cycle, outgoing),
        motion('tv_viewer_a_drinking', drink_start, drink_end, cycle,
               [[drink_start, *points[-1], 0., 0.], [drink_end, *points[-1], 0., 0.]]),
        motion('tv_viewer_a_walking', drink_end, cycle, cycle,
               returning+[[cycle, *chair, 0., yaw]]),
        motion('patrol_person', 0., patrol_end, patrol_end, patrol),
    ]
    # One model may have disjoint active intervals. Give each interval its own
    # physical model so an inactive track cannot hide another active track.
    returning_model = copy.deepcopy(scene.world.find("model[@name='tv_viewer_a_walking']"))
    returning_model.set('name', 'tv_viewer_a_returning')
    scene.world.append(returning_model)
    motions[3]['model'] = 'tv_viewer_a_returning'
    returned = dict(next(p for p in scene.people if p['name'] == 'tv_viewer_a_walking'))
    returned['name'] = 'tv_viewer_a_returning'
    scene.people.append(returned)
    for m in motions:
        model = scene.world.find(f"model[@name='{m['model']}']")
        if m['start'] > 0:
            model.find('pose').text = '0 0 -50 0 0 0'
    plugin = element(scene.world, 'plugin', filename='libsocial_scenario_motion.so',
                     name='rescue::SocialScenarioMotion')
    for m in motions:
        node = element(plugin, 'motion')
        for tag in ('model', 'start', 'end', 'period'):
            element(node, tag, m[tag])
        for t, x, y, z, heading in m['keyframes']:
            key = element(node, 'key')
            element(key, 'time', t)
            pose(key, (x, y, z), heading)
    ET.indent(scene.root, space='  ')
    ET.ElementTree(scene.root).write(package/'worlds/social_dynamic.sdf', encoding='utf-8', xml_declaration=True)

    # Furniture only. People and scripted paths must not leak into robot maps.
    physical = copy.deepcopy(scene.root)
    people_names = {p['name'] for p in scene.people}
    for model in list(physical.find('world')):
        if (model.tag != 'model' or model.get('name') in people_names
                or not model.get('name', '').startswith(('chair_', 'tv_', 'bed_', 'water_'))):
            physical.find('world').remove(model)
    pixels, _ = rasterize(collision_shapes(physical), *PIXELS, *ORIGIN, RESOLUTION)
    (package/'map/social_dynamic.pgm').write_bytes(f'P5\n{PIXELS[0]} {PIXELS[1]}\n255\n'.encode()+pixels)
    original_yaml = (package/'map/social_static.yaml').read_text()
    (package/'map/social_dynamic.yaml').write_text(original_yaml.replace('social_static.pgm', 'social_dynamic.pgm'))
    bridge = (package/'config/gz_bridge/social_static_bridge.yaml').read_text()
    (package/'config/gz_bridge/social_dynamic_bridge.yaml').write_text(bridge.replace('social_static', 'social_dynamic'))
    manifest.update(world='social_dynamic', motions=motions, people=scene.people,
                    obstacles=scene.obstacles, kinematic_humans=True,
                    articulated_walk_animation=False,
                    timeline=dict(watch_until=watch_end, stand_until=stand_end, drink_start=drink_start,
                                  drink_end=drink_end, return_to_chair=sit_start, cycle=cycle))
    # TV ground-truth bounds are illustrative, not a permanent keepout.
    manifest['zones'].extend([
        dict(name='sleeping', activity='lying_still_script', center=[-3.9, -.25],
             size=[2.4, 1.3], color=[.3, .6, .9]),
        dict(name='patrol', activity='walking_patrol_script', center=[0., 0.],
             size=[0., 0.], color=[.95, .5, .2])])
    next(z for z in manifest['zones'] if z['name'] == 'tv_group')['size'] = [0., 0.]
    (package/'config/social_dynamic_scene.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Generated dynamic scene; TV cycle {cycle:.1f} sim s, patrol {patrol_end:.1f} sim s')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--watch-seconds', type=float, default=12.)
    parser.add_argument('--walk-speed', type=float, default=.35)
    parser.add_argument('--patrol-speed', type=float, default=.4)
    options = parser.parse_args()
    generate(Path(__file__).resolve().parents[1], options.watch_seconds, options.walk_speed, options.patrol_speed)
