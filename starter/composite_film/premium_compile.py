"""Alternative authored cut of FORM; pure JSON layers, no custom shot renderer."""
import json,sys,math
from pathlib import Path
from recipes import resample
ROOT=Path(__file__).resolve().parents[2]
def compile_plan(meta,image):
 S=[x['start_frame']/30 for x in meta]+[sum(x['frames'] for x in meta)/30];end=S[-1]; L=[]; black='#101015';paper='#eff0e9';lime='#d3f77a';lav='#b6b8ec';white='#fafafa';gray='#aaaab3'
 def K(*p):return [[round(x,6),y,*z] for x,y,*z in p]
 def add(kind,id,a,b,**kw):L.append(dict(kind=kind,id=id,active=[a,b],**kw));return id
 def T(id,a,b,txt,x,y,size,**kw):return add('text',id,a,b,text=txt,x=x,y=y,size=size,**kw)
 def R(id,a,b,x,y,w,h,**kw):return add('rect',id,a,b,x=x,y=y,w=w,h=h,**kw)
 def G(id,a,b,**kw):return add('group',id,a,b,**kw)
 def I(id,a,b,x,y,w,**kw):return add('image',id,a,b,x=x,y=y,w=w,src=str(image),**kw)
 def E(a,d=.35):return K((a,0),(a+d,1,'out'))
 def O(a,b):return K((a,1),(b,0,'in'))
 # Opening: giant cropped type moves from physical poster into a conversation bubble.
 a,b=S[:2];R('paper',a,b+.25,360,640,720,1280,color=paper)
 T('ghost',a,b+.25,'WORK',360,650,430,maxw=1050,font='heavy',color='#d5d7cc',outline=2,scale=K((0,1.2),(b+.25,2.1,'linear')))
 g=G('msg',a,b+.25,x=K((0,360),(b-.45,360),(b+.25,360,'quint')),y=K((0,710),(.50,605,'back'),(b-.4,605),(b+.25,-230,'in')),rotate=K((0,-8),(.58,0,'out')),scale=K((0,.8),(.55,1,'back'),(b-.4,1),(b+.25,.82,'in')))
 R('bubble',a,b+.25,0,0,604,285,parent=g,radius=38,color=black,velocity_blur=.6)
 T('q1',a,b+.25,'Can you send',0,-64,65,parent=g,color=white,font='heavy',maxw=545,reveal=E(.04,.28))
 T('q2',a,b+.25,'me your work?',0,30,66,parent=g,color=lime,font='heavy',maxw=545,reveal=E(.3,.34))
 T('from',a,b+.25,'INCOMING MESSAGE',0,-208,20,parent=g,color=black,font='mono',reveal=E(.16))
 # Search as overflowing index, individual file cards approach from depth.
 a,b=S[1:3];c=S[3];R('dark',a,c+.1,360,640,720,1280,color=black,mask='wipe',mask_progress=E(a,.22))
 T('searchHead',a,c-.35,'Finding it…',360,180,88,color=white,font='heavy',maxw=620,reveal=E(a+.07))
 R('input',a+.22,c-.32,360,320,620,80,color='#2f3039',radius=16)
 T('query',a+.30,c-.32,'portfolio',300,320,40,color=white,font='regular',reveal=E(a+.3,.4));R('cursor',a+.7,b+.25,425,320,4,42,color=lime)
 cards=[('01','PORTFOLIO','.PDF',lime),('02','STUDIO NOTES','.PNG',lav),('03','CONTACT','.TXT',paper),('04','LINKS','.TXT','#f2bba5')]
 for i,(num,name,ext,col) in enumerate(cards):
  st=a+.55+i*.44; en=c+.1; y=488+i*146
  g=G('card'+num,st,en,x=K((st,850 if i%2==0 else -130),(st+.58,360,'out'),(b+.52,360),(c-.45,360+(i-1.5)*50,'quint'),(en,360,'in')),y=K((st,y+140),(st+.58,y,'out'),(b+.52,y),(c-.45,635+(i-1.5)*62,'quint'),(en,640,'in')),rotate=K((st,15*(-1)**i),(st+.58,0,'out'),(b+.52,0),(c-.45,-15+i*12,'quint'),(en,0)),scale=K((st,.7),(st+.58,1,'back'),(c-.45,1),(en,.04,'in')),opacity=K((st,0),(st+.18,1),(c-.10,1),(en,0)))
  R('cardbg'+num,st,en,0,0,610,126,parent=g,radius=18,color=col,velocity_blur=.65)
  T('num'+num,st,en,num,-245,-2,42,parent=g,color=black,font='heavy');T('name'+num,st,en,name,-20,-4,35,parent=g,color=black,font='heavy',maxw=365);T('ext'+num,st,en,ext,243,34,18,parent=g,color=black,font='mono')
 # Lens scans the file stack to give a moment of physical dimensionality. No glass over small text during reading.
 add('lens','scan',b+.13,c-.62,x=K((b+.13,640),(b+.70,475,'out'),(c-.62,85,'linear')),y=K((b+.13,390),(c-.62,1020,'linear')),w=214,h=220,strength=.18,dispersion=.013,shine=.76,opacity=K((b+.13,0),(b+.38,.9),(c-.85,.9),(c-.62,0)),light=K((b+.13,0),(c-.62,3.14,'linear')))
 # Macro type and divergent fragments, no generic headline/headline reset.
 a,b=S[3:5];R('lavender',a,b+.12,360,640,720,1280,color=lav,mask='iris',mask_progress=E(a,.43))
 T('none-outline',a+.12,b,'NONE',360,470,280,font='heavy',maxw=790,color='#7778aa',outline=3,scale=K((a+.12,1.8),(a+.65,1,'quint'),(b,1.18,'linear')))
 T('none-solid',a+.45,a+1.65,'None of them.',360,646,88,color=black,font='heavy',maxw=620,reveal=E(a+.45))
 for i,(num,name,ext,col) in enumerate(cards):
  st=a+1.30+i*.09;en=b+.1;x=[100,590,120,610][i];y=[255,365,920,1065][i]
  R('fragment'+num,st,en,K((st,360),(st+.55,x,'back'),(b-.4,x),(en,360,'in')),K((st,640),(st+.55,y,'back'),(b-.4,y),(en,640,'in')),282,82,color=col,radius=12,rotate=K((st,0),(st+.55,[-16,15,10,-12][i],'out'),(en,0,'in')),scale=K((st,.08),(st+.55,1,'back'),(b-.4,1),(en,.04,'in')),velocity_blur=.7)
 T('thewhole',a+1.64,b-.17,'THE WHOLE',360,595,104,maxw=650,font='heavy',color=black,reveal=E(a+1.64));T('story',a+1.95,b-.17,'STORY.',360,730,175,maxw=650,font='heavy',color=black,reveal=E(a+1.95))
 # 3D hero as one single reveal; gradient overlay underneath is not a separate mesh pass.
 a,b=S[4:6];R('ink',a,b+.15,360,640,720,1280,color=black,mask='iris',mask_progress=E(a,.32))
 add('mesh','hero',a+.18,b+.06,x=360,y=640,w=720,h=1280,opacity=K((a+.18,0),(a+.55,1,'out'),(b-.35,1),(b+.06,0)),mesh={'kind':'ribbon','material':'chrome','resolution':72,'quality':.68,'samples':1,'bg':black,'grain':.06,'bloom':.035,'phase':[[0,0],[1,1]],'twist':[[0,1.7],[1,.2,'smooth']],'yaw':[[0,1.2],[1,-.12,'smooth']],'pitch':[[0,.3],[1,.04,'smooth']],'roll':[[0,-.6],[1,.08,'smooth']],'zoom':[[0,2.0],[.6,1.12,'smooth'],[1,1.35,'smooth']],'light':[[0,-.35],[1,1.24,'linear']],'roughness':.17})
 T('one',a+.35,b+.05,'ONE',360,210,205,color=white,font='heavy',maxw=620,reveal=E(a+.35,.44),opacity=O(b-.25,b+.05));T('place',a+.78,b+.05,'place?',360,1080,109,color=lime,font='heavy',reveal=E(a+.78),opacity=O(b-.25,b+.05))
 # Proof: continuous actual screen, with purposeful magnifier; genuine crop to contact proof.
 a,b=S[5:7];R('proof',a,b+.15,360,640,720,1280,color=lime,mask='diagonal',mask_progress=E(a,.44))
 g=G('proofcam',a+.08,b+.15,x=K((a+.08,360),(a+.58,360,'quint'),(a+1.15,360),(a+1.8,555,'quint'),(a+2.2,555),(a+2.7,180,'quint'),(a+3.15,180),(b+.15,360,'quint')),y=K((a+.08,920),(a+.58,710,'quint'),(a+1.15,710),(a+1.8,720,'quint'),(a+2.7,720),(b+.15,710,'quint')),scale=K((a+.08,.48),(a+.58,1,'back'),(a+1.15,1),(a+1.8,1.6,'quint'),(a+2.7,1.6),(b+.15,1,'quint')),rotate=K((a+.08,9),(a+.58,0,'quint')))
 I('screen',a+.08,b+.15,0,0,658,parent=g,velocity_blur=.3)
 R('proofHeader',a,b+.15,360,135,720,270,color=lime)
 for i,(txt,st,en) in enumerate([('Your projects.',a+.15,a+1.46),('Your notes.',a+1.46,a+2.55),('All together.',a+2.55,b+.10)]):T('proof'+str(i),st,en,txt,360,175,83,color=black,font='heavy',maxw=650,reveal=E(st,.24))
 # Return to opening bubble; user action and visible link as the payoff.
 a,b=S[6:8];R('returnpaper',a,b+.08,360,640,720,1280,color=paper,mask='wipe',mask_progress=E(a,.32))
 T('reach',a+.16,a+1.40,'Reach me.',360,260,91,font='heavy',color=black,reveal=E(a+.16));I('contact',a+.19,a+1.46,360,K((a+.19,720),(a+.65,555,'back')),650,crop=[.025,.613,.505,.72],opacity=O(a+1.24,a+1.46))
 g=G('replycamera',a+1.28,b+.08,x=360,y=K((a+1.28,830),(a+1.85,620,'back'),(b-.27,620),(b+.08,640,'quint')),scale=K((a+1.28,.85),(a+1.85,1,'back'),(b-.27,1),(b+.08,1.06,'quint')))
 R('replybubble',a+1.28,b+.08,0,0,610,300,parent=g,color=black,radius=40);T('sure',a+1.46,b+.08,'Sure.',-162,-72,76,parent=g,color=white,font='heavy',reveal=E(a+1.46))
 R('linkpill',a+1.75,b+.08,0,62,536,92,parent=g,color=lime,radius=24,scale=K((a+1.75,.1),(a+2.12,1,'back')));T('url',a+1.91,b+.08,'FORM / portfolio   ↗',0,62,36,parent=g,color=black,font='bold',maxw=485,reveal=E(a+1.91,.27));T('oneLink',a+2.2,b+.08,'One link.',0,230,83,parent=g,color=black,font='heavy',reveal=E(a+2.2))
 a,b=S[7:9];R('endpaper',a,b,360,640,720,1280,color=black,mask='iris',mask_progress=E(a,.34));T('form',a+.15,b,'FORM',360,600,210,maxw=650,font='heavy',color=lime,scale=K((a+.15,.78),(a+.68,1,'back')),reveal=E(a+.15,.38));T('tag',a+.45,b,'Your work, in one place.',360,770,34,font='regular',color=white,reveal=E(a+.45));T('label',a+.45,b,'FICTIONAL PRODUCT STUDY',360,1120,17,font='mono',color=gray)
 return dict(version=1,width=720,height=1280,fps=30,duration=end,background=black,grain=0,layers=L,review_times=[round(S[i]+p*(S[i+1]-S[i]),3) for i in range(8) for p in (.24,.58,.84)],sound_events=[dict(time=t,kind=k,gain_db=g) for t,k,g in [(0.45,'impact',-23),(2.52,'whoosh',-23),(3.07,'click',-24),(3.52,'click',-25),(3.95,'click',-24),(4.39,'click',-25),(7.68,'whoosh',-21),(8.1,'impact',-23),(11.8,'drop',-22),(14.9,'chime',-24),(16.4,'whoosh',-27),(20.35,'click',-22),(22.4,'chime',-24)]])
if __name__=='__main__':
 meta=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True);p=compile_plan(meta,ROOT/'examples/assets/v15-workspace.png');out.write_text(json.dumps(p,indent=2));print(len(p['layers']),p['duration'])
