#!/usr/bin/env python3
"""Check the structure of a creative decision record, not artistic merit or factual truth."""
import argparse,json,math
from pathlib import Path

def assess(x):
 errors=[];advice=[]
 def req(test,msg):
  if not test:errors.append(msg)
 def text(v):return isinstance(v,str) and bool(v.strip())
 def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
 if not isinstance(x,dict):return {'structure_valid':False,'errors':['Expected JSON object'],'advice':[]}
 for k in ('product','audience','central_idea','cta','platform'):req(text(x.get(k)),f'{k}: required meaningful text')
 duration=x.get('duration');req(finite(duration) and 0<duration<=180,'duration must be 0–180 seconds');valid_duration=finite(duration) and duration>0
 mode=x.get('mode');req(mode in ('advertisement','fictional_study','revision'),'mode invalid')
 proofs=x.get('proofs',[]);ids=set()
 if not isinstance(proofs,list):errors.append('proofs must be an array');proofs=[]
 for j,p in enumerate(proofs):
  if not isinstance(p,dict):errors.append(f'proof {j}: expected object');continue
  i=p.get('id');req(text(i) and i not in ids,f'proof {j}: unique id required');
  if text(i):ids.add(i)
  for k in ('claim','source','visible_evidence'):req(text(p.get(k)),f'proof {j}: {k} required')
  req(p.get('status') in ('verified_by_agent','illustrative','pending'),f'proof {j}: status required')
  if mode=='advertisement' and p.get('status')!='verified_by_agent':errors.append(f'proof {j}: actual ad requires verified evidence; do not assert a pending claim')
 if mode=='advertisement':req(bool(ids),'actual ad requires at least one proof reference')
 concepts=x.get('concepts',[])
 if not isinstance(concepts,list):errors.append('concepts must be array');concepts=[]
 families=set();names=set()
 for j,c in enumerate(concepts):
  if not isinstance(c,dict):errors.append(f'concept {j}: expected object');continue
  for k in ('id','family','visible_event','reason','risk'):req(text(c.get(k)),f'concept {j}: {k} required')
  if text(c.get('family')):families.add(c['family'])
  if text(c.get('id')):req(c['id'] not in names,f'concept {j}: duplicate id');names.add(c['id'])
 if mode=='advertisement':req(len(families)>=3,'develop three distinct idea families before selecting')
 req(x.get('selected_concept') in names if text(x.get('selected_concept')) else False,'selected_concept must reference existing concept')
 req(text(x.get('selection_reason')),'selection_reason required')
 beats=x.get('beats',[]);prev=0;prev_layout=None;repeats=0;used_proof=set();used_events=set()
 if not isinstance(beats,list) or not beats:errors.append('beats must be a nonempty array');beats=[]
 for i,b in enumerate(beats):
  if not isinstance(b,dict):errors.append(f'beat {i}: expected object');continue
  a,z=b.get('start'),b.get('end');ok=finite(a) and finite(z) and 0<=a<z
  req(ok,f'beat {i}: invalid timing')
  if ok:
   req(abs(a-prev)<=.001,f'beat {i}: gap or overlap; cover timeline exactly');prev=z
   if i==0 and z>3:advice.append('First beat exceeds 3s; verify immediate attention, not a slow logo intro.')
  for k in ('purpose','visible_event','dominant_subject','support_motion','outgoing_anchor','incoming_anchor','layout','audio_cue'):req(text(b.get(k)),f'beat {i}: {k} required')
  event=b.get('visible_event','');generic={'animate','cool animation','motion','animate nicely','text appears','zoom','fade','transition'}
  if text(event):
   if event.strip().lower() in generic:advice.append(f'beat {i}: describe a meaningful concrete action, not merely an effect name')
   if event.strip().lower() in used_events:advice.append(f'beat {i}: repeated visible event; verify narrative development')
   used_events.add(event.strip().lower())
  layout=b.get('layout');repeats=repeats+1 if layout==prev_layout else 1;prev_layout=layout
  if repeats==3:advice.append(f'beat {i}: third consecutive same layout; inspect slideshow tendency')
  p=b.get('proof_id');req(p is None or (text(p) and p in ids),f'beat {i}: unknown proof_id')
  if text(p):used_proof.add(p)
  if i>0 and isinstance(beats[i-1],dict):
   left=beats[i-1].get('outgoing_anchor');right=b.get('incoming_anchor')
   if text(left) and text(right) and left!=right and not text(b.get('cut_reason')):advice.append(f'beat {i}: no shared anchor; explain deliberate cut or match movement')
 if valid_duration:req(abs(prev-duration)<=.001,'beats do not end at declared duration')
 if mode=='advertisement':req(bool(used_proof),'at least one beat must show verified product evidence')
 if beats and isinstance(beats[-1],dict) and beats[-1].get('purpose') not in ('cta','callback','resolution'):advice.append('Verify a clear ending/CTA or deliberately resolved callback.')
 return {'structure_valid':not errors,'errors':errors,'advice':advice,'note':'Structure only. Source truth, rights, concept quality and actual visual execution require human/agent verification.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('record',type=Path);a=ap.parse_args();r=assess(json.loads(a.record.read_text()));print(json.dumps(r,indent=2));raise SystemExit(0 if r['structure_valid'] else 2)
if __name__=='__main__':main()
