#!/usr/bin/env python3
"""Generate the additional outdoor world/map, never modify indoor scene assets."""
import json
import math
from pathlib import Path
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]
WORLD='street_intersection'


def sub(parent,tag,text=None,**attrs):
    node=E.SubElement(parent,tag,attrs)
    if text is not None:node.text=str(text)
    return node


def pose(node,values):sub(node,'pose',' '.join(map(str,values)))


def shape(link,name,kind,size,xyz=(0,0,0),color=(.5,.5,.5,1),collision=False,rpy=(0,0,0),glow=False):
    v=sub(link,'visual',name=name);pose(v,(*xyz,*rpy));g=sub(v,'geometry');geo=sub(g,kind)
    if kind=='box':sub(geo,'size',' '.join(map(str,size)))
    elif kind=='sphere':sub(geo,'radius',size[0])
    else:sub(geo,'radius',size[0]);sub(geo,'length',size[1])
    m=sub(v,'material')
    for t in ('ambient','diffuse'):sub(m,t,' '.join(map(str,color)))
    if glow:sub(m,'emissive',' '.join(map(str,color)))
    if collision:
        c=sub(link,'collision',name=name+'_collision');pose(c,(*xyz,*rpy))
        c.append(E.fromstring(E.tostring(g)))


def model(world,name,xy=(0,0),yaw=0):
    m=sub(world,'model',name=name);sub(m,'static','true');pose(m,(*xy,0,0,0,yaw))
    return m,sub(m,'link',name='body')


def make_route(turn):
    # Eastbound approach. Right-hand traffic, lane centre y=-1.65.
    pts=[(-36.,-2.5),(-10.,-2.5),(-5.,-2.5)]
    if turn=='straight':return pts+[(36.,-2.5)]
    end=(2.5,6.) if turn=='left' else (-2.5,-6.)
    c1=(-.5,-2.5) if turn=='left' else (-2.5,-2.5)
    c2=(2.5,1.) if turn=='left' else (-2.5,-4.)
    start=pts[-1]
    for i in range(1,25):
        t=i/24;u=1-t
        pts.append(tuple(u**3*start[j]+3*u*u*t*c1[j]+3*u*t*t*c2[j]+t**3*end[j] for j in (0,1)))
    pts.append((end[0],36. if turn=='left' else -36.))
    return pts


