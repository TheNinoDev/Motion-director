"""Authored FORM refinement, not a generic automatic director. Uses the existing global layer graph."""
import json,sys,math
from pathlib import Path
from premium_compile import compile_plan
ROOT=Path(__file__).resolve().parents[2]
def build(meta,image):
 p=compile_plan(meta,image);L=p['layers'];D={l['id']:l for l in L}; S=[x['start_frame']/30 for x in meta]+[p['duration']];end=S[-1];ink='#101117';paper='#eeeee8';lime='#dbf68a';lav='#c6c8f0';white='#f8f8f3'
 def K(*a):return [[round(t,6),v,*e] for t,v,*e in a]
 def add(kind,id,a,b,**kw):return dict(kind=kind,id=id,active=[round(a,6),round(b,6)],**kw)
 def insert(before,*layers):L[L.index(D[before]):L.index(D[before])]=layers
 def text(id,a,b,txt,x,y,size,**kw):return add('text',id,a,b,text=txt,x=x,y=y,size=size,font='heavy',**kw)
 def rect(id,a,b,x,y,w,h,**kw):return add('rect',id,a,b,x=x,y=y,w=w,h=h,**kw)
 def grad(id,a,b,stops,angle=55,**kw):return add('gradient',id,a,b,w=720,h=1280,x=360,y=640,stops=stops,angle=angle,**kw)
 def shadow(l,opacity=.27,blur=18,y=16):l.update(shadow=True,shadow_opacity=opacity,shadow_blur=blur,shadow_y=y)
 # Opening poster now has an ink-on-paper stage and a camera contraction from the actual question.
 D['paper'].update(color=paper);D['ghost'].update(text='SEND',color='#cdd0c6',outline=3,scale=K((0,1.05),(2.75,1.36,'linear')),y=K((0,895),(2.75,695,'linear')))
 D['msg']['y']=K((0,810),(.55,605,'spring'),(1.6,588,'sine'),(2.23,605),(2.75,-230,'in'));shadow(D['bubble'],.26,24,20);D['bubble']['projected_blur']=.65
 insert('msg',add('text','intro-counter',0,2.45,text='01 / REQUEST',x=114,y=110,size=16,color=ink,font='mono'),rect('intro-rule',0,2.4,360,147,640,2,color='#aaa99f',scale_x=K((0,0),(.5,1,'out'))),text('intro-footer',.8,2.45,'One question.',360,1042,42,color=ink,opacity=K((.8,0),(1.1,1,'out'))))
 # Search: genuine staggered hierarchy, count changes with file arrivals, perspective blur and layered shadow.
 a,b,c=S[1:4];D['dark'].update(kind='gradient',stops=[[0,'#242632'],[.45,'#101117'],[1,'#08090d']],angle=72,mask_feather=.09)
 for i,num in enumerate(('01','02','03','04')):
  bg=D['cardbg'+num];shadow(bg,.38,13,11);bg['projected_blur']=.8;D['card'+num]['rotate'][-2][1]=[-22,17,-9,12][i]
  for prefix in ('num','name','ext'):D[prefix+num]['projected_blur']=.65
 # Count intercut uses its own typography and clipped file detail, temporarily replacing the list without full-screen slide.
 st=b+.18;en=b+1.21
 insert('scan',rect('countfield',st,en,360,640,720,1280,color=ink,mask='diagonal',mask_progress=K((st,0),(st+.20,1,'quint')),mask_feather=.065),text('count-shadow',st,en,'04',360,640,490,color='#454853',outline=2,scale=K((st,.9),(en,1.25,'linear')),maxw=690),text('count-face',st+.09,en,'04',360,603,450,color=white,material='metal',light=K((st,.12),(en,.98,'linear')),bevel=12,maxw=610,projected_blur=.65,scale=K((st,.65),(st+.46,1,'spring'),(en,1.04,'linear'))),text('count-caption',st+.24,en,'SEPARATE LINKS',360,931,35,color=lime,reveal=K((st+.24,0),(st+.49,1,'out'))))
 D['scan']['active']=[en,c-.62];D['scan']['opacity']=K((en,0),(en+.2,.9),(c-.85,.9),(c-.62,0)) if en+.2<c-.85 else .65
 # Broken story: film strips of the actual fictional interface through a moving text matte.
 a,b=S[3:5];D['lavender'].update(kind='gradient',stops=[[0,'#b5b8ea'],[1,'#e5e5fa']],angle=85,mask_feather=.05)
 D['none-outline']['opacity']=K((a,.45),(a+1.45,.45),(a+1.65,0,'out'));D['none-solid']['active'][1]=a+1.49
 st=a+1.52;en=a+2.49
 insert('thewhole',text('story-mask',st,en,'WHOLE',360,630,290,maxw=620,color='white',matte_only=True,scale=K((st,.82),(st+.35,1,'quint'),(en,1.06,'linear'))),text('story-base',st,en,'WHOLE',360,630,290,maxw=620,color=ink,scale=K((st,.82),(st+.35,1,'quint'),(en,1.06,'linear'))),add('image','story-inside',st,en,src=str(image),x=K((st,180),(en,520,'linear')),y=640,w=1340,opacity=.48,matte='story-mask'),text('story-sub',st+.08,en,'Not the individual pieces.',360,830,30,color=ink,reveal=K((st+.08,0),(st+.34,1,'out'))))
 D['thewhole']['active'][0]=en;D['thewhole']['reveal']=K((en,0),(en+.22,1,'out'));D['story']['active'][0]=en+.1;D['story']['reveal']=K((en+.1,0),(en+.36,1,'out'));D['story']['size']=188
 # CGI macro film: moving key light, rim, as a short cinematic visual punctuation.
 a,b=S[4:6];D['hero']['mesh'].update(roughness=.22,zoom=[[0,2.2],[.32,1.65,'smooth'],[.65,1.12,'smooth'],[1,1.48,'smooth']],yaw=[[0,1.65],[.52,.28,'smooth'],[1,-.25,'smooth']],light=[[0,-.7],[.4,.35,'linear'],[1,1.5,'linear']]);D['one']['y']=250;D['one']['size']=260;D['one']['maxw']=700
 D['place']['y']=1035; D['place']['size']=92
 # Product proof: dark surface, big crop, typography separated spatially, no tiny full screenshot as only evidence.
 a,b=S[5:7];D['proof'].update(kind='gradient',stops=[[0,'#e8f5c0'],[.5,'#cfe993'],[1,'#b3cd71']],angle=90,mask_feather=.08)
 D['proofHeader']['color']='#d8edaa';D['proofHeader']['h']=260;D['proofHeader']['y']=130
 D['screen']['projected_blur']=.7;shadow(D['screen'],.33,26,23)
 D['proofcam']['scale']=K((a+.08,.55),(a+.56,1.04,'spring'),(a+1.12,1.04),(a+1.65,1.72,'quint'),(a+2.2,1.72),(a+2.68,1.72,'quint'),(b+.15,1.04,'quint'))
 D['proofcam']['y']=K((a+.08,1030),(a+.56,700,'quint'),(a+1.12,700),(a+1.65,770,'quint'),(a+2.68,770),(b+.15,700,'quint'))
 insert('proofHeader',add('lens','proof-lens',a+1.48,a+2.52,x=K((a+1.48,95),(a+2.52,610,'quint')),y=K((a+1.48,705),(a+2.52,860,'quint')),w=186,h=180,strength=.12,dispersion=.009,shine=.65,opacity=K((a+1.48,0),(a+1.72,.8),(a+2.28,.8),(a+2.52,0))))
 # End: callback link and small deliberate brand signature rather than idle 2s logo.
 shadow(D['replybubble'],.25,28,18);D['replybubble']['projected_blur']=.7;D['linkpill']['projected_blur']=.7;D['replycamera']['rotate']=K((S[6]+1.28,-6),(S[6]+1.85,0,'spring'))
 a,b=S[7:9];D['endpaper'].update(kind='gradient',stops=[[0,'#20242b'],[1,'#090a0e']],angle=50,mask_feather=.1);D['form']['scale']=K((a+.15,.68),(a+.7,1,'spring'),(b,1.035,'linear'));D['form']['projected_blur']=.7
 insert('tag',rect('signature-line',a+.79,b,360,706,480,2,color=lime,scale_x=K((a+.79,0),(a+1.22,1,'quint'))))
 p['review_times']=sorted(set(round(t,2) for t in p['review_times']+[S[2]+.66,S[3]+1.95,S[5]+1.74]));p['sound_events'] += [dict(time=5.44,kind='impact',gain_db=-26),dict(time=9.55,kind='whoosh',gain_db=-28),dict(time=16.71,kind='click',gain_db=-29)];return p
if __name__=='__main__':
 meta=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True);p=build(meta,ROOT/'examples/assets/v15-workspace.png');out.write_text(json.dumps(p,indent=2));print(len(p['layers']),p['duration'])
