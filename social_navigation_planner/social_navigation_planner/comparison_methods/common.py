"""Shared math for the three explicit algorithms of THIS experiment.

These are research comparisons, not the authors' released implementations.
No proven stability or physical collision avoidance guarantees.
"""
from __future__ import annotations
import math
from dataclasses import dataclass


def bound(v, lo, hi): return max(lo, min(hi, v))
def limit(vx, vy, maximum):
    mag = math.hypot(vx, vy)
    if mag > maximum and mag > 1e-12: return vx*maximum/mag, vy*maximum/mag
    return vx, vy

def angle_diff(a, b): return (a - b + math.pi) % (2*math.pi) - math.pi

def ref_at(refs, k, i): return refs[min(max(k, 0), len(refs)-1)][i]

@dataclass
class Memory:
    last_vx: float = 0.0
    last_vy: float = 0.0
    last_w: float = 0.0
    ex_int: float = 0.0
    ey_int: float = 0.0
    prev_ex: float = 0.0
    prev_ey: float = 0.0
    leader_vx: float = 0.0
    leader_vy: float = 0.0
    last_leader: tuple | None = None
    last_pose: tuple | None = None
    slip_ratio: float = 0.0
    disturbance_x: float = 0.0
    disturbance_y: float = 0.0
