"""Local optical adjustment passes, no full-frame image allocations for small lenses."""
import math
import cv2
import numpy as np
from PIL import ImageColor

def rgb(c): return np.asarray(ImageColor.getrgb(c),np.float32)

def gradient(w,h,stops,angle=0):
    yy,xx=np.ogrid[:h,:w]; a=math.radians(angle); p=(xx/max(w-1,1)-.5)*math.cos(a)+(yy/max(h-1,1)-.5)*math.sin(a);p=p/max(abs(math.cos(a))+abs(math.sin(a)),1e-5)+.5
    t=np.asarray([s[0] for s in stops]); cs=np.array([rgb(s[1]) for s in stops]); out=np.stack([np.interp(p,t,cs[:,i]) for i in range(3)],axis=-1).astype(np.uint8);return np.dstack([out,np.full((h,w),255,np.uint8)])

def lens(im,cx,cy,w,h,*,strength=.16,dispersion=.015,radius=.23,opacity=1.,tint='#dbe6ff',shine=.65,light=.0):
    """Refract already-composited layers through rounded lens, analytic 2D approximation."""
    H,W=im.shape[:2]; x0=max(0,int(cx-w/2-2));x1=min(W,int(cx+w/2+3));y0=max(0,int(cy-h/2-2));y1=min(H,int(cy+h/2+3));
    if x1<=x0 or y1<=y0 or min(w,h)<3:return
    y,x=np.mgrid[y0:y1,x0:x1].astype(np.float32);u=(x-cx)/(w/2);v=(y-cy)/(h/2);r=max(.02,min(.95,radius));qx=np.abs(u)-1+r;qy=np.abs(v)-1+r;d=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-r
    aa=np.clip(.5-d*min(w,h)/4,0,1);edge=np.exp(-((d+.032)/.065)**2);bend=strength*(.45+.75*np.exp(-((d+.1)/.15)**2));mx=(cx+(x-cx)*(1-bend)).astype(np.float32);my=(cy+(y-cy)*(1-bend)).astype(np.float32)
    dst=cv2.remap(im,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101).astype(np.float32)
    if dispersion:
        for channel,sign in [(0,1),(2,-1)]:
            dst[:,:,channel]=cv2.remap(im[:,:,channel],(mx+(x-cx)*dispersion*sign).astype(np.float32),(my+(y-cy)*dispersion*sign).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    spec=(.2+.8*np.maximum(0,np.cos(np.arctan2(v,u)-light))**6)*edge*shine;dst=dst*.92+rgb(tint)*.08+spec[:,:,None]*120;mix=(aa*opacity)[:,:,None];roi=im[y0:y1,x0:x1];roi[:]=np.uint8(np.clip(roi*(1-mix)+dst*mix,0,255))

def directional(packed,dx,dy,samples=5):
    """Exposure of a translating premultiplied layer, cropped ROI. Rotation excluded."""
    if math.hypot(dx,dy)<.65:return packed
    h,w=packed.shape[:2];acc=np.zeros_like(packed,dtype=np.float32)
    for q in np.linspace(-.5,.5,samples):acc+=cv2.warpAffine(packed,np.float32([[1,0,dx*q],[0,1,dy*q]]),(w,h),flags=cv2.INTER_LINEAR)
    return np.uint8(np.clip(acc/samples,0,255))

def shaped_lens(im, transform, w, h, *, shape='roundrect', strength=.16, dispersion=.012, radius=.23, opacity=1., tint='#dbe6ff', shine=.65, light=0., frost=0., tint_mix=.08, feather=1.5):
    """Affine local optical pass; shapes share image-space refraction with rotated parent axes."""
    A=np.asarray(transform,dtype=np.float64); B=A[:2,:2]; center=A[:2,2]
    if min(w,h)<1 or abs(np.linalg.det(B))<1e-7 or opacity<=0:return
    H,W=im.shape[:2]; corners=np.array([[-w/2,-h/2],[w/2,-h/2],[w/2,h/2],[-w/2,h/2]])@B.T+center
    lo=np.maximum(0,np.floor(corners.min(0)-3-feather).astype(int));hi=np.minimum([W,H],np.ceil(corners.max(0)+3+feather).astype(int));x0,y0=lo;x1,y1=hi
    if x1<=x0 or y1<=y0:return
    yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32); inv=np.linalg.inv(B);X=xx-center[0];Y=yy-center[1];u=(inv[0,0]*X+inv[0,1]*Y)/(w/2);v=(inv[1,0]*X+inv[1,1]*Y)/(h/2)
    if shape=='ellipse':d=np.hypot(u,v)-1
    elif shape=='diamond':d=(np.abs(u)+np.abs(v)-1)/1.4142
    elif shape=='squircle':d=(np.abs(u)**4+np.abs(v)**4)**.25-1
    elif shape=='capsule':
        r=min(w,h)/2; xx0=u*w/2; yy0=v*h/2
        d=(np.hypot(np.maximum(np.abs(xx0)-max(0,w/2-r),0),np.maximum(np.abs(yy0)-max(0,h/2-r),0))-r)/r
    else:
        r=np.clip(radius,.02,1) if shape!='capsule' else 1.;qx=np.abs(u)-1+r;qy=np.abs(v)-1+r;d=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-r
    unit=max(1,min(np.linalg.norm(B[:,0])*w,np.linalg.norm(B[:,1])*h)/2);aa=np.clip(.5-d*unit/max(.6,feather),0,1);edge=np.exp(-((d+.034)/.067)**2);bend=strength*(.38+.8*np.exp(-((d+.095)/.17)**2));mx=(xx-X*bend).astype(np.float32);my=(yy-Y*bend).astype(np.float32)
    # Remap the already-composited image, not a pre-rendered glass texture.
    dst=cv2.remap(im,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101).astype(np.float32)
    if dispersion:
        for channel,sign in [(0,1),(2,-1)]:dst[:,:,channel]=cv2.remap(im[:,:,channel],(mx+X*dispersion*sign).astype(np.float32),(my+Y*dispersion*sign).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    if frost>.01:dst=cv2.GaussianBlur(dst,(0,0),frost)
    spec=(.18+.82*np.maximum(0,np.cos(np.arctan2(v,u)-light))**6)*edge*shine
    dst=dst*(1-tint_mix)+rgb(tint)*tint_mix+spec[:,:,None]*120;mix=(aa*np.clip(opacity,0,1))[:,:,None];roi=im[y0:y1,x0:x1];roi[:]=np.uint8(np.clip(roi*(1-mix)+dst*mix,0,255))
