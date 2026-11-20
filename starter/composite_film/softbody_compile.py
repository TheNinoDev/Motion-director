"""Original standalone technical study and a targeted FORM recut."""
import json,sys,copy
from pathlib import Path
from volume_compile import build as prior
ROOT=Path(__file__).resolve().parents[2]
def recut(meta,image):
 p=prior(meta,image);D={l['id']:l for l in p['layers']};l=D['count-face'];a,b=l['active'];l.update(kind='text3d',material='chrome',depth=54,bevel3d=7,quality=.75,roughness=.19,yaw=[[a,-24],[a+.43,8,'sine'],[b,14,'sine']],pitch=[[a,12],[b,-5,'sine']],light=[[a,-.8],[b,.35,'linear']],softbody=dict(preset='silicone',frequency=3.4,events=[dict(time=a,strength=.22,mode='squash')]))
 l.pop('bevel',None);l.pop('projected_blur',None)
 D['hero']['mesh']['softbody']=dict(preset='rubber',frequency=5,events=[dict(time=.16,strength=.24,mode='bend'),dict(time=.38,strength=.35,mode='ripple')]);return p

def showcase():
 def L(id,kind,active,**kw):return dict(id=id,kind=kind,active=active,**kw)
 return dict(version=1,width=720,height=1280,fps=30,duration=6,background='#08090e',grain=.12,layers=[
 L('back','gradient',[0,6],x=360,y=640,w=720,h=1280,stops=[[0,'#10121b'],[.55,'#292d38'],[1,'#0b0c11']],angle=90),
 L('intro','text',[0,3],text='MATERIAL STUDIES / 032',x=360,y=155,size=24,color='#a8b4c8'),
 L('type','text3d',[0,3],text='08',font='heavy',size=490,maxw=610,x=360,y=550,depth=74,bevel3d=7,material='chrome',quality=.8,roughness=.14,yaw=[[0,-32],[1.3,12,'sine'],[3,25,'sine']],pitch=[[0,18],[3,-10,'sine']],light=[[0,-1],[3,.6,'linear']],softbody={'preset':'rubber','events':[{'time':.25,'mode':'squash','strength':.6},{'time':1.4,'mode':'bend','strength':.48}]},scale=[[0,.9],[.7,1,'sine'],[3,1.04,'linear']],shadow=True,shadow_opacity=.3,shadow_blur=30),
 L('sub','text',[0,3],text='EXTRUDED / BEVELED',x=360,y=1050,size=32,color='#e5eaf3'),
 L('hero-bg','gradient',[3,6],x=360,y=640,w=720,h=1280,stops=[[0,'#dde5e8'],[1,'#a6b5c8']],angle=90),
 L('bgtype','text',[3,6],text='ELASTIC',x=360,y=600,size=137,maxw=690,color='#263542'),
 L('glass','glass_object',[3,6],x=360,y=580,w=410,h=390,depth=340,geometry='rounded_box',material='prism',bevel3d=.28,quality=.6,yaw=[[3,-32],[6,36,'sine']],pitch=[[3,17],[6,-12,'sine']],light=[[3,-.3],[6,.6,'linear']],softbody={'preset':'jelly','events':[{'time':3.2,'mode':'squash','strength':.85},{'time':4.2,'mode':'twist','strength':.8},{'time':4.8,'mode':'bend','strength':-.66}]},background_gap=.24,roughness=.055),
 L('foot','text',[3,6],text='SOLID / IMPULSE RESPONSE',x=360,y=1050,size=27,color='#263542')],review_times=[0,.25,.48,.7,1.55,2.3,2.9,3.15,3.45,3.85,4.45,5.4])
if __name__=='__main__':
 out=Path(sys.argv[-1]);out.parent.mkdir(parents=True,exist_ok=True);p=showcase() if sys.argv[1]=='--showcase' else recut(json.loads(Path(sys.argv[1]).read_text()),ROOT/'examples/assets/v15-workspace.png');out.write_text(json.dumps(p,indent=2))
