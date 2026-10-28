# Paper 2 — APF–MPC + enhanced APF formation, v1 adapted

Reference: Yang She, Chao Song, Zetian Sun, Bo Li. **Optimized Model Predictive
Control-Based Path Planning for Multiple Wheeled Mobile Robots in Uncertain
Environments**, Drones 2025, 9(1), 39.
DOI: https://doi.org/10.3390/drones9010039

**Independent, adapted implementation. Not author code or a validated exact
reproduction. No ROS/Gazebo runtime validation was performed in this environment.**

## Algorithm mapping

| Layer | Implemented method | Reference / difference |
|---|---|---|
| Leader planning/control | Receding-horizon SLSQP continuous optimization of a sequence of world XY velocities | Eq21 structure: reference tracking + input-increment penalty + predicted APF |
| Leader potential | Goal-distance attraction; goal-weighted inverse-distance obstacle repulsion with velocity-dependent Ds | Eq10–12 functional form; positive Ds floor and footprint clearance replace center-distance geometry |
| Follower references | Leader-frame offsets (-0.70 m, +/-0.50 m) | Algorithm 1 / virtual leader geometry |
| Follower control | Distance attraction, relative target-velocity attraction and desired-velocity attraction; position/closing-velocity repulsion | Sec3.2, Eq22–33 functional structure; gradients are computed numerically for vector directions |
| Additional safety | Swept grid/scan/camera-person/peer checks; speed scaling or stop | Engineering gate, not DWA or a second path planner |
| Camera | Existing RGB-D perception, head/body estimation, social inference and map | Existing project functionality, not a contribution of this paper |
| LiDAR | Existing per-robot scans plus height-filtered leader scan | Existing sensor pipeline |

The backend does **not** use GWO–WOA, DWA, D* Lite or the three old MPC
controllers. Existing TF/pose/markers are reused from the base coordinator.
Legacy RViz/topic names containing dstar/mpc remain for display compatibility.

## Important differences from the paper

1. The paper models four-wheel Mecanum robots. This adapter optimizes **world XY
   velocities**, maps them into the three-wheel omni body frame, and controls yaw
   separately. The world XY integrator is linear; the original four wheel-input
   Taylor/augmented model is not reproduced. It can use lateral omni motion.
2. Horizons are Np=16 and Nc=5, T=0.1 s, instead of the paper's Np=40, Nc=20.
   Speeds are scaled to this scene (leader 0.18 m/s, followers 0.22 m/s); weights,
   APF radii and gains are integration choices, not calibrated paper parameters.
3. Camera direction: leader turns toward desired world velocity before moving
   when the angle error exceeds 0.65 rad. Followers can move laterally/backward
   to maintain formation. This gate is additional to the paper.
4. Robot velocities are estimated from measured poses. Camera-person and LiDAR
   velocities are **unknown and modeled stationary over the short horizon**;
   they are never fabricated from array ordering. Dynamic obstacle prediction
   is implemented numerically but not supplied with identified moving-person
   tracks in this version. Do not claim full reproduction of the paper's
   moving-obstacle experiments.
5. The printed follower force equations contain scalar/vector and sign
   ambiguities. This implementation uses negative gradients of the stated
   potentials and explicit damping toward target velocity; force-to-acceleration
   scaling, clipping and safety braking are adapted. Eq12 angles use closing
   direction, Ds is clipped positive, and obstacle distances include footprints.
6. MPC uses bounded velocity norms and componentwise input increments. A solver
   result that is feasible but hits iteration limit is labeled SUBOPTIMAL.
   If the wall budget expires before a result, no unoptimized seed is executed.
   Every actual command passes an additional collision gate. This gate uses a
   conservative constant-command rollout plus braking tail, so it may stop even
   when a more complex safe maneuver exists. No guaranteed global convergence.
