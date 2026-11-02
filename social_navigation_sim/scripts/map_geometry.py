"""Shared SDF collision rasterization for the static and dynamic scenes."""

import math


def parse_pose(element):
    if element is None or not element.text:
        return 0.0, 0.0, 0.0
    values = [float(value) for value in element.text.split()]
    if len(values) not in (3, 6):
        raise ValueError(f'Expected an SDF pose with 3 or 6 values: {values}')
    x, y, yaw = values[0], values[1], values[-1]
    return x, y, yaw


def compose_pose(parent, child):
    px, py, pyaw = parent
    cx, cy, cyaw = child
    cosine = math.cos(pyaw)
    sine = math.sin(pyaw)
    return (
        px + cosine * cx - sine * cy,
        py + sine * cx + cosine * cy,
        pyaw + cyaw,
    )


def collision_shapes(world_root):
    shapes = []
    for model in world_root.findall('./world/model'):
        model_pose = parse_pose(model.find('pose'))
        for link in model.findall('link'):
            link_pose = compose_pose(model_pose, parse_pose(link.find('pose')))
            for collision in link.findall('collision'):
                collision_pose = compose_pose(
                    link_pose, parse_pose(collision.find('pose'))
                )
                geometry = collision.find('geometry')
                if geometry is None:
                    continue
                box = geometry.find('box/size')
                if box is not None:
                    sx, sy, _ = (float(value) for value in box.text.split())
                    shapes.append(('box', collision_pose, sx, sy))
                    continue
                cylinder = geometry.find('cylinder')
                if cylinder is not None:
                    radius = float(cylinder.findtext('radius'))
                    shapes.append(('circle', collision_pose, radius, radius))
    return shapes


def rasterize(shapes, width, height, origin_x, origin_y, resolution):
    pixels = bytearray([255]) * (width * height)
    occupied_count = 0

    for kind, (center_x, center_y, yaw), size_x, size_y in shapes:
        if kind == 'circle':
            radius = size_x
            extent_x = extent_y = radius
        else:
            half_x = size_x * 0.5
            half_y = size_y * 0.5
            extent_x = abs(math.cos(yaw)) * half_x + abs(math.sin(yaw)) * half_y
            extent_y = abs(math.sin(yaw)) * half_x + abs(math.cos(yaw)) * half_y

        min_x = max(0, math.floor((center_x - extent_x - origin_x) / resolution))
        max_x = min(width - 1, math.floor((center_x + extent_x - origin_x) / resolution))
        min_y = max(0, math.floor((center_y - extent_y - origin_y) / resolution))
        max_y = min(height - 1, math.floor((center_y + extent_y - origin_y) / resolution))
        cosine = math.cos(yaw)
        sine = math.sin(yaw)

        for grid_y in range(min_y, max_y + 1):
            world_y = origin_y + (grid_y + 0.5) * resolution
            for grid_x in range(min_x, max_x + 1):
                world_x = origin_x + (grid_x + 0.5) * resolution
                dx = world_x - center_x
                dy = world_y - center_y
                if kind == 'circle':
                    inside = dx * dx + dy * dy <= size_x * size_x
                else:
                    local_x = cosine * dx + sine * dy
                    local_y = -sine * dx + cosine * dy
                    inside = (
                        abs(local_x) <= size_x * 0.5
                        and abs(local_y) <= size_y * 0.5
                    )
                if inside:
                    image_y = height - 1 - grid_y
                    pixel_index = image_y * width + grid_x
                    if pixels[pixel_index] != 0:
                        occupied_count += 1
                        pixels[pixel_index] = 0

    return pixels, occupied_count
