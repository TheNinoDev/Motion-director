"""Deterministic damped modal soft-body controls. No collision or FEM solver.
A volume-preserving squash mode, transverse bend and localized dent/wave.
Event time uses the caller's clock (seconds for composite, normalized time for mesh).
"""
import math
import numpy as np
PRESETS={'jelly':(3.2,0.32),'rubber':(4.8,0.58),'silicone':(2.6,0.78),'heavy':(1.8,0.68),'jelly_soft':(2.3,.22),'jelly_firm':(4.4,.42),'foam':(2.5,.85),'gel':(2.8,.16)}
MODES=('squash','bend','twist','dent','ripple')
def validate(config):
 if not isinstance(config,dict) or config.get('preset','jelly') not in PRESETS:raise ValueError('invalid softbody preset')
 f,d=PRESETS[config.get('preset','jelly')];f=config.get('frequency',f);d=config.get('damping',d)
 if not isinstance(f,(int,float)) or not .3<=f<=12 or not isinstance(d,(int,float)) or not .08<=d<=.98:raise ValueError('softbody frequency/damping')
 events=config.get('events',[])
 if not isinstance(events,list) or len(events)>64:raise ValueError('softbody events')
 for e in events:
  if not isinstance(e,dict) or e.get('mode','squash') not in MODES or not isinstance(e.get('time'),(int,float)) or not math.isfinite(e['time']) or e['time']<0 or not isinstance(e.get('strength'),(int,float)) or not -1<=e['strength']<=1:raise ValueError('softbody event')
 return config

def response(t,frequency,damping):
 if t<0:return 0.
 w=2*math.pi*frequency;wd=w*math.sqrt(1-damping*damping)
 return math.exp(-damping*w*t)*math.sin(wd*t)*w/wd

def sample(config,t):
 f,d=PRESETS[config.get('preset','jelly')];f=config.get('frequency',f);d=config.get('damping',d); out={m:0. for m in MODES}
 for e in config.get('events',[]):out[e.get('mode','squash')]+=e['strength']*response(t-e['time'],f,d)
 return {m:max(-1.,min(1.,v)) for m,v in out.items()}

def deform(vertices,config,t):
 """Independent vertices, same continuous deformation field, no random stepping."""
 q=sample(config,t);v=np.asarray(vertices,dtype=float).copy();center=(v.min(0)+v.max(0))/2;v-=center;extent=max(float(np.max(np.abs(v))),1e-8);v/=extent
 k=math.exp(-.48*q['squash']);v[:,1]*=k;v[:,[0,2]]/=math.sqrt(k)
 x,y,z=v.T.copy();a=.8*q['twist']*y;v[:,0]=x*np.cos(a)-z*np.sin(a)+.55*q['bend']*y*y;v[:,2]=x*np.sin(a)+z*np.cos(a)
 # Smooth local deformation in normalized object coordinates.
 r=np.exp(-4*((x-.25)**2+(y-.3)**2));v[:,2]-=.30*q['dent']*r
 v[:,2]+=.12*q['ripple']*np.sin(8*x+5*y)*np.exp(-.7*(x*x+y*y))
 return v*extent+center

def solid_layer(layer,t,value):
 """Map supported modal channels into physical SDF dimensions and warps."""
 q=sample(layer['softbody'],t);l=dict(layer)
 # The sphere SDF otherwise uses min(a,b,c), collapsing nonuniform squash into uniform shrink.
 if l.get('geometry')=='sphere':
  diameter=min(l['w'],l['h'],value(l.get('depth',min(l['w'],l['h'])*.65),t));l.update(geometry='ellipsoid',w=diameter,h=diameter,depth=diameter)
 k=math.exp(-.48*q['squash']);
 for key,mul in [('size_x',1/math.sqrt(k)),('size_y',k),('scale_z',1/math.sqrt(k))]:l[key]=max(.05,min(5,value(layer.get(key,1),t)*mul))
 for key,add,lo,hi in [('bend3d',.50*q['bend'],-.8,.8),('twist3d',.9*q['twist'],-2,2)]:l[key]=max(lo,min(hi,value(layer.get(key,0),t)+add))
 return l
