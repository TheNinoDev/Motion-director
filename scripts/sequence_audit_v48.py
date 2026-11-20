#!/usr/bin/env python3
"""Inspect resolved schedule and compare compiled revisions, without modifying either source."""
import argparse,json
from pathlib import Path
from director_v48 import build
from agent_session import write

def load(p):return build(json.loads(p.read_text()),p.resolve().parent)
def report(p,e):
 fps=p['fps'];actions=e['cue_actions'];sounds=e['named_sound_cues']
 return {'fps':fps,'duration':p['duration'],'sequences':[{**x,'start_seconds':x['start_frame']/fps,'end_seconds':x['end_frame']/fps,'actions':[actions[i] for i in x['action_indices']],'sounds':[sounds[i] for i in x['sound_indices']]} for x in e['sequences']]}
def compare(a,b):
 p,e,_=a;q,f,_=b
 old={l['id']:l for l in p['layers']};new={l['id']:l for l in q['layers']};changes=[]
 for k in sorted(old.keys()|new.keys()):
  if k not in old or k not in new:changes.append({'layer':k,'fields':['added' if k in new else 'removed']});continue
  keys=sorted(key for key in old[k].keys()|new[k].keys() if old[k].get(key)!=new[k].get(key) or (key in old[k])!=(key in new[k]))
  if keys:changes.append({'layer':k,'fields':keys})
 sa={x['id']:x for x in report(p,e)['sequences']};sb={x['id']:x for x in report(q,f)['sequences']};seq=[]
 for key in sorted(sa.keys()|sb.keys()):
  if sa.get(key)!=sb.get(key):seq.append({'id':key,'before':sa.get(key),'after':sb.get(key)})
 return {'layer_changes':changes,'layer_order_changed':list(old)!=list(new),'global_changes':sorted(k for k in p.keys()|q.keys() if k!='layers' and p.get(k)!=q.get(k)),'marker_changes':[{'marker':k,'before':e['named_markers'].get(k),'after':f['named_markers'].get(k)} for k in sorted(e['named_markers'].keys()|f['named_markers'].keys()) if e['named_markers'].get(k)!=f['named_markers'].get(k)],'sequence_changes':seq,'audio_cues_changed':e['sound_cues']!=f['sound_cues'],'note':'Compiled property diff only. Reinspect actual media; does not compare changed bytes at unchanged asset paths.'}
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True)
 a=sub.add_parser('schedule');a.add_argument('source',type=Path);a.add_argument('--out',type=Path)
 a=sub.add_parser('compare');a.add_argument('before',type=Path);a.add_argument('after',type=Path);a.add_argument('--out',type=Path)
 z=ap.parse_args();r=report(*load(z.source)[:2]) if z.cmd=='schedule' else compare(load(z.before),load(z.after))
 if z.out:write(z.out,r)
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
