"""Scene description for evaluation; never imported by navigation nodes."""
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET


def pose(element):
    values = [float(v) for v in element.text.split()] if element is not None and element.text else []
    return (values + [0.]*6)[:6]


def matrix(p):
    x,y,z,r,pitch,yaw=p
    cr,sr,cp,sp,cy,sy=math.cos(r),math.sin(r),math.cos(pitch),math.sin(pitch),math.cos(yaw),math.sin(yaw)
    return [[cy*cp,cy*sp*sr-sy*cr,cy*sp*cr+sy*sr,x],
            [sy*cp,sy*sp*sr+cy*cr,sy*sp*cr-cy*sr,y],[-sp,cp*sr,cp*cr,z],[0,0,0,1]]


def multiply(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def transform(m,p):
    return [sum(m[i][k]*p[k] for k in range(3))+m[i][3] for i in range(3)]


def hull(points):
    pts=sorted(set(tuple(p) for p in points))
    if len(pts)<3:return pts
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    result=[]
    for seq in [pts,pts[::-1]]:
        half=[]
        for p in seq:
            while len(half)>1 and cross(half[-2],half[-1],p)<=0:half.pop()
            half.append(p)
        result.extend(half[:-1])
    return result


def shapes(model):
    result=[]
    for link in model.findall('link'):
        for tag in ['collision','visual']:
            for item in link.findall(tag):
                geometry=item.find('geometry')
                if geometry is None:continue
                m=multiply(matrix(pose(link.find('pose'))),matrix(pose(item.find('pose'))))
                box=geometry.findtext('box/size');radius=geometry.findtext('cylinder/radius');length=geometry.findtext('cylinder/length')
                if box:
                    size=[float(v) for v in box.split()]
                    points=[transform(m,[a*size[0]/2,b*size[1]/2,c*size[2]/2]) for a in [-1,1] for b in [-1,1] for c in [-1,1]]
                elif radius and length:
                    radius,length=float(radius),float(length)
                    points=[transform(m,[radius*math.cos(i*math.pi/16),radius*math.sin(i*math.pi/16),c*length/2]) for i in range(32) for c in [-1,1]]
                else:continue
                result.append({'polygon':hull([p[:2] for p in points]),'z':[min(p[2] for p in points),max(p[2] for p in points)],'collision':tag=='collision'})
    return result


def make_scene(project,world='social_dynamic'):
    package=project/'social_navigation_sim'
    source=package/'worlds'/f'{world}.sdf'
    xml=ET.parse(source).getroot().find('world')
    authored=json.loads((package/'config'/f'{world}_scene.json').read_text())
    people={p['name'] for p in authored['people']}
    person_data={p['name']:p for p in authored['people']}
    objects={}
    for model in xml.findall('model'):
        name=model.get('name');human=name in people or name.removesuffix('_contact') in people
        objects[name]={'name':name,'kind':'human' if human else 'object','initial_pose':pose(model.find('pose')),
                       'shapes':shapes(model),'ignore_overlap':name=='ground_plane'}
    for actor in xml.findall('actor'):
        name=actor.get('name')
        proxy=name+'_contact'
        if proxy in objects:
            objects[proxy]['facing_source']=name
            objects[proxy]['facing_offset']=person_data.get(name,{}).get('yaw',pose(actor.find('pose'))[5])-pose(actor.find('pose'))[5]
        objects[name]={'name':name,'kind':'actor','initial_pose':pose(actor.find('pose')),'shapes':[],
                       'proxy':name+'_contact' if name+'_contact' in objects else None,'ignore_overlap':True}
    for name in ['robot1','robot2','robot3']:
        objects[name]={'name':name,'kind':'robot','radius':.15,'z':[0.,.20],
                       'geometry_source':'configured circular robot envelope; overlap estimate, not exact wheel contacts',
                       'initial_pose':None,'shapes':[]}
    return {'version':1,'world':xml.get('name'),'bounds':authored.get('bounds',[-6.5,-5.5,6.5,5.5]),
            'source':'SDF geometry + measured ECM poses; never used as perception/navigation input',
            'overlap_label':'GEOMETRY ESTIMATE - NOT PHYSICS CONTACT',
            'objects':objects,'limits':['Robot circle is a configured envelope, not full wheel/mesh geometry.',
              'Boxes/cylinders projected from SDF; cylinder polygons have 32 sides.',
              'Non-primitive meshes without collision geometry are markers only.',
              'Pose samples are 20Hz. New recordings contain per-step physics contacts aggregated into each frame; old frames may have none.']}
