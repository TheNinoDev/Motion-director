"""Extrude font outlines including interior holes. True 3D triangle geometry."""
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from shapely import constrained_delaunay_triangles
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

def glyph(char,font_path,depth=.22,bevel=.02):
    font=ImageFont.truetype(str(font_path),160);l,t,r,b=font.getbbox(char);h=max(b-t,1);w=r-l
    im=Image.new('L',(w+12,h+12));ImageDraw.Draw(im).text((6-l,6-t),char,font=font,fill=255)
    cs,tree=cv2.findContours((np.array(im)>127).astype('uint8'),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if tree is None:raise ValueError('Empty glyph '+char)
    def ring(c):
        a=cv2.approxPolyDP(c,.7,True).reshape(-1,2).astype(float);a[:,0]=(a[:,0]-6-w/2)/h;a[:,1]=-(a[:,1]-6-h/2)/h;return a
    out=[];beveled=0
    def tri(a,b,c,n):
        for p in (a,b,c):out.extend([*p,*n])
    def quad(a,b,c,d,n):tri(a,b,c,n);tri(a,c,d,n)
    def unit(v):return v/max(np.linalg.norm(v),1e-9)
    def inset(rr,amt):
        result=[]
        for i,p in enumerate(rr):
            e=unit(p-rr[i-1]);f=unit(rr[(i+1)%len(rr)]-p);n=np.array([-e[1],e[0]]);m=np.array([-f[1],f[0]]);v=unit(n+m);result.append(p+v*min(amt/max(.3,np.dot(v,n)),amt*2.5))
        return np.array(result)
    for i,c in enumerate(cs):
        if tree[0,i,3]!=-1 or len(c)<3:continue
        p=Polygon(ring(c),[ring(x) for j,x in enumerate(cs) if tree[0,j,3]==i and len(x)>=3])
        if not p.is_valid or p.area<.0001:raise ValueError('Invalid contour '+char)
        p=orient(p,sign=1);rings=[np.array(p.exterior.coords[:-1])]+[np.array(x.coords[:-1]) for x in p.interiors];amt=min(bevel,depth*.45);ri=[inset(x,amt) for x in rings];pin=Polygon(ri[0],ri[1:])
        if not pin.is_valid or pin.area<=0 or not p.buffer(1e-6).covers(pin):amt=0;ri=rings;pin=p
        if amt:beveled+=1
        z=depth/2;mid=z-amt
        for tt in constrained_delaunay_triangles(pin).geoms:
            a,b,c=list(tt.exterior.coords)[:3];tri((*a,z),(*b,z),(*c,z),(0,0,1));tri((*c,-z),(*b,-z),(*a,-z),(0,0,-1))
        for rr,ii in zip(rings,ri):
            for j,a in enumerate(rr):
                k=(j+1)%len(rr);b=rr[k];A=ii[j];B=ii[k];e=unit(b-a);n=np.array([e[1],-e[0],0]);quad((*a,-mid),(*b,-mid),(*b,mid),(*a,mid),n)
                if amt:quad((*a,mid),(*b,mid),(*B,z),(*A,z),unit(n+np.array([0,0,1])));quad((*A,-z),(*B,-z),(*b,-mid),(*a,-mid),unit(n+np.array([0,0,-1])))
    if not out:raise ValueError('No geometry '+char)
    return {'vertices':np.round(out,6).tolist(),'beveled_components':beveled,'triangles':len(out)//18}
