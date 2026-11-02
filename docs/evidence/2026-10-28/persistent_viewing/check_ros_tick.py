import sys,json,copy
from pathlib import Path
sys.path[:0]=['social_navigation_sim/scripts','social_navigation_sim/test']
import numpy as np
import rclpy
from nav_msgs.msg import OccupancyGrid
from social_costmap import SocialNavigation
from test_tv_attention import scene,confirm
class Capture:
 def __init__(self):self.messages=[]
 def publish(self,m):self.messages.append(copy.deepcopy(m))
rclpy.init();n=SocialNavigation()
for name in ['map_pub','mask_pub','marker_pub','status_pub','attention_debug_pub']:setattr(n,name,Capture())
clock=[1.7];n.now=lambda:clock[0];n.last_time=1.7
m=OccupancyGrid();m.header.frame_id='map';m.info.width=m.info.height=100;m.info.resolution=.1
m.info.origin.position.x=m.info.origin.position.y=-5.;m.info.origin.orientation.w=1.;m.data=[0]*10000
n.on_map(m);n.color_attention=scene(((-1.,0.),(1.,0.)));confirm(n.color_attention)
n.color_attention.people[0]['camera_id']=8;n.color_attention.people[1]['camera_id']=9
n.tick();initial=int(np.count_nonzero(n.previous_mask));assert len(n.zones)==2
clock[0]=200.;n.tick();retained=int(np.count_nonzero(n.previous_mask))
assert len(n.zones)==2 and retained==initial and retained>0
assert all(v['stamp']==1.7 for v in n.zones.values())
status=n.status_pub.messages[-1].data;assert 'viewing_recheck_required=2' in status
obs=dict(p=np.array([-.8,.4]),stamp=200.,since=199.,hits=5,velocity=np.array([0.,.35]))
n.color_attention.observe_people({8:obs},(),200.);n.tick()
assert len(n.zones)==1 and all(k[1]==1 for k in n.zones)
after=int(np.count_nonzero(n.previous_mask));assert 0<after<retained
clock[0]=201.;n.tick();assert len(n.zones)==1
# A map coordinate change discards old anchors, rather than moving them into
# a different map silently. Reset service and clock rewind also clear memory.
m=copy.deepcopy(m);m.info.origin.position.x=-6.;n.on_map(m);assert not n.zones and not n.color_attention.cached_regions
n.color_attention=scene();confirm(n.color_attention);n.tick();assert n.zones
clock[0]=0.;n.tick();assert not n.zones and not n.color_attention.cached_regions
result={'initial_zones':2,'zones_after_200s_without_camera':2,'initial_keepout_cells':initial,'keepout_cells_after_200s':retained,'zones_after_one_viewer_departed':1,'keepout_cells_after_departure':after,'capture_stamp_preserved':1.7,'status_after_occlusion':status,'map_geometry_reset_passed':True,'clock_reset_passed':True,'domain':94,'limits':'ROS node tick with synthetic measurements and empty physical map; no Gazebo or DNN replay'}
Path('docs/evidence/2026-10-28/persistent_viewing/ros_tick_smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result))
n.destroy_node();rclpy.shutdown()