def generate():
    sdf=E.Element('sdf',version='1.8');w=sub(sdf,'world',name=WORLD)
    ph=sub(w,'physics',name='street_physics',type='ignored');sub(ph,'max_step_size',.002);sub(ph,'real_time_factor',1.)
    base=E.parse(ROOT/'worlds/social_dynamic.sdf').getroot().find('world')
    for plugin in base.findall('plugin'):
        if plugin.get('name') in ('rescue::SocialScenarioMotion',):continue
        w.append(E.fromstring(E.tostring(plugin)))
    scene=sub(w,'scene');sub(scene,'ambient','.7 .7 .7 1');sub(scene,'background','.65 .8 .95 1');sub(scene,'shadows','true')
    light=sub(w,'light',name='sun',type='directional');pose(light,(0,0,20,0,0,0));sub(light,'diffuse','.9 .9 .85 1');sub(light,'direction','-.3 .2 -.9')
    m,l=model(w,'ground_plane');shape(l,'ground','box',(84,84,.1),(0,0,-.05),(.32,.48,.28,1),True)
    for name,sz in [('road_ew',(76,12,.015)),('road_ns',(12,76,.018))]:
        m,l=model(w,name);shape(l,'asphalt','box',sz,(0,0,.01),(.12,.13,.15,1))
    fixed=[]
    # Paved sidewalks flush at marked crossings; buildings are in static map.
    for sx in (-1,1):
        for sy in (-1,1):
            m,l=model(w,f'sidewalk_{sx}_{sy}',(sx*23.,sy*23.))
            shape(l,'paving','box',(34.,34.,.02),(0,0,.005),(.66,.66,.62,1))
            bx,by=sx*25.,sy*25.
            m,l=model(w,f'building_{sx}_{sy}',(bx,by))
            shape(l,'building','box',(24,24,5),(0,0,2.5),(.48,.56,.61,1),True)
            fixed.append([bx,by,24.,24.])
            for dz in (1.2,2.8,4.2):
                for dx in (-5,-2,1,4):shape(l,f'window_{dz}_{dx}','box',(1.1,.03,.65),(dx,-sy*12.02,dz),(.12,.3,.4,1))
    for axis in range(2):
        for i in range(-35,36,3):
            if abs(i)<10:continue
            xy=(i,0) if axis==0 else (0,i)
            m,l=model(w,f'lane_mark_{axis}_{i}',xy,axis*math.pi/2)
            shape(l,'dash','box',(1.5,.09,.015),(0,0,.032),(.95,.83,.25,1))
    for arm in range(4):
        a=arm*math.pi/2;c,s=math.cos(a),math.sin(a)
        for i in range(-6,7):
            x,y=-8.,i*.85
            m,l=model(w,f'crosswalk_{arm}_{i}',(c*x-s*y,s*x+c*y),a)
            shape(l,'stripe','box',(1.5,.4,.015),(0,0,.035),(.95,.95,.92,1))
        x,y=-10.,-3.
        m,l=model(w,f'stopline_{arm}',(c*x-s*y,s*x+c*y),a)
        shape(l,'line','box',(.14,6.,.015),(0,0,.036),(.95,.95,.92,1))
    plugin=sub(w,'plugin',filename='libstreet_traffic.so',name='rescue::StreetTraffic')
    vehicles=[]
    for arm in range(4):
        a=arm*math.pi/2;c,s=math.cos(a),math.sin(a)
        for i,turn in enumerate(('straight','left','right')):
            name=f'car_{arm}_{turn}';route=[(c*x-s*y,s*x+c*y) for x,y in make_route(turn)]
            # Three cars share the approach lane, queue spaced 5m.
            initial=18.-5*i
            x,y=route[0];x+=c*initial;y+=s*initial
            m,l=model(w,name,(x,y),a)
            color=[(.1,.35,.9,1),(.85,.2,.12,1),(.9,.7,.12,1)][i]
            shape(l,'chassis','box',(2.6,1.3,.65),(0,0,.55),color,True)
            shape(l,'cabin','box',(1.25,1.15,.55),(-.12,0,1.1),(.18,.3,.38,1),True)
            for xx in (-.85,.85):
                for yy in (-.68,.68):shape(l,f'wheel_{xx}_{yy}','cylinder',(.28,.15),(xx,yy,.3),(.04,.04,.04,1),False,(math.pi/2,0,0))
            for yy in (-.4,.4):shape(l,f'headlight_{yy}','box',(.035,.25,.12),(1.31,yy,.7),(.95,.95,.7,1))
            e=sub(plugin,'vehicle');sub(e,'name',name);sub(e,'approach',arm);sub(e,'initial_s',initial)
            stop_s=26.-1.33-.07-.15
            sub(e,'stop_s',stop_s);sub(e,'speed',2.2)
            for px,py in route:sub(e,'point',f'{px} {py}')
            vehicles.append(dict(name=name,turn=turn,approach=arm,speed=2.2,route=route,
                                 stop_s=stop_s,stop_line_s=26.,front_extent=1.33,stop_gap=.15))
    people=[]
    # Same north crossing: runner catches a slower walker; can choose either side.
    agents=[('walker_north',(-9.2,8.),(9.2,8.),.80,.27,'walker'),
            ('runner_north',(-11.2,8.),(11.2,8.),1.65,.27,'runner'),
            ('cane_walker',(-9.2,-8.),(9.2,-8.),.48,.35,'cane'),
            ('walker_south',(9.2,-8.),(-9.2,-8.),.85,.27,'walker'),
            ('walker_east',(8.,-9.2),(8.,9.2),.9,.27,'walker'),
            ('walk_then_run',(8.85,-10.2),(8.85,10.2),.8,.27,'walk_to_run'),
            ('runner_west',(-8.,-11.2),(-8.,11.2),1.5,.27,'runner'),
            ('dog',(-9.2,-9.2),(9.2,-9.2),1.05,.28,'dog')]
    colors={'walker':(.15,.65,.45,1),'runner':(.9,.3,.15,1),'cane':(.5,.2,.65,1),'dog':(.55,.34,.17,1),'walk_to_run':(.1,.65,.9,1)}
    for idx,(name,start,end,speed,radius,kind) in enumerate(agents):
        yaw=math.atan2(end[1]-start[1],end[0]-start[0]);m,l=model(w,name,start,yaw)
        if kind=='dog':
            shape(l,'body','box',(.7,.3,.3),(0,0,.42),colors[kind],True)
            shape(l,'head','sphere',(.17,),(.4,0,.55),colors[kind],True)
            for side in (-1,1):
                shape(l,f'ear_{side}','box',(.10,.06,.20),(.38,side*.12,.72),(.25,.16,.09,1))
            shape(l,'tail','cylinder',(.035,.40),(-.45,0,.54),colors[kind],False,(0,-.8,0))
        else:
            shape(l,'torso','cylinder',(.19,.65),(0,0,1.12),colors[kind])
            shape(l,'head','sphere',(.14,),(0,0,1.62),(.8,.62,.45,1))
            shape(l,'person_body','cylinder',(radius,1.7),(0,0,.86),colors[kind],True)
            # Collision visual transparent; body/limbs above remain colored.
            l.findall('visual')[-1].find('material/ambient').text='0 0 0 0'
            l.findall('visual')[-1].find('material/diffuse').text='0 0 0 0'
            sub(l.findall('visual')[-1],'transparency','1')
            if kind=='cane':
                shape(l,'walking_cane','cylinder',(.024,1.),(.24,-.37,.52),(.3,.22,.1,1),True,(0,.18,0))
        e=sub(plugin,'agent');sub(e,'name',name);sub(e,'start',f'{start[0]} {start[1]}');sub(e,'end',f'{end[0]} {end[1]}')
        sub(e,'speed',speed);sub(e,'radius',radius);sub(e,'kind',kind)
        if kind=='walk_to_run':sub(e,'run_after_distance',2.4);sub(e,'running_speed',1.6)
        for limb in range(4):
            lm,ll=model(w,f'{name}_limb_{limb}',start,yaw)
            shape(ll,'limb','cylinder',(.045,.35 if kind=='dog' else .6),(0,0,0),colors[kind] if limb>=2 else (.12,.16,.22,1))
        people.append(dict(name=name,x=start[0],y=start[1],yaw=yaw,radius=radius,
                           height=.75 if kind=='dog' else 1.75,activity=kind,posture='walking',kind=kind))
    # Local -X is the front of every head, facing the approaching traffic.
    bulbs=[('red',(1,.03,.03,1)),('yellow',(1,.8,.01,1)),('green',(.01,1,.08,1))]
    for arm in range(4):
        a=arm*math.pi/2;c,s=math.cos(a),math.sin(a)
        x,y=c*9.8-s*-6.5,s*9.8+c*-6.5
        m,l=model(w,f'traffic_pole_{arm}',(x,y),a)
        shape(l,'pole','cylinder',(.07,3.5),(.07,0,1.75),(.17,.17,.17,1),True)
        shape(l,'housing','box',(.28,.36,1.05),(0,0,3),(.04,.04,.04,1))
        for idx,(color,rgba) in enumerate(bulbs):
            z=3.3-.3*idx
            shape(l,'bezel_'+color,'cylinder',(.135,.04),(-.145,0,z),(.015,.015,.015,1),rpy=(0,math.pi/2,0))
            initial_on=(arm%2==0 and color=='green') or (arm%2==1 and color=='red')
            m,ll=model(w,f'signal_{arm}_{color}',(x,y),a)
            m.find('pose').text=' '.join(map(str,(x,y,z if initial_on else -10.,0,0,a)))
            shape(ll,'bulb','cylinder',(.11,.035),(-.17,0,0),rgba,rpy=(0,math.pi/2,0),glow=True)
        e=sub(plugin,'signal');sub(e,'approach',arm);sub(e,'xy',f'{x} {y}');sub(e,'yaw',a)
        fixed.append([x,y,.28,.36])
    # One far-side head per direction of each crossing, all supported on kerb poles.
    pedestrian_heads=[(-9.8,8.9,math.pi),(9.8,8.9,0.),
                      (-9.8,-8.9,math.pi),(9.8,-8.9,0.),
                      (8.9,-9.8,-math.pi/2),(8.9,9.8,math.pi/2),
                      (-8.9,-9.8,-math.pi/2),(-8.9,9.8,math.pi/2)]
    for index,(x,y,a) in enumerate(pedestrian_heads):
        m,l=model(w,f'pedestrian_pole_{index}',(x,y),a)
        shape(l,'pole','cylinder',(.055,2.7),(.07,0,1.35),(.16,.16,.16,1),True)
        shape(l,'housing','box',(.20,.40,.90),(0,0,2.2),(.035,.035,.035,1))
        for label,z,rgba in [('wait',2.43,(1,.03,.03,1)),('walk',2.0,(.01,1,.08,1))]:
            shape(l,label+'_background','box',(.025,.34,.36),(-.11,0,z),(.015,.015,.015,1))
            m,ll=model(w,f'pedestrian_{index}_{label}',(x,y),a)
            m.find('pose').text=' '.join(map(str,(x,y,z if ((index<4 and label=='walk') or (index>=4 and label=='wait')) else -10.,0,0,a)))
            shape(ll,'head','sphere',(.035,),(-.14,0,.12),rgba,glow=True)
            segments=[((0,.07),(0,-.035))]
            if label=='walk':
                segments += [((0,.04),(-.09,-.015)),((0,.04),(.08,.085)),
                             ((0,-.035),(-.085,-.14)),((0,-.035),(.09,-.10))]
            else:
                segments += [((0,.04),(-.065,-.035)),((0,.04),(.065,-.035)),
                             ((0,-.035),(-.035,-.14)),((0,-.035),(.035,-.14))]
            for limb,(start,end) in enumerate(segments):
                dy,dz=end[0]-start[0],end[1]-start[1]
                shape(ll,f'icon_{limb}','cylinder',(.013,math.hypot(dy,dz)),
                      (-.14,(start[0]+end[0])/2,(start[1]+end[1])/2),rgba,
                      rpy=(-math.atan2(dy,dz),0,0),glow=True)
        e=sub(plugin,'pedestrian_signal');sub(e,'xy',f'{x} {y}');sub(e,'yaw',a);sub(e,'axis',0 if index<4 else 1)
        fixed.append([x,y,.20,.40])
    sub(plugin,'status_period',.2)
    E.indent(sdf);(ROOT/'worlds'/f'{WORLD}.sdf').write_bytes(E.tostring(sdf,encoding='utf-8',xml_declaration=True))
    scene=dict(world=WORLD,frame_id='map',bounds=[-40,-40,40,40],people=people,
        annotation_source='authored_traffic_scenario_not_perception',map_contains_people=False,
        map_contains_social_zones=False,vehicles=vehicles,static_boxes=fixed,
        signals={'cycle_seconds':128,'approach_slot_seconds':20,'vehicle_approach_pairs':[[0,2],[1,3]],'left_turn_yields_to_oncoming':True,'green':14,'yellow':3,'all_red':3,
                 'exclusive_pedestrian_start':80,'exclusive_pedestrian_end':128,'clearance_interlock':True,
                 'vehicle_heads':4,'pedestrian_heads':8,'front_axis':'local_negative_x','parallel_pedestrian_green':True,'pedestrian_axis_by_vehicle_approach':[0,1,0,1],
                 'turns_yield_to_pedestrians':True,'vehicle_stop_gap':.15},
        limitations=['Procedural low-detail human/animal models; not photorealistic.',
                     'Kinematic traffic collision bodies, not vehicle dynamics or full biomechanics.',
                     'Traffic light schedule is scenario truth; robot controller has no traffic-law policy.'])
    (ROOT/'config'/f'{WORLD}_scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
    # 80x80m, 10cm grid, only fixed objects. Roads/crosswalks remain traversable.
    n=800;res=.1;pixels=bytearray([254])*(n*n)
    for row in range(n):
        y=40-(row+.5)*res
        for col in range(n):
            x=-40+(col+.5)*res
            if row in (0,n-1) or col in (0,n-1) or any(abs(x-bx)<=sx/2 and abs(y-by)<=sy/2 for bx,by,sx,sy in fixed):pixels[row*n+col]=0
    (ROOT/'map'/f'{WORLD}.pgm').write_bytes(f'P5\n{n} {n}\n255\n'.encode()+pixels)
    from street_rules import walkable
    pedestrian=bytearray(pixels)
    for row in range(n):
        y=40-(row+.5)*res
        for col in range(n):
            x=-40+(col+.5)*res
            if not walkable(x,y):pedestrian[row*n+col]=0
    (ROOT/'map/street_pedestrian.pgm').write_bytes(f'P5\n{n} {n}\n255\n'.encode()+pedestrian)
    (ROOT/'map/street_pedestrian.yaml').write_text(
        'image: street_pedestrian.pgm\nmode: trinary\nresolution: 0.1\norigin: [-40.0, -40.0, 0.0]\n'
        'negate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n')
    (ROOT/'map'/f'{WORLD}.yaml').write_text(f'image: {WORLD}.pgm\nmode: trinary\nresolution: 0.1\norigin: [-40.0, -40.0, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n')
    (ROOT/'config/gz_bridge'/f'{WORLD}_bridge.yaml').write_text((ROOT/'config/gz_bridge/social_dynamic_bridge.yaml').read_text().replace('social_dynamic',WORLD))
    with (ROOT/'config/gz_bridge'/f'{WORLD}_bridge.yaml').open('a') as bridge:
        bridge.write('\n- ros_topic_name: /street/traffic_state\n  gz_topic_name: /street/traffic_state\n'
                     '  ros_type_name: std_msgs/msg/String\n  gz_type_name: ignition.msgs.StringMsg\n  direction: GZ_TO_ROS\n')
    print('Generated only street_intersection world/map/scene/bridge')


if __name__=='__main__':generate()
