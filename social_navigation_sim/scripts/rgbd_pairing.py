"""Select a recent aligned RGB-D capture before spending CPU on inference."""


def stamp_ns(header):
    return header.stamp.sec*1_000_000_000+header.stamp.nanosec


def aligned(rgb, depth, info):
    return (info is not None and rgb.header.frame_id
            and rgb.header.frame_id == depth.header.frame_id == info.header.frame_id
            and rgb.width == depth.width == info.width
            and rgb.height == depth.height == info.height
            and info.k[0] > 0 and info.k[4] > 0
            and all(abs(v) < 1e-6 for v in info.d)
            and depth.encoding in ('32FC1', '16UC1'))


def newest_pair(rgbs, depths, info, now_ns, max_age=.75, tolerance=.06):
    """An unmatched newer RGB must not starve an older, complete capture."""
    for rgb in sorted(rgbs, key=lambda m: stamp_ns(m.header), reverse=True):
        if not -.1 <= (now_ns-stamp_ns(rgb.header))/1e9 <= max_age:
            continue
        choices = [d for d in depths if aligned(rgb, d, info)
                   and abs(stamp_ns(d.header)-stamp_ns(rgb.header))/1e9 <= tolerance]
        if choices:
            depth = min(choices, key=lambda d: abs(stamp_ns(d.header)-stamp_ns(rgb.header)))
            return rgb, depth
    return None
