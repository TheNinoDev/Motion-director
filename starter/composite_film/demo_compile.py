#!/usr/bin/env python3
"""A complete authored fictional campaign. Configurable contents, no template claims.
The generated timeline is entirely editable; this example is not a universal story.
"""
import argparse,json,sys,math,subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'story_film'))
from film import audio
from music_cues import analyze,snap

ROOT=Path(__file__).resolve().parents[2]
PHRASES=[('Can you send me your work?',2.5),('Sure. Let me find the link.',2.75),('Actually, there are four.',2.65),('And somehow, none of them tell the whole story.',3.65),('What if there was just one place?',2.85),('Your projects. Your notes. A way to reach you.',3.65),('Next time they ask, just send one link.',3.7),('Form.',1.7)]

def compile_plan(out,meta,cues,image,fps=30):
 L=[];times=[m['start_frame']/fps for m in meta];end=sum(m['frames'] for m in meta)/fps;times.append(end); F='#eeeef0';B='#090a0c';A='#d9ed85';G='#86878c';INK='#171b13';idn=0
 def add(kind,id,span,**kw):L.append({'id':id,'kind':kind,'active':list(span),**kw});return id
 def text(id,span,txt,x,y,size,**kw):return add('text',id,span,text=txt,x=x,y=y,size=size,**kw)
 def rect(id,span,x,y,w,h,**kw):return add('rect',id,span,x=x,y=y,w=w,h=h,**kw)
 def pic(id,span,x,y,w,crop=None,**kw):return add('image',id,span,x=x,y=y,w=w,src=str(image),**({'crop':crop} if crop else {}),**kw)
 def track(*pairs):return [[round(x,5),y,*z] for x,y,*z in pairs]
 def cue(t):return snap(t,cues,.085)
 def enter(t,d=.30):return track((t,0),(t+d,1,'out'))
 def leave(a,b):return track((a,1),(b,0,'in'))
 def reveal(id,span,txt,x,y,size,when,**kw):return text(id,span,txt,x,y,size,reveal=enter(when,.32),**kw)
 def section(i):return times[i],times[i+1]
 def path(id,span,pts,**kw):return add('path',id,span,points=pts,w=720,h=1280,x=360,y=640,**kw)
 # opening: a typographic chat interaction, not fabricated product UI. Large close-up to actual composition.
 a,b=section(0); group=add('group','question-camera',(a,b+.24),x=track((a,360),(a+.45,360),(b-.45,360),(b+.24,175,'quint')),y=track((a,640),(b-.45,640),(b+.24,420,'quint')),scale=track((a,1.9),(a+.62,1,'quint'),(b-.42,1),(b+.24,2.5,'in')))
 text('question1',(a,b+.24),'Can you',-310,-94,118,parent=group,color=F,font='heavy',maxw=620,reveal=enter(a,.24)) # use centered anchor - fix after
 L[-1]['x']=-30
 reveal('question2',(a,b+.24),'send me',-35,26,118,a+.20,parent=group,color=F,font='heavy',maxw=620)
 reveal('question3',(a,b+.24),'your work?',-7,148,105,a+.43,parent=group,color=A,font='heavy',maxw=650)
 rect('typing-caret',(a+.58,b+.24),296,154,6,90,parent=group,color=A,opacity=track((a+.58,1),(a+1.10,1,'hold'),(a+1.11,0,'hold'),(a+1.48,0,'hold'),(a+1.49,1,'hold'),(b+.24,1)))
 # Opening is the question itself; no ornamental copy.
 # continuous file search. Cursor and filenames use common parent & persistent positions.
 a,b=section(1); c,d=section(2); e,f=section(3)
 # individual full-height dark field, no gray borders or microsized scaffolding
 text('search-label',(a,c+.12),'SEARCH',360,184,20,color=G,font='mono')
 rect('search-border',(a,c+.12),360,310,624,97,color='#3a3b40',radius=17,stroke=2,scale=track((a,.86),(a+.4,1,'out')))
 text('search-query',(a,c+.12),'portfolio',325,307,48,font='regular',reveal=enter(a+.07,.42))
 rect('search-caret',(a+.17,c+.12),437,310,3,44,color=A,opacity=enter(a+.17,.15))
 items=['portfolio.pdf','studio-notes.png','contact.txt','links.txt']; col=['#d9ed85','#b7bde8','#e8e8e6','#9ea0a5']
 for i,name in enumerate(items):
  s=cue(a+.52+i*.34); yy=468+i*125; group=add('group',f'file{i}',(s,d+.18),x=track((s,760),(s+.40,360,'out'),(c+.55,360),(d-.58,360+(i-1.5)*31,'quint'),(d+.18,360,'in')),y=track((s,yy+55),(s+.4,yy,'out'),(c+.55,yy),(d-.58,640+(i-1.5)*36,'quint'),(d+.18,640,'in')),rotate=track((s,-8),(s+.4,0,'out'),(c+.55,0),(d-.58,(i-1.5)*-8,'quint'),(d+.18,0)),scale=track((s,.93),(s+.4,1,'out'),(c+.55,1),(d-.58,.92,'quint'),(d+.18,.15,'in')),opacity=track((s,0),(s+.18,1),(d-.13,1),(d+.18,0)))
  rect(f'filebar{i}',(s,d+.18),0,0,622,97,parent=group,color='#181a1d',radius=14)
  rect(f'fileicon{i}',(s,d+.18),-255,0,41,52,parent=group,color=col[i],radius=6)
  text(f'filename{i}',(s,d+.18),name,-20,0,37,parent=group,font='regular',maxw=450,color=F)
  text(f'fileindex{i}',(s,d+.18),f'0{i+1}',260,0,21,parent=group,font='mono',color=G)
 # giant counter sits behind? layers ordering after cards, reveal only before collapse. Use white background for dramatic contrast, cut is intentional.
 text('four',(c+.2,d-.7),'04',360,222,344,color=F,font='heavy',material='metal',light=track((c+.2,.13),(d-.7,.83,'linear')),scale=track((c+.2,1.48),(c+.68,1,'quint'),(d-1.05,1),(d-.7,2.6,'in')),reveal=enter(c+.2,.30),opacity=track((c+.2,1),(d-.95,1),(d-.7,0)))
 # abstract data cascade from file outline to overfull screen, physical motif reused. diagonal image panels at the point of escalation.
 a,b=section(3); bgspan=(a,b)
 for i in range(12):
  s=a+.03+i*.055; en=b-.62; pos=145+i*90; x=360+(i%3-1)*50; opa=.35 if i%3 else .70
  rect(f'noisebar{i}',(s,en),track((s,1000),(s+.36,x,'out'),(en,360,'in')),track((s,pos+200),(s+.36,pos,'out'),(en,640,'in')),640,68,color='#292b30',radius=6,opacity=track((s,0),(s+.16,opa),(en-.17,opa),(en,0)))
  text(f'noisetext{i}',(s,en),items[i%4],track((s,1000),(s+.36,x-32,'out'),(en,360,'in')),track((s,pos+200),(s+.36,pos,'out'),(en,640,'in')),31,font='mono',color=G,opacity=track((s,0),(s+.19,opa),(en-.17,opa),(en,0)))
 # foreground matte and scale-aware editorial assertion: black reset holds for a reason.
 rect('scrim',(a+.65,b-.48),360,640,720,223,color=B,opacity=enter(a+.65,.3))
 reveal('whole1',(a+.72,b-.48),'None of them.',360,562,92,a+.72,color=F,maxw=660,font='heavy')
 reveal('whole2',(a+1.10,b-.48),'The whole story.',360,688,76,a+1.1,color=A,maxw=650)
 # single stroke emerges on reset; becomes a frame with the next shot, no cold scene restart.
 a,b=section(4); cp=b+.30; stroke=[(360,640),(360,420),(620,420),(620,860),(100,860),(100,420),(360,420)]
 path('singleStroke',(a-.50,a+.82),stroke,color=A,stroke=3,trim=track((a-.50,0),(a+.20,.15,'out'),(a+.65,1,'quint')),opacity=track((a-.50,0),(a-.25,1),(a+.55,1),(a+.82,0)),glow=.15)
 add('mesh','linkMetaphor',(a+.56,b-.09),x=360,y=640,w=720,h=1280,opacity=track((a+.56,0),(a+.90,1,'out'),(b-.32,1),(b-.09,0)),mesh={'kind':'ribbon','material':'chrome','resolution':80,'quality':.78,'samples':1,'bg':B,'grain':.12,'bloom':.04,'phase':[[0,0],[1,1]],'twist':[[0,1.4],[1,0,'smooth']],'yaw':[[0,.85],[1,.08,'smooth']],'pitch':[[0,.28],[1,.04,'smooth']],'roll':[[0,-.45],[1,.15,'smooth']],'zoom':[[0,1.8],[.50,1.22,'smooth'],[1,1.48,'smooth']],'light':[[0,-.35],[1,1.24,'linear']],'roughness':.19});text('oneQ',(a+.13,b+.13),'one place?',360,920,101,color=F,font='heavy',maxw=635,reveal=enter(a+.13,.32),scale=track((a+.13,.92),(a+.50,1,'out'),(b-.38,1),(b+.13,1.65,'in')),opacity=track((a+.13,1),(b-.30,1),(b+.13,0)))
 # product proof on a continuous global camera rig. Native screenshot capture; transitions via same rectangle and detail crop.
 a,b=section(5); c,d=section(6); e,f=section(7)
 # full-bleed brand color only when changing context. Other areas maintain reference-like restraint.
 rect('proofPaper',(a-.14,c+.10),360,640,720,1280,color=A,mask='iris',mask_progress=track((a-.14,0),(a+.38,1,'quint')),opacity=track((a-.14,1),(c-.07,1),(c+.10,0)))
 # screenshot top at center (image naturally 1200x950); zoom crop to UI evidence, then pull out. Never fake clicking functional product.
 group=add('group','product-camera',(a-.05,c+.10),x=track((a-.05,360),(a+.52,360,'quint'),(a+1.12,360),(a+1.72,662,'quint'),(a+2.12,662),(a+2.68,41,'quint'),(a+3.0,41),(c+.10,360,'quint')),y=track((a-.05,805),(a+.52,654,'quint'),(a+1.12,654),(a+1.72,698,'quint'),(a+2.12,698),(a+2.68,698,'quint'),(a+3.0,698),(c+.10,640,'quint')),scale=track((a-.05,.55),(a+.52,1.0,'quint'),(a+1.12,1),(a+1.72,1.65,'quint'),(a+2.12,1.65),(a+2.68,1.65,'quint'),(a+3.0,1.65),(c+.10,1.0,'quint')),rotate=track((a-.05,-9),(a+.52,0,'quint')),opacity=track((a-.05,0),(a+.22,1),(c-.07,1),(c+.10,0)))
 pic('actualUI',(a-.05,c+.10),0,0,670,parent=group,pitch=track((a-.05,25),(a+.52,0,'quint')),mask='diagonal',mask_progress=enter(a-.05,.44))
 rect('titleMatte',(a,c+.10),360,178,720,356,color=A,opacity=track((a,1),(c-.07,1),(c+.10,0)))
 # compact detail labels are stable, enough reading time, not fake dashboard statistics.
 for i,(label,st,en) in enumerate([('All your work.',a+.18,a+1.42),('Portfolio.',a+1.42,a+2.43),('Studio notes.',a+2.43,c-.04)]):
  text('proofTitle'+str(i),(st,en),label,360,215,87,color=INK,font='heavy',maxw=645,reveal=enter(st,.25))
 # second proof close-up of contact with dark UI, and callback single link.
 a,b=section(6); ss=a+.08; ee=a+1.52
 pic('contact',(ss,ee+.28),360,track((ss,760),(ss+.48,640,'quint')),650,crop=[.025,.613,.505,.72],mask='wipe',mask_progress=enter(ss,.38),scale=track((ss,1.18),(ss+.48,1,'quint')),opacity=track((ss,1),(ee,1),(ee+.28,0)))
 reveal('contactLabel',(ss,ee),'Reach me.',360,490,80,ss,color=F,font='heavy')
 group=add('group','returnCamera',(ee,b+.15),x=360,y=track((ee,820),(ee+.46,640,'quint'),(b-.35,640),(b+.15,640)),scale=track((ee,.8),(ee+.46,1,'quint'),(b-.3,1),(b+.15,1.65,'in')),opacity=track((ee,0),(ee+.25,1),(b-.30,1),(b+.15,0)))
 text('reply',(ee,b+.15),'Sure.',0,-182,100,parent=group,color=F,font='heavy',reveal=enter(ee,.30))
 rect('replybar',(ee,b+.15),0,0,640,94,parent=group,color=A,radius=24)
 text('replylink',(ee,b+.15),'FORM / portfolio',-18,0,41,parent=group,color=INK,font='regular',maxw=520,reveal=enter(ee+.19,.34))
 text('arrow',(ee,b+.15),'↗',268,0,43,parent=group,color=INK,font='regular',reveal=enter(ee+.44,.18))
 reveal('replynote',(ee+.38,b+.15),'One link.',0,148,64,ee+.38,parent=group,color=F,font='bold')
 a,b=section(7);text('brand',(a,b),'FORM',360,605,198,maxw=640,color=F,font='heavy',material='metal',light=track((a,.15),(b-.35,.65,'sine')),reveal=enter(a,.27),scale=track((a,1.15),(a+.48,1,'quint')))
 text('tagline',(a+.30,b),'Your work, in one place.',360,776,31,color=F,font='regular',reveal=enter(a+.30,.25))
 text('concept',(a+.45,b),'FICTIONAL CONCEPT',360,1060,17,color=G,font='mono',opacity=enter(a+.45,.35))
 # Avoid invalid floating rounding and reorder only as arranged, parent earlier. All positions at global picture time.
 plan={'version':1,'width':720,'height':1280,'fps':fps,'duration':end,'background':B,'grain':0.25,'seed':27,'shutter':.55,'shutter_windows':[[times[0],times[0]+.65],[times[1]+.4,times[1]+1.65],[times[3]-.65,times[3]+.75],[times[5]-.12,times[5]+.60],[times[5]+1.15,times[5]+1.75],[times[5]+2.14,times[5]+2.72]],'review_times':[round(t,4) for i in range(len(meta)) for t in [times[i]+.35*(times[i+1]-times[i]),times[i]+.78*(times[i+1]-times[i])]],'layers':L}
 plan['sound_events']=[{'time':cue(times[1]+.55),'kind':'click','gain_db':-23},{'time':cue(times[1]+1.22),'kind':'click','gain_db':-25},{'time':cue(times[2]+.22),'kind':'impact','gain_db':-21},{'time':times[3]-.38,'kind':'whoosh','gain_db':-23},{'time':times[4]-.23,'kind':'drop','gain_db':-25},{'time':times[4]+.63,'kind':'riser','gain_db':-26},{'time':times[5]+.09,'kind':'chime','gain_db':-24},{'time':times[5]+1.36,'kind':'whoosh','gain_db':-27},{'time':times[6]+1.64,'kind':'click','gain_db':-24},{'time':times[7]+.08,'kind':'chime','gain_db':-24}]
 return plan

