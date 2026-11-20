"""Authored FORM refinement, plus independent reusable volume showcase."""
import json,sys
from pathlib import Path
from continuity_compile import build as base_build
ROOT=Path(__file__).resolve().parents[2]
def build(meta,image):
 p=base_build(meta,image);D={l['id']:l for l in p['layers']};L=p['layers']
 l=D['proof-lens'];a,b=l['active'];l.update(kind='glass_object',geometry='rounded_box',material='clear',depth=100,bevel3d=.24,quality=.65,yaw=[[a,-42],[b,36,'sine']],pitch=[[a,22],[b,-16,'sine']],ior=1.37,roughness=.07,background_gap=.18,reflection=.85,absorption=.9,dispersion=.01)
 for k in ['shape','strength','shine','frost','tint_mix','radius','edge_feather']:l.pop(k,None)
 # Reduce the earlier unrelated optical pass; a single optical motif is enough.
 L.remove(D['scan'])
 return p

def showcase():
 # Standalone: independently animatable solid bodies over a changing 2D scene.
 def layer(id,kind,**kw):return dict(id=id,kind=kind,active=[0,6],**kw)
 return dict(version=1,width=720,height=1280,fps=30,duration=6,background='#101218',layers=[
 layer('bg','gradient',x=360,y=640,w=720,h=1280,stops=[[0,'#10121b'],[.5,'#2c374b'],[1,'#111820']]),
 layer('type','text',text='LIGHT',x=360,y=625,size=160,w=680,color='#e6edfb'),
 layer('sub','text',text='MATERIAL / 031',x=360,y=1020,size=26,color='#d4e5ff'),
 layer('group','group',x=360,y=590,rotate=[[0,-12],[6,12,'sine']]),
 layer('box','glass_object',parent='group',x=-106,y=-170,w=238,h=214,depth=172,geometry='rounded_box',material='clear',yaw=[[0,-26],[6,55,'sine']],pitch=[[0,18],[6,-20,'sine']],phase3d=[[0,0],[3,.62,'sine'],[6,0,'sine']],rotate=[[0,8],[6,-16,'sine']],quality=.6,bevel3d=.19),
 layer('orb','glass_object',parent='group',x=[[0,130],[3,70,'sine'],[6,130,'sine']],y=115,w=240,h=240,depth=240,geometry='sphere',material='prism',background_gap=.25,quality=.6),
 layer('ring','object3d',parent='group',x=100,y=-103,w=200,h=210,depth=83,geometry='torus',material='chrome',yaw=[[0,30],[6,-45,'sine']],pitch=24,quality=.6),
 layer('front','text',text='SOLID / OPTICAL',x=360,y=1120,size=24,color='#e6edfb')],review_times=[0,1.5,3,4.5,5.9])
if __name__=='__main__':
 out=Path(sys.argv[-1]);out.parent.mkdir(parents=True,exist_ok=True)
 p=showcase() if sys.argv[1]=='--showcase' else build(json.loads(Path(sys.argv[1]).read_text()),ROOT/'examples/assets/v15-workspace.png');out.write_text(json.dumps(p,indent=2))
