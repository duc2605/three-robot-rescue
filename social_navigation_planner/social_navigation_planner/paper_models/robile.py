"""Paper7: Robile position-vector PID formation, ported from PyBullet to ROS.

See upstream_sources.py for exact source revision. Gains1/.1/.1 and integral
cap10 follow SimpleDistanceController; actual dt replaces hardcoded1/240s.
Outputs are world velocities, transformed to each robot body by the ROS node.
"""
import math
from .kinematic import clip, limit, wrap, v_targets


class RobileFormation:
    def __init__(self,leader):
        self.leader=leader
        self.integral=[[0.,0.] for _ in range(3)]
        self.previous=[None]*3
        self.status=['not_commanded']*3

    def targets(self,poses,waypoint):
        # First two V slots from the original four-follower configuration.
        return v_targets(poses,self.leader,waypoint,gap=1.,width=1.)

    def commands(self,poses,targets,velocities,obstacles,dt,grid):
        dt=max(.001,min(.2,dt));result=[]
        for i,(pose,target) in enumerate(zip(poses,targets)):
            error=[target[k]-pose[k] for k in range(2)]
            if i==self.leader:
                # Original demo commands fixed leader motion. Goal tracking
                # is experiment infrastructure added to make routes comparable.
                vx,vy=limit(*error,.2)
                heading=math.atan2(vy,vx) if math.hypot(vx,vy)>.02 else pose[2]
                w=clip(wrap(heading-pose[2]),-1.2,1.2)
            else:
                for k in range(2):
                    self.integral[i][k]=clip(self.integral[i][k]+error[k]*dt,-10.,10.)
                derivative=[0.,0.] if self.previous[i] is None else [(error[k]-self.previous[i][k])/dt for k in range(2)]
                command=[error[k]+.1*self.integral[i][k]+.1*derivative[k] for k in range(2)]
                vx,vy=limit(*command,.28)
                w=clip(wrap(poses[self.leader][2]-pose[2]),-1.2,1.2)
                self.previous[i]=error
            if math.hypot(*error)<.01:
                vx=vy=0.
            result.append((vx,vy,w))
        self.status=['robile_vector_pid_adapter']*3
        return result
