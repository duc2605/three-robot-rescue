"""Source and implementation status, separate from historical prototype labels."""
PAPERS = {
    3: ('10.12962/jaree.v9i1.433', 'implemented_adaptation', 'V formation, Pure Pursuit, velocity obstacles'),
    4: ('10.1109/JAS.2017.7510631', 'implemented_adaptation', 'Outer impedance; omni velocity interface instead of identified Pioneer dynamics'),
    8: ('10.1109/LRA.2025.3552998', 'implemented_adaptation', 'DEFORM: width, assignment, reference consensus, constrained predictive control'),
    5: ('10.1109/LRA.2025.3559843', 'implemented_adaptation', 'Replacement: upstream Hierarchical Optimization MPC, three omni robots'),
    6: ('', 'implemented_adaptation', 'Replacement: Different Drivetrains project, Hybrid A* / Pure Pursuit / mecanum follower; localization adapted'),
    7: ('', 'implemented_adaptation', 'Replacement: Robile project, omni vector-PID formation ported from PyBullet'),
}


def require_paper(paper):
    info = PAPERS.get(paper)
    if info is None or info[1] != 'implemented_adaptation':
        raise ValueError(f'Paper{paper} disabled: {info[2] if info else "unknown paper"}. No legacy fallback.')
    return info


def require_runtime(paper):
    """Validate optional upstream before a wrapper starts Gazebo/recording."""
    info = require_paper(paper)
    if paper == 5:
        from .ho_mpc import activate_upstream
        activate_upstream()
    return info
