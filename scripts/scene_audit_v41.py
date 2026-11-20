#!/usr/bin/env python3
"""Parent-aware frame sampling plus conservative explicit repair proposals."""
import argparse,copy,json,math
from pathlib import Path
from agent_session import sha,write
from compositor import val,validate
import numpy as np

# Mirrors the renderer's affine state, including active ancestor gates.
def world(l,by,t):
 def g(k,d):return val(l.get(k,d),t)
 x,y=g('x',360),g('y',640);r=math.radians(g('rotate',0));sx=g('scale',1)*g('scale_x',1);sy=g('scale',1)*g('scale_y',1)
 M=np.array([[math.cos(r)*sx,-math.sin(r)*sy,x],[math.sin(r)*sx,math.cos(r)*sy,y],[0,0,1]])
 op=max(0,min(1,g('opacity',1))) if l['active'][0]<=t<l['active'][1] else 0
 if l.get('parent'):
  P,a=world(by[l['parent']],by,t);M=P@M;op*=a
 return M,op

def audit(p):
 by={l['id']:l for l in p['layers']};fps=p['fps'];out=[];proposals={}
 for l in p['layers']:
  if l['kind']=='group':continue
  a,b=l['active'];stats={'layer':l['id'],'sampled_frames':0,'parent_hidden_frames':0,'effective_visible_frames':0,'offscreen_bounds_frames':0,'first_problem_s':None};parent=l.get('parent')
  # Direct and transitive interval mismatch. Expansion is intentionally opt-in.
  while parent:
   q=by[parent];lo,hi=q['active']
   if a<lo or b>hi:
    item=proposals.setdefault(parent,{'id':'extend:'+parent,'layer':parent,'field':'active','before':q['active'][:],'after':q['active'][:],'reason':'Descendant active outside group window; may be intentional. Expansion affects ALL descendants.'})
    item['after']=[min(item['after'][0],a),max(item['after'][1],b)]
   parent=q.get('parent')
  for j in range(math.ceil(a*fps-1e-9),min(round(p['duration']*fps),math.ceil(b*fps-1e-9))):
   t=j/fps;M,op=world(l,by,t);own=val(l.get('opacity',1),t);stats['sampled_frames']+=1
   hidden=own>.05 and op<=.05 and bool(l.get('parent'));stats['parent_hidden_frames']+=int(hidden);stats['effective_visible_frames']+=int(op>.05)
   off=False
   # Only flat unwarped, explicit dimensions; no claim about matte or actual pixels.
   if op>.05 and l['kind'] in ('rect','ellipse','line','image') and 'w' in l and 'h' in l and not any(k in l for k in ('pitch','yaw','shadow','glow','blur','projected_blur','velocity_blur')):
    w,h=l['w']/2,l['h']/2;v=M@np.array([[-w,w,w,-w],[-h,-h,h,h],[1,1,1,1]])
    off=bool(v[0].max()<0 or v[0].min()>720 or v[1].max()<0 or v[1].min()>1280);stats['offscreen_bounds_frames']+=int(off)
   if (hidden or off) and stats['first_problem_s'] is None:stats['first_problem_s']=t
  out.append(stats)
 return {'layers':out,'repairs':list(proposals.values()),'limitations':'Affine bounds, sampled opacity and ancestor active windows only. Not rendered pixel visibility, matte, occlusion, perspective, materials or creative judgement.'}

def repair(plan,output,selected,expected):
 if sha(plan)!=expected:raise ValueError('source changed; audit current file')
 p=json.loads(plan.read_text());r=audit(p);options={x['id']:x for x in r['repairs']};by={l['id']:l for l in p['layers']}
 if not selected or len(set(selected))!=len(selected) or set(selected)-set(options):raise ValueError('select existing unique repair IDs')
 for key in selected:
  q=options[key];by[q['layer']][q['field']]=q['after']
 # The compiled plan uses absolute asset paths. Refuse moving relative assets.
 for l in p['layers']:
  for src in [l.get('src'),l.get('mesh',{}).get('src')]:
   if src and not Path(src).is_absolute() and output.resolve().parent!=plan.resolve().parent:raise ValueError('relative asset would move')
 if any(not Path(v).is_absolute() for v in p.get('fonts',{}).values()) and output.resolve().parent!=plan.resolve().parent:raise ValueError('relative font would move')
 validate(p,output.resolve().parent);output.parent.mkdir(parents=True,exist_ok=True);write(output,p)
 return {'source_sha256':expected,'output_sha256':sha(output),'applied':[options[k] for k in selected],'remaining':audit(p)['repairs'],'note':'New compiled-plan revision only. Update canonical source, recompile and visually review before normal gated export.'}

def main():
 a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True);b=s.add_parser('audit');b.add_argument('plan',type=Path);b=s.add_parser('repair');b.add_argument('plan',type=Path);b.add_argument('output',type=Path);b.add_argument('--expected-sha256',required=True);b.add_argument('--select',action='append',required=True);z=a.parse_args()
 if z.cmd=='audit':
  p=json.loads(z.plan.read_text());validate(p,z.plan.resolve().parent);r={'source_sha256':sha(z.plan),**audit(p)}
 else:r=repair(z.plan,z.output,z.select,z.expected_sha256)
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
