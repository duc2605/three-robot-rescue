"""Paper5 bridge to the actual pinned author HOMPCMultiRobot / HierarchicalQP.

No surrogate weighted optimizer. Author omni state has x,y only: yaw tracking
is an explicit outside-the-MPC integration choice. Three robots, four steps.
"""
import math
import os
from pathlib import Path
import subprocess
import sys

from .kinematic import clip, limit, wrap, v_targets
from .upstream_sources import SOURCES, QP_COMMIT


def activate_upstream():
    root=Path(os.environ.get('SOCIAL_HO_MPC_ROOT',str(Path.home()/'.cache/three-robot-rescue/paper5'))).expanduser()
    for directory,commit in ((root/'upstream',SOURCES[5]['commit']),(root/'hierarchical_qp',QP_COMMIT)):
        if not (directory/'.git').exists():
            raise RuntimeError('Paper5 upstream missing. Follow README_PAPER5_HO_MPC.md / scripts/prepare_ho_mpc.py before running.')
        actual=subprocess.check_output(['git','-C',str(directory),'rev-parse','HEAD'],text=True).strip()
        if actual!=commit:raise RuntimeError(f'Paper5 upstream revision mismatch: {directory}')
        subprocess.run(['git','-C',str(directory),'diff','--quiet','HEAD'],check=True)
    for path in (root/'upstream/src/hierarchical_optimization_mpc',root/'hierarchical_qp'):
        if str(path) not in sys.path:sys.path.insert(0,str(path))
    try:
        import casadi
        from hierarchical_optimization_mpc.ho_mpc_multi_robot import HOMPCMultiRobot
        from hierarchical_qp.hierarchical_qp import QPSolver
        from hierarchical_optimization_mpc.tasks_creator_ho_mpc_mr import TasksCreatorHOMPCMultiRobot
        from hierarchical_optimization_mpc.utils.robot_models import get_omnidirectional_model
    except ImportError as exc:
        raise RuntimeError('Paper5 optional dependencies missing; use the dedicated venv/PYTHONPATH commands in README_PAPER5_HO_MPC.md') from exc


class HierarchicalOmni:
    def __init__(self,leader):
        activate_upstream()
        import casadi as ca
        import numpy as np
        from hierarchical_optimization_mpc.ho_mpc_multi_robot import HOMPCMultiRobot, QPSolver, TaskType, TaskBiCoeff
        from hierarchical_optimization_mpc.tasks_creator_ho_mpc_mr import TasksCreatorHOMPCMultiRobot
        from hierarchical_optimization_mpc.utils.robot_models import get_unicycle_model,get_omnidirectional_model
        self.ca,self.np=ca,np
        self.Model,self.Type,self.Bi=HOMPCMultiRobot,TaskType,TaskBiCoeff
        self.Creator=TasksCreatorHOMPCMultiRobot;self.solver=QPSolver.quadprog
        self.models=[get_unicycle_model(.1),get_omnidirectional_model(.1)]
        self.leader=leader;self.last=[(0.,0.)]*3
        self.status=['not_solved']*3

    def commands(self,poses,targets,velocities,obstacles,dt,grid):
        ca,np=self.ca,self.np
        states,inputs,dynamics=map(list,zip(*self.models))
        model=self.Model(states,inputs,dynamics,[0,3],solver=self.solver,hierarchical=True)
        model.n_control=4;model.n_pred=0
        creator=self.Creator(states,inputs,dynamics,.1,[0,3])
        # Per-axis bounds guarantee ||v|| <= .28 without post-scaling a QP
        # result and thereby invalidating its collision inequalities.
        creator.v_max=.28/math.sqrt(2);creator.v_min=-creator.v_max
        model.create_task(name='limits',prio=1,type=self.Type.Same,
                          ineq_task_ls=creator.get_task_input_limits())
        aux=ca.SX.sym('pair_positions',2,2)
        squared=ca.sumsqr(aux[0,:]-aux[1,:])
        mapping=[states[0][:2],states[1][:2]]
        pair_coeff=[self.Bi(1,i,1,j,k,-.36**2) for i in range(3) for j in range(i+1,3) for k in range(4)]
        model.create_task_bi(name='peer_clearance',prio=2,type=self.Type.Bi,
            aux=aux,mapping=mapping,ineq_task_ls=-squared,ineq_task_coeff=pair_coeff)
        # Forecast observed LiDAR disks. Common final swept veto also checks
        # physical/social grids, which do not have a differentiable encoding.
        for i in range(3):
            for k in range(4):
                inequalities=[]
                for x,y,vx,vy,r in obstacles[i]:
                    predicted=ca.vertcat(x+vx*.1*(k+1),y+vy*.1*(k+1))
                    inequalities.append((r+.18)**2-ca.sumsqr(states[1]-predicted))
                if inequalities:
                    model.create_task(name=f'lidar_{i}_{k}',prio=2,type=self.Type.Same,
                        ineq_task_ls=[ca.SX.zeros(0,1),ca.vertcat(*inequalities)],
                        robot_index=[[],[i]],time_index=[k])
        target_arrays=[[],[np.array(p[:2]) for p in targets]]
        pos,coeff=creator.get_task_pos_ref(target_arrays,robot_idx=[[],[self.leader]])
        model.create_task(name='leader_waypoint',prio=3,type=self.Type.Same,
                          eq_task_ls=pos,eq_task_coeff=coeff,robot_index=[[],[self.leader]])
        # Preserve desired inter-robot distances, the author's formation task.
        slots=v_targets(poses,self.leader,poses[self.leader][:2])
        distances=[self.Bi(1,i,1,j,k,math.dist(slots[i],slots[j])**2)
                   for i in range(3) for j in range(i+1,3) for k in range(4)]
        model.create_task_bi(name='formation',prio=4,type=self.Type.Bi,
            aux=aux,mapping=mapping,eq_task_ls=squared,eq_task_coeff=distances)
        model.create_task(name='minimum_input',prio=5,type=self.Type.Same,eq_task_ls=creator.get_task_input_min())
        nominal=[[],[[np.array(limit(*velocities[i][:2],.28)) for _ in range(4)] for i in range(3)]]
        answer=model([[],[np.array(p[:2]) for p in poses]],inputs=nominal)[1]
        result=[]
        for i,velocity in enumerate(answer):
            vx,vy=map(float,velocity)
            if not all(math.isfinite(v) for v in (vx,vy)) or math.hypot(vx,vy)>.2801:
                raise ValueError('Paper5 returned invalid/out-of-bounds velocity')
            heading=math.atan2(vy,vx) if math.hypot(vx,vy)>.02 else poses[i][2]
            result.append((vx,vy,clip(wrap(heading-poses[i][2]),-1.2,1.2)))
        self.last=[r[:2] for r in result];self.status=['upstream_hierarchical_qp']*3
        return result
