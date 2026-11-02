"""Common SDF building primitives; authored scenario data stays in generators."""

import math
import xml.etree.ElementTree as ET

RESOLUTION = 0.05
ORIGIN = (-6.5, -5.5)
PIXELS = (260, 220)


def element(parent, tag, text=None, **attributes):
    child = ET.SubElement(parent, tag, attributes)
    if text is not None:
        child.text = str(text)
    return child


def values(numbers):
    return ' '.join(f'{v:.6f}' for v in numbers)


def pose(parent, xyz=(0, 0, 0), yaw=0):
    return element(parent, 'pose', values((*xyz, 0, 0, yaw)))


def material(visual, color, emissive=False):
    mat = element(visual, 'material')
    for tag in ('ambient', 'diffuse'):
        element(mat, tag, values(color))
    if emissive:
        element(mat, 'emissive', values(color))


class Scene:
    def __init__(self):
        self.root = ET.Element('sdf', version='1.8')
        self.world = element(self.root, 'world', name='social_static')
        self.people, self.obstacles = [], []

    def model(self, name, xyz, yaw=0):
        model = element(self.world, 'model', name=name)
        element(model, 'static', 'true')
        pose(model, xyz, yaw)
        return element(model, 'link', name='link')

    def box(self, name, x, y, sx, sy, height, color, yaw=0, base=0,
            collision=True, annotate=False, emissive=False):
        link = self.model(name, (x, y, base + height / 2), yaw)
        for tag in (('collision', 'visual') if collision else ('visual',)):
            part = element(link, tag, name=tag)
            geometry = element(part, 'geometry')
            element(element(geometry, 'box'), 'size', values((sx, sy, height)))
            if tag == 'visual':
                material(part, color, emissive)
        if annotate:
            self.obstacles.append(dict(name=name, xy=[x, y], height=height,
                                       size=[sx, sy], yaw=yaw))

    def cylinder(self, name, x, y, radius, height, color):
        link = self.model(name, (x, y, height / 2))
        for tag in ('collision', 'visual'):
            part = element(link, tag, name=tag)
            shape = element(element(part, 'geometry'), 'cylinder')
            element(shape, 'radius', radius)
            element(shape, 'length', height)
            if tag == 'visual':
                material(part, color)
        self.obstacles.append(dict(name=name, xy=[x, y], radius=radius, height=height))

    def person(self, name, x, y, facing, activity, group, posture='standing'):
        link = self.model(name, (x, y, 0), facing)
        # The original mesh faces -Y. Rotate it so model +X is the gaze
        # direction used in the manifest and the RViz orientation arrows.
        visual = element(link, 'visual', name='textured_person')
        pose(visual, (0, 0, 0.01), math.pi / 2)
        mesh = element(element(visual, 'geometry'), 'mesh')
        mesh_name = 'seated' if posture == 'seated' else 'standing'
        element(mesh, 'uri', f'model://person_standing/meshes/{mesh_name}.dae')
        element(mesh, 'scale', '0.92 0.92 0.92')
        collision = element(link, 'collision', name='body_envelope')
        if posture == 'seated':
            pose(collision, (0.18, 0, 0.70))
            shape = element(element(collision, 'geometry'), 'box')
            element(shape, 'size', '0.88 0.62 1.40')
        else:
            pose(collision, (0, 0, 0.89))
            cylinder = element(element(collision, 'geometry'), 'cylinder')
            element(cylinder, 'radius', '0.32')
            element(cylinder, 'length', '1.78')
        self.people.append(dict(name=name, x=x, y=y, yaw=facing,
                                activity=activity, group=group, radius=0.32,
                                posture=posture, height=1.40 if posture == 'seated' else 1.78))

    def core(self):
        physics = element(self.world, 'physics', name='1ms', type='ignored')
        element(physics, 'max_step_size', '0.001')
        element(physics, 'real_time_factor', '1.0')
        for system in ('Physics', 'UserCommands', 'SceneBroadcaster', 'Contact', 'Imu'):
            stem = {'UserCommands': 'user-commands', 'SceneBroadcaster': 'scene-broadcaster'}
            element(self.world, 'plugin', filename=f'ignition-gazebo-{stem.get(system, system.lower())}-system',
                    name=f'gz::sim::systems::{system}')
        sensors = element(self.world, 'plugin', filename='libgz-sim-sensors-system.so',
                          name='gz::sim::systems::Sensors')
        element(sensors, 'render_engine', 'ogre2')
        scene = element(self.world, 'scene')
        element(scene, 'ambient', '0.65 0.65 0.65 1')
        element(scene, 'background', '0.16 0.19 0.23 1')
        element(scene, 'shadows', 'true')
        sun = element(self.world, 'light', name='sun', type='directional')
        pose(sun, (0, 0, 12))
        element(sun, 'diffuse', '0.85 0.85 0.80 1')
        element(sun, 'specular', '0.12 0.12 0.12 1')
        element(sun, 'direction', '-0.25 0.15 -0.95')
        element(sun, 'cast_shadows', 'true')
        floor = self.model('ground_plane', (0, 0, 0))
        for tag in ('collision', 'visual'):
            part = element(floor, tag, name=tag)
            plane = element(element(part, 'geometry'), 'plane')
            element(plane, 'normal', '0 0 1')
            element(plane, 'size', '16 14')
            if tag == 'visual':
                material(part, (0.77, 0.79, 0.80, 1))
