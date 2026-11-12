"""Authored pedestrian road permissions for the outdoor experiment."""
import math


def walkable(x, y):
    sidewalk = abs(x) >= 6. and abs(y) >= 6.
    vertical = abs(abs(x)-8.) <= .75
    horizontal = abs(abs(y)-8.) <= .75
    return sidewalk or vertical or horizontal


def crossing(x, y):
    if abs(abs(x)-8.) <= .9 and abs(y) < 6.35:
        return ('vertical', 1 if x > 0 else -1)
    if abs(abs(y)-8.) <= .9 and abs(x) < 6.35:
        return ('horizontal', 1 if y > 0 else -1)
    return None


def enters_crossing(start, end):
    return bool(entry_axes(start,end))


def entry_axes(start, end):
    current=crossing(*start)
    count=max(1,math.ceil(math.dist(start,end)/.05))
    axes=set()
    for k in range(1,count+1):
        point=tuple(start[i]+(end[i]-start[i])*k/count for i in (0,1))
        target=crossing(*point)
        if target is not None and target!=current:
            axes.add(1 if target[0]=='vertical' else 0)
    return axes


def signal_allows_entry(signal, axis, now):
    try:
        age=now-float(signal['stamp'])
        green=signal['pedestrian_green_axes'];remaining=signal['pedestrian_remaining_axes']
        return (0 <= age <= .6 and len(green)==2 and len(remaining)==2
                and green[axis] is True and math.isfinite(float(remaining[axis]))
                and float(remaining[axis])>age+.5)
    except (KeyError,ValueError,TypeError,IndexError):
        return False
