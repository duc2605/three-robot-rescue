"""Read-only replay serialization; these records are never navigation inputs."""
import base64
import math


def social_regions(markers):
    """Normalize this project's full-snapshot camera_social_regions markers."""
    labels={m['id']:m.get('text','') for m in markers
            if m.get('action',0)==0 and m.get('type')==9 and m.get('frame')=='map'}
    regions=[]
    for m in markers:
        if m.get('action',0)!=0 or m.get('type')!=4 or m.get('frame')!='map':continue
        points=m.get('points',[])
        if len(points)<3 or not all(len(p)==2 and all(math.isfinite(v) for v in p) for p in points):continue
        # The camera social publisher emits world-space LINE_STRIP coordinates.
        regions.append(dict(id=m['id'],points=points,label=labels.get(m['id']+1,'Vùng xã hội'),color=m.get('color',[1.,.6,.05,1.])))
    return regions


def encode_camera(row):
    """JPEG work runs on the perception writer thread, outside callbacks/control."""
    msg=row.pop('_image',None)
    if msg is None:return row
    try:
        import cv2
        from cv_bridge import CvBridge
        pixels=CvBridge().imgmsg_to_cv2(msg,'bgr8')
        if max(pixels.shape[:2])>640:
            factor=640/max(pixels.shape[:2]);pixels=cv2.resize(pixels,(round(pixels.shape[1]*factor),round(pixels.shape[0]*factor)))
        ok,jpeg=cv2.imencode('.jpg',pixels,[cv2.IMWRITE_JPEG_QUALITY,75])
        if not ok:raise ValueError('JPEG encode failed')
        row.update(image='data:image/jpeg;base64,'+base64.b64encode(jpeg).decode(),width=int(pixels.shape[1]),height=int(pixels.shape[0]))
    except Exception as error:
        row.update(kind='camera_error',error=str(error))
    return row
