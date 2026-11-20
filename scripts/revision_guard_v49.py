#!/usr/bin/env python3
"""Capture before editing: compare actual asset bytes and compiled state, not paths alone."""
import argparse,json
from pathlib import Path
from agent_session import sha,write
from director_v49 import build
from sequence_audit_v48 import compare

def capture(source,creative=None,audio=None):
 source=Path(source).resolve();p,e,n=build(json.loads(source.read_text()),source.parent)
 assets={}
 def add(role,path):
  f=(source.parent/path).resolve()
  if not f.is_file():raise ValueError('missing asset '+str(f))
  assets[role]={'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size}
 for l in p['layers']:
  if l['kind']=='image':add('image:'+l['id'],l['src'])
  if l['kind']=='mesh' and l.get('mesh',{}).get('src'):add('mesh:'+l['id'],l['mesh']['src'])
 for name,path in p.get('fonts',{}).items():add('font:'+name,path)
 if creative:add('creative',str(Path(creative).resolve()))
 if audio:add('audio',str(Path(audio).resolve()))
 return {'version':49,'source':str(source),'source_sha256':sha(source),'plan':p,'expanded':e,'notes':n,'assets':assets}

def diff(a,b):
 if a.get('version')!=49 or b.get('version')!=49:raise ValueError('need two V49 snapshots')
 r=compare((a['plan'],a['expanded'],a['notes']),(b['plan'],b['expanded'],b['notes']));aa=a['assets'];bb=b['assets'];changes=[]
 for role in sorted(aa.keys()|bb.keys()):
  x,y=aa.get(role),bb.get(role)
  if x!=y:changes.append({'role':role,'before':x,'after':y,'bytes_changed':not x or not y or x['sha256']!=y['sha256']})
 r['asset_changes']=changes;r['source_changed']=a['source_sha256']!=b['source_sha256'];r['note']='Explicit file snapshots and compiled state, not proof of visual equivalence. System fonts and renderer binaries are not fingerprinted.'
 return r

def guard(report,allow):
 allowed=set(allow);actual=set()
 for x in report['layer_changes']:
  actual.update('layer:'+x['layer']+':'+f for f in x['fields'])
 actual.update('global:'+x for x in report['global_changes'])
 actual.update('marker:'+x['marker'] for x in report['marker_changes'])
 actual.update('sequence:'+x['id'] for x in report['sequence_changes'])
 actual.update('asset:'+x['role'] for x in report['asset_changes'])
 if report['layer_order_changed']:actual.add('layer_order')
 if report['audio_cues_changed']:actual.add('audio_cues')
 unexpected=sorted(actual-allowed)
 return {'ready_for_visual_review':not unexpected,'unexpected':unexpected,'actual':sorted(actual),'unused_allowances':sorted(allowed-actual),'note':'Do not broaden allowlist merely to pass. Review actual changed and adjacent frames; this is not approval.'}

def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True);a=s.add_parser('capture');a.add_argument('source',type=Path);a.add_argument('output',type=Path);a.add_argument('--creative',type=Path);a.add_argument('--audio',type=Path)
 a=s.add_parser('compare');a.add_argument('before',type=Path);a.add_argument('after',type=Path);a.add_argument('--out',type=Path);a.add_argument('--allow',action='append',default=None)
 z=p.parse_args()
 if z.cmd=='capture':r=capture(z.source,z.creative,z.audio);write(z.output,r);r={'snapshot':str(z.output),'assets':len(r['assets']),'layers':len(r['plan']['layers'])}
 else:
  r=diff(json.loads(z.before.read_text()),json.loads(z.after.read_text()));r['guard']=guard(r,z.allow if z.allow is not None else [])
  if z.out:write(z.out,r)
 print(json.dumps(r,indent=2));raise SystemExit(2 if z.cmd=='compare' and not r['guard']['ready_for_visual_review'] else 0)
if __name__=='__main__':main()