def main():
 ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);ap.add_argument('--voice-dir',type=Path);ap.add_argument('--music',type=Path);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True);p={'fps':30,'bpm':120,'beats':[{'voice':v,'min':m} for v,m in PHRASES]};meta=audio(p,out,out,args.voice_dir.resolve() if args.voice_dir else None,args.music.resolve() if args.music else None);c=analyze(out/'music.wav');(out/'music-cues.json').write_text(json.dumps(c,indent=2));plan=compile_plan(out,meta,c['cues'],ROOT/'examples/assets/v15-workspace.png');(out/'plan.json').write_text(json.dumps(plan,indent=2));
 from mix_picture import mix_picture
 mix_picture(out/'mix.wav',plan,out/'final-mix.wav');print('layers',len(plan['layers']),'seconds',plan['duration']);
 # local file paths can be replayed by compile in any installation. Voice performance instructions distinct from clean script.
 (out/'script.txt').write_text('\n'.join(x[0] for x in PHRASES));
 def stamp(s):
  m=round(s*1000);return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'
 (out/'captions.srt').write_text('\n'.join(f'{i+1}\n{stamp(m["voice_start"])} --> {stamp(m["voice_end"])}\n{m["voice"]}\n' for i,m in enumerate(meta)))
if __name__=='__main__':main()
