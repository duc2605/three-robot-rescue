"""Retired prototype registry; remaining historical modules only. Production uses paper_models/catalog.py."""
from importlib import import_module

METHODS = {1: {'id': 1, 'backend': 'compare01', 'module': 'method_01_pure_pursuit_vo', 'slug': 'pure_pursuit_vo', 'control': 'Kinematic Velocity Control', 'trajectory': 'Pure Pursuit', 'formation': 'V-Formation + separation-bearing + VO-inspired safety', 'paper_number': 3}, 2: {'id': 2, 'backend': 'compare02', 'module': 'method_02_impedance', 'slug': 'impedance', 'control': 'Feedback Linearization + Impedance', 'trajectory': 'Reference Trajectory Tracking', 'formation': 'Leader-Follower separation-bearing + SFM interactions', 'paper_number': 4}, 5: {'id': 5, 'backend': 'compare05', 'module': 'method_05_deform', 'slug': 'deform', 'control': 'Constrained local velocity control', 'trajectory': 'Distributed MPC-inspired trajectory optimization', 'formation': 'Adaptive Consensus + APF + temporary leadership heuristic', 'paper_number': 7}}

def load_method(method_id):
    if method_id not in METHODS:
        raise ValueError('legacy method must be 1,2,5')
    info = METHODS[method_id]
    return import_module('.' + info['module'] + '.pipeline', __package__), info
