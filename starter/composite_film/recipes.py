#!/usr/bin/env python3
"""General editable layer recipes. No fixed scene ordering or product claims."""
import math
import numpy as np
from PIL import ImageFont

def keys(*k):return [list(x) for x in k]
def staggered_line(prefix,text,span,center,y,font_path,size,*,start,step=.04,travel=.27,color='#ffffff',font='bold'):
 """Position once using full text advances. Spaces remain reserved. Latin lettering only;
 use whole-line masks for scripts requiring shaping. Kerning approximated by prefix advance."""
 f=ImageFont.truetype(font_path,size);n=len(text);full=f.getlength(text);out=[]
 for i,ch in enumerate(text):
  if ch.isspace():continue
  x=center-full/2+f.getlength(text[:i])+f.getlength(ch)/2;t=start+i*step
  out.append({'kind':'text','id':f'{prefix}{i}','active':[span[0],span[1]],'text':ch,'size':size,'font':font,'x':x,'y':keys((t,y+size*.47),(t+travel,y,'out')),'color':color,'opacity':keys((t,0),(t+travel*.65,1,'out')),'reveal':keys((t,0),(t+travel,1,'out'))})
 return out

def bezier(p0,p1,p2,p3,n=84):
 t=np.linspace(0,1,n)[:,None];p=(1-t)**3*np.array(p0)+3*(1-t)**2*t*np.array(p1)+3*(1-t)*t*t*np.array(p2)+t**3*np.array(p3);return p.tolist()
def resample(points,n=96):
 p=np.asarray(points,float);dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];
 if dist[-1]<=0:raise ValueError('path length zero')
 x=np.linspace(0,dist[-1],n);return np.column_stack([np.interp(x,dist,p[:,j]) for j in range(2)]).tolist()
def morph_path(id,span,paths,*,color='#ffffff',stroke=3):
 """Uniform arc-length samples; author equal start orientation/direction for closed shapes."""
 pts=[(t,resample(p)) for t,p in paths];return {'kind':'path','id':id,'active':list(span),'points':pts[0][1],'points_keyframes':pts,'w':720,'h':1280,'x':360,'y':640,'color':color,'stroke':stroke}
