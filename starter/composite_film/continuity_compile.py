"""Targeted V30 recut of FORM. Reusable glass is in optics.py, not this authored timeline."""
from refined_compile import build as base_build
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2]
def build(meta,image):
 p=base_build(meta,image);D={l['id']:l for l in p['layers']};L=p['layers'];a=meta[4]['start_frame']/30;b=meta[5]['start_frame']/30
 def K(*points):return [[round(t,6),v,*e] for t,v,*e in points]
 # Persistent outgoing composition: the aperture reveals the incoming CGI directly, no intermediate black screen.
 D['lavender']['active'][1]=a+.60
 for key,y,end_y in [('thewhole',595,288),('story',730,995)]:
  l=D[key];l['active'][1]=a+.48;l['y']=K((a-.48,y),(a+.42,end_y,'sine'));l['scale']=K((a-.48,1),(a+.42,.78,'sine'));l['opacity']=K((a-.2,1),(a+.10,1),(a+.43,0,'sine'));l['projected_blur']=.72
 for i in range(1,5):
  l=D[f'fragment{i:02d}'];l['active'][1]=a+.34;l['opacity']=K((a-.38,1),(a+.23,0,'sine'))
 # mesh is a full canvas: the exact same layer supplies the new background and actual CGI.
 D['ink']['active'][0]=a+.57;D['ink']['mask_progress']=1
 hero=D['hero'];hero['active']=[a-.32,b+.48];hero['opacity']=1;hero['mask']='iris';hero['mask_progress']=K((a-.32,0),(a+.60,1,'sine'));hero['mask_feather']=.075
 hero['mesh'].update(zoom=[[0,1.05],[.19,1.30,'smooth'],[.48,1.17,'smooth'],[.83,1.18,'smooth'],[1,1.56,'smooth']],yaw=[[0,1.30],[.55,.28,'smooth'],[1,-.25,'smooth']],twist=[[0,1.45],[1,.2,'smooth']])
 for key,start,y,from_y in [('one',a+.12,250,165),('place',a+.44,1035,1125)]:
  l=D[key];l['active']=[start,b+.38];l['reveal']=1;l['y']=K((start,from_y),(start+.50,y,'quint'),(b-.24,y),(b+.32,640+(y-640)*1.22,'sine'));l['opacity']=K((start,0),(start+.36,1,'sine'),(b-.15,1),(b+.32,0,'sine'));l['projected_blur']=.7
 # Next transition: the product field covers the still moving mesh before it ends.
 # Background begins before cue; header is not an opaque rectangle appearing on one frame.
 D['proof']['active'][0]=b-.13;D['proof']['mask_progress']=K((b-.13,0),(b+.44,1,'sine'));D['proofHeader']['opacity']=K((b,0),(b+.52,1,'sine'))
 D['proofcam']['scale']=K((b+.08,.70),(b+.56,1.04,'quint'),(b+1.12,1.04),(b+1.65,1.72,'quint'),(b+2.2,1.72),(b+2.68,1.72),(meta[6]['start_frame']/30+.15,1.04,'quint'))
 D['proof-lens'].update(shape='squircle',rotate=K((b+1.48,-23),(b+2.52,20,'sine')),scale=K((b+1.48,.75),(b+1.88,1.08,'sine'),(b+2.52,.81,'sine')),frost=.35,tint_mix=.045,strength=.13,radius=.35,edge_feather=2.)
 # A lens is optional; avoid duplicate glass motifs without reason.
 p['review_times']=sorted(set(p['review_times']+[round(a+x,3) for x in [-.30,-.1,.1,.3,.5,.7]]+[round(b+x,3) for x in [-.1,.1,.3,.5]]));return p
if __name__=='__main__':
 out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(build(json.loads(Path(sys.argv[1]).read_text()),ROOT/'examples/assets/v15-workspace.png'),indent=2))
