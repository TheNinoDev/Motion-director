"""Frame-sampled LOCAL motion diagnostics; advisory, not pixel or aesthetic analysis."""
import json,argparse,math
from pathlib import Path
from motion_workbench import DEFAULTS
from compositor import val

def audit(plan,creative):
 fps=plan['fps'];by={l['id']:l for l in plan['layers']};out=[];issues=[]
 for i,b in enumerate(creative['beats']):
  a,z=b['start'],b['end'];stats=[]
  for k in b['layer_ids']:
   l=by[k];lo=max(a,l['active'][0]);hi=min(z,l['active'][1]);n=max(0,math.ceil(hi*fps-1e-9)-math.ceil(lo*fps-1e-9));ts=[j/fps for j in range(math.ceil(lo*fps-1e-9),math.ceil(hi*fps-1e-9))];pts=[];visible=0
   for t in ts:
    if val(l.get('opacity',1),t)>.05:
     visible+=1;pts.append((t,[val(l.get(q,DEFAULTS[q]),t) for q in ('x','y','scale','rotate','yaw','pitch','opacity')]))
   speeds=[];change=0
   for (t,p),(u,q) in zip(pts,pts[1:]):
    speeds.append((u,math.hypot(q[0]-p[0],q[1]-p[1])/(u-t)));change+=math.hypot(q[0]-p[0],q[1]-p[1])+abs(q[2]-p[2])*100+sum(abs(q[j]-p[j]) for j in (3,4,5))+abs(q[6]-p[6])*100
   peak=max((v for _,v in speeds),default=0);jump=max(((abs(y[1]-x[1]),y[0]) for x,y in zip(speeds,speeds[1:])),default=(0,None));stats.append({'layer':k,'active_frames':n,'opacity_visible_frames':visible,'local_motion_score':round(change,2),'peak_design_px_per_s':round(peak,1),'largest_speed_step':round(jump[0],1),'step_time':jump[1]})
   if jump[0]>700:issues.append({'beat':i,'layer':k,'time':jump[1],'message':'Inspect sharp local speed change; may be intentional.'})
  if not any(x['opacity_visible_frames'] for x in stats):issues.append({'beat':i,'message':'No linked layer with sampled opacity above .05.'})
  if not any(x['local_motion_score']>4 for x in stats):issues.append({'beat':i,'message':'Little tracked transform change. Inspect reveal, matte, material, parent motion or intentional hold.'})
  out.append({'beat':i,'start':a,'end':z,'layers':stats})
 return {'beats':out,'advice':issues,'limitations':'Local transforms and opacity only, does not account for crop, occlusion, parent motion, material, shader or actual screen visibility.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('creative',type=Path);a=p.parse_args();print(json.dumps(audit(json.loads(a.plan.read_text()),json.loads(a.creative.read_text())),indent=2))