7. Nearby map/scan points are merged and capped at 100 for potential evaluation.
   The full occupancy grid remains in exact swept-circle checks. Unobserved
   moving people, data delay, slip and braking dynamics remain limitations.
8. No global graph fallback and no formation shape change. Local minima or
   narrow passages can still cause SAFETY_BRAKE/EMERGENCY_HOLD. No claim of
   better RTF, fewer collisions or better accuracy until measured on the same
   tests as paper1 and baseline.
9. Active camera turning / social search is disabled, while perception and
   social-map keepout remain enabled. Protected TV-viewing regions are not
   erased to force goal reaching. Poses still use Gazebo as in the base project.

## Install and build

The paper backend is integrated in this repository. Build directly; no patch installer is needed.

Stop the old simulation with Ctrl+C. Then:

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
sudo apt install -y python3-scipy
CMAKE_BUILD_PARALLEL_LEVEL=1 colcon build \
  --base-paths social_navigation_planner social_navigation_sim --symlink-install \
  --packages-select social_navigation_planner social_navigation_sim --executor sequential
source install/setup.bash
export ROS_DOMAIN_ID=31
export QT_QPA_PLATFORM=xcb
ros2 launch social_navigation_sim paper2_apf_mpc.launch.py
```

Only one simulation/launch should run at a time. In RViz use 2D Goal Pose.
Start with a nearby free goal in front of robot3, outside social keepout.

## Verify the active algorithm

```bash
source /opt/ros/humble/setup.bash
source ~/three-robot-rescue/install/setup.bash
export ROS_DOMAIN_ID=31
ros2 topic echo --once --full-length /paper2/status
```

Backend must be `PAPER2_V1_ADAPTED`. Status meanings:

- WAIT_MAP_OR_FRESH_POSES / WAIT_FRESH_LIDAR: missing/stale inputs, stop.
- GOAL_BLOCKED_IN_CURRENT_MAP: physical/social map blocks the goal, stop.
- MPC_NO_FEASIBLE_RESULT: optimizer returned no admissible result, stop.
- TRACKING: APF_MPC for leader, ENHANCED_APF for followers.
- LEADER_ALIGN_CAMERA: leader turning toward planned motion.
- SAFETY_BRAKE / EMERGENCY_HOLD: safety gate reduced/rejected the command.
- GOAL_REACHED: leader within 0.12 m and followers within 0.18 m of formation.

`formation_error_m` order is robot1, robot2, robot3. Leader entry is distance
to goal, not cross-track error; follower entries are distance to their virtual
targets. `solver.solve_ms` is measured wall computation time. Travel distance
comes from pose measurements; elapsed/reached time uses the simulation clock.
This is not a full statistical benchmark or a collision/RTF evaluation suite.

## Switch modes

Ctrl+C before switching:

```bash
# Paper 1
ros2 launch social_navigation_sim paper1_gwo_woa.launch.py
# Paper 2
ros2 launch social_navigation_sim paper2_apf_mpc.launch.py
# Original D* Lite/MPC baseline
ros2 launch social_navigation_sim social_navigation.launch.py navigation_backend:=baseline
```

Paper1 modules are not overwritten by this update. To remove paper2 source
changes entirely, use `install.py WORKSPACE --restore BACKUP_PATH` with the
backup printed during installation, then rebuild both packages. Restore refuses
files changed after install.

## Validation

13 numerical checks: APF at goal/obstacle/approaching obstacle, follower tracking
and acceleration bounds, continuous MPC optimization and control increments,
obstacle-disc avoidance, budget exhaustion, swept scan/peer collisions, braking
tail, virtual formation and receding-horizon goal reaching. Python syntax and
launch-mode expressions are checked. Installer/restore/hash checks are included
in packaging validation. These are offline checks, not Gazebo experiments.

```bash
cd ~/three-robot-rescue
PYTHONPATH=social_navigation_planner python3 -m unittest discover \
  -s social_navigation_planner/test -p test_paper2_apf_mpc.py -v
```
