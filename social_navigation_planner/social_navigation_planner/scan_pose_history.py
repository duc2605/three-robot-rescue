"""Robot localization poses at LiDAR capture time; no obstacle ground truth."""
from collections import deque
import math


class ScanPoseHistory:
    def __init__(self,count=3):
        self.samples=[deque(maxlen=96) for _ in range(count)]

    def clear(self):
        for history in self.samples:history.clear()

    def add(self,index,stamp,pose):
        history=self.samples[index]
        if history and stamp<history[-1][0]-1e-9:return False
        if history and abs(stamp-history[-1][0])<1e-9:history.pop()
        history.append((stamp,tuple(pose[:3])))
        return True

    def at(self,index,stamp):
        history=self.samples[index]
        if not history or stamp<history[0][0]-1e-6:return None
        if abs(stamp-history[0][0])<1e-6:return history[0][1]
        for (a,p),(b,q) in zip(history,list(history)[1:]):
            if a<=stamp<=b:
                return self.interpolate(p,q,(stamp-a)/max(b-a,1e-9))
        last,p=history[-1]
        if abs(stamp-last)<1e-6:return p
        if stamp-last>.05 or len(history)<2:return None
        previous,q=history[-2]
        # Short extrapolation covers a scan arriving just before the next
        # pose packet; never extrapolate across a dropped pose stream.
        return self.interpolate(q,p,(stamp-previous)/max(last-previous,1e-9))

    def velocity(self,index,stamp):
        history=[(t,p) for t,p in self.samples[index] if 0 <= stamp-t <= .4]
        if len(history)<2:return (0.,0.,0.)
        t,p=history[-1]
        if stamp-t>.3:return (0.,0.,0.)
        first=next(((a,q) for a,q in history if .15<=t-a<=.35),history[0])
        a,q=first;dt=t-a
        if dt<.04:return (0.,0.,0.)
        vx,vy=(p[0]-q[0])/dt,(p[1]-q[1])/dt
        w=math.atan2(math.sin(p[2]-q[2]),math.cos(p[2]-q[2]))/dt
        if math.hypot(vx,vy)>1.5:return (0.,0.,0.)
        return vx,vy,max(-3.,min(3.,w))

    @staticmethod
    def interpolate(p,q,fraction):
        delta=math.atan2(math.sin(q[2]-p[2]),math.cos(q[2]-p[2]))
        yaw=p[2]+fraction*delta
        return (p[0]+fraction*(q[0]-p[0]),p[1]+fraction*(q[1]-p[1]),
                math.atan2(math.sin(yaw),math.cos(yaw)))
