"""Derive a compact list of absolute review timestamps around real motion events."""
import argparse,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'starter/composite_film'))
from compositor import validate,KEYS

def targets(p,limit=18):
 fps=p['fps'];n=round(p['duration']*fps);scores={}
 def add(t,reason,weight):
  f=max(0,min(n-1,round(t*fps)));x=scores.setdefault(f,{'score':0,'reasons':[]});x['score']+=weight
  if reason not in x['reasons']:x['reasons'].append(reason)
 add(0,'opening',12);add((n-1)/fps,'closing',12)
 for l in p['layers']:
  if l['kind']=='group' or l.get('matte_only'):continue
  a,b=l['active'];i=l['id'];priority=3 if l['kind'] in ('text3d','object3d','glass_object','mesh') else 1
  for t in (a,b):
   if 0<t<p['duration']:
    for dt in (-2,0,2):add(t+dt/fps,f'{i}: layer boundary',priority)
  add((a+b)/2,f'{i}: midpoint',priority)
  for key in sorted(KEYS):
   v=l.get(key)
   if isinstance(v,list) and v and isinstance(v[0],list):
    for pair in v:
     if a<=pair[0]<b:add(pair[0],f'{i}: {key}',priority)
  for event in l.get('softbody',{}).get('events',[]):
   t=event['time']
   for dt in (0,.08,.22):add(t+dt,f'{i}: elastic event',5)
 # Avoid a dense cluster consuming the whole budget; seed opening and closing.
 chosen={0,n-1};ordered=sorted(scores,key=lambda f:(-scores[f]['score'],f))
 for min_gap in (max(2,round(.15*fps)),1):
  for f in ordered:
   if len(chosen)>=limit:break
   if f not in chosen and all(abs(f-x)>=min_gap for x in chosen):chosen.add(f)
 return [dict(frame=f,time=f/fps,reasons=scores[f]['reasons']) for f in sorted(chosen)]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--limit',type=int,default=18);a=ap.parse_args();p=json.loads(a.plan.read_text());validate(p,a.plan.resolve().parent)
 if not 2<=a.limit<=60:ap.error('--limit must be 2–60')
 t=targets(p,a.limit);cmd=[sys.executable,str(ROOT/'starter/composite_film/compositor.py'),str(a.plan.resolve()),str(a.out.resolve()),'--size','1080','--profile','high','--backend','auto'];
 for x in t:cmd+=['--at',str(x['time'])]
 print(json.dumps({'targets':t,'render_argv':cmd,'note':'Inspect these native-resolution PNGs; this sampling does not replace playback.'},indent=2))
if __name__=='__main__':main()
