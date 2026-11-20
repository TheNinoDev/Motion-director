#!/usr/bin/env python3
"""Build a deliberately varied, editable four-beat sequence. Use real evidence and narration timing."""
import argparse,json
from pathlib import Path
STYLES={'editorial':('ribbons','orbit','scanner','waves'),'technical':('network','halftone','scanner','sparkfield'),'kinetic':('halftone','aperture','ribbons','orbit'),'luxury':('sparkfield','orbit','waves','aperture')}

def build(brand,hook,benefit,cta,image,style='editorial',accent='#d5ed87',frames=(45,48,78,57),width=1080,height=1920,fps=30,samples=1,detail=None):
    if style not in STYLES:raise ValueError('unknown style')
    if len(frames)!=4 or any(type(n)!=int or not 30<=n<=900 for n in frames):raise ValueError('four shot durations 30..900 frames')
    if samples not in range(1,9):raise ValueError('samples 1..8')
    for key,v,limit in [('brand',brand,18),('hook',hook,65),('benefit',benefit,75),('cta',cta,45)]:
        if not isinstance(v,str) or not v.strip() or len(v)>limit:raise ValueError('invalid '+key)
    if not image:raise ValueError('provide product image')
    if not isinstance(accent,str) or len(accent)!=7 or accent[0]!='#':raise ValueError('expected #RRGGBB')
    int(accent[1:],16);shots=[];fx=STYLES[style];white='#f4f4ef';ink='#101113';mute='#8a8e92'
    def shot(i,name,bg,trans=None):
        n=frames[i];layers=[];c={'background':bg,'samples':samples,'shutter':.5,'layers':layers};s={'id':name,'engine':'layers','frames':n,'content':c};shots.append(s)
        if trans:s['transition_in']={'kind':trans,'frames':4}
        def K(*pairs):return [[round(q*(n-1)),v,*e] for q,v,*e in pairs]
        def L(id,kind,size,x,y,**kw):layers.append(dict(id=id,kind=kind,size=size,x=x,y=y,**kw))
        return c,L,K
    c,L,K=shot(0,'opening', '#101113');c['ambient']={'color':'#566150','strength':.22,'x':.35,'y':.67};c['camera']={'zoom':K((0,1.04),(1,1,'inout'))}
    L('texture',fx[0],[1050,1200],540,1220,color=accent,count=48,stroke_width=2,opacity=.55,progress=K((0,.15),(1,.9)),speed=.6,depth=.5)
    L('index','text',[900,55],540,316,text=brand.upper()+'  /  01',font_size=36,color=accent,decorative=True,depth=0)
    L('rule','line',[910,3],540,365,color='#6e7863',reveal=K((0,0),(.2,1,'out')),depth=0)
    L('headline','text',[920,440],540,K((0,690),(.22,660,'out'),(1,650,'inout')),text=hook,font_size=176,color=white,opacity=K((0,.2),(.15,1,'out')),reveal=K((0,.12),(.22,1,'out')),reveal_axis='y',feather=5,depth=0)
    L('hero','morph',[630,630],540,1240,**{'from':'ring','to':'ring'},progress=0,outline=15,color='#d9e1cd',metal=.88,scale=K((0,.65),(.45,1.0,'out'),(1,1.1,'inout')),tilt=K((0,-50),(1,20,'inout')),pitch=K((0,12),(1,-8,'inout')),glow=.08)
    c,L,K=shot(1,'motif',accent);c['camera']={'zoom':K((0,.98),(.48,1.02,'inout'),(1,1.12,'inout'))}
    L('field',fx[1],[990,990],540,1050,color='#334323',count=48,stroke_width=3,progress=K((0,.08),(1,.88,'inout')),opacity=.9,speed=.8)
    L('label','text',[900,85],540,395,text='02  /  THE IDEA',font_size=36,color=ink,decorative=True,depth=0)
    L('motif','morph',[850,850],540,1050,**{'from':'ring','to':'square'},progress=K((0,0),(.22,0),(.85,1,'inout')),color=ink,outline=12,scale=K((0,.76),(.85,1.02,'inout')),rotation=K((0,0),(.85,-5,'inout')))
    L('panel','image',[650,520],540,1050,src=image,radius=25,scale=K((.15,.42),(.9,1,'out')),opacity=K((.15,0),(.65,1,'out')),reveal=K((.12,0),(.84,1,'inout')),reveal_axis='radial',feather=10,shadow=.25,tilt=K((0,30),(1,0,'inout')))
    c,L,K=shot(2,'product-proof','#eaece5');c['camera']={'zoom':K((0,1),(.3,1.02,'out'),(.8,1,'inout'))}
    L('marker','rect',[80,8],150,385,color='#6a773a',radius=2,depth=0)
    L('benefit','text',[900,330],540,600,text=benefit,font_size=136,color=ink,reveal=K((0,.15),(.22,1,'out')),reveal_axis='y',feather=4,depth=0)
    L('proof-shadow','rect',[940,740],540,1190,color='#b6bcb0',radius=28,opacity=.4,rotation=K((0,-5),(.35,0,'out')))
    L('panel','image',[940,740],540,K((0,1280),(.30,1185,'out'),(1,1170,'inout')),src=image,radius=20,scale=K((0,.78),(.30,1,'out'),(1,1.015,'inout')),tilt=K((0,14),(.32,0,'out')),pitch=K((0,-10),(.32,0,'out')),shadow=.35)
    L('trace',fx[2],[920,720],540,1185,color='#c5e96b',count=20,progress=K((0,0),(.2,0),(.74,1,'inout')),opacity=K((0,0),(.18,.36),(.72,.36),(.9,0)),stroke_width=3,speed=.6)
    if detail is not None:
        if len(detail)!=4 or not (0<=detail[0]<detail[2]<=1 and 0<=detail[1]<detail[3]<=1):raise ValueError('detail crop must be normalized left top right bottom')
        full=next(l for l in c['layers'] if l['id']=='panel');full['opacity']=K((0,1),(.45,1),(.61,0,'inout'));full['y']=K((0,1280),(.30,1185,'out'),(.49,1185),(.66,1420,'inout'));full['scale']=K((0,.78),(.30,1,'out'),(.49,1),(.66,1.25,'inout'))
        L('detail','image',[940,740],540,1185,src=image,crop=detail,radius=16,scale=K((.47,.74),(.68,1.02,'out'),(1,1.04,'inout')),opacity=K((.45,0),(.64,1,'inout')),reveal=K((.42,0),(.68,1,'inout')),reveal_axis='y',feather=6,shadow=.34)
        trace=next(l for l in c['layers'] if l['id']=='trace');trace['opacity']=K((0,0),(.18,.36),(.43,.36),(.5,0));
    L('proof-label','text',[900,62],540,1620,text=brand.upper()+'  /  PRODUCT VIEW',font_size=29,color='#525751',decorative=True,depth=0)
    c,L,K=shot(3,'end','#101113','circleclose');c['ambient']={'color':'#61704c','strength':.22,'x':.5,'y':.44}
    L('echo',fx[3],[1050,1040],540,925,color=accent,count=64,stroke_width=2,opacity=K((0,.6),(.48,.38),(.73,.15,'out')),progress=K((0,0),(.8,1)),speed=.6)
    L('collect','swarm',[950,850],540,910,**{'from':'ring','to':'text'},text=brand.upper(),color=accent,count=550,dot=4,arc=.22,scatter=.07,progress=K((0,0),(.1,0),(.52,1,'inout')),opacity=K((0,.9),(.45,.9),(.64,0,'out')))
    L('brand','text',[920,280],540,910,text=brand.upper(),font_size=195,align='center',color=white,opacity=K((0,0),(.43,0),(.62,1,'out')),scale=K((0,.95),(.65,1,'out')),depth=0)
    L('action','text',[900,140],540,1180,text=cta,font_size=66,align='center',color=white,opacity=K((0,0),(.48,0),(.65,1,'out')),depth=0)
    L('rule','line',[420,3],540,1325,color=accent,reveal=K((0,0),(.48,0),(.68,1,'out')),depth=0)
    return dict(version=1,width=width,height=height,fps=fps,shots=shots)

def main():
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--brand',required=True);p.add_argument('--hook',required=True);p.add_argument('--benefit',required=True);p.add_argument('--cta',required=True);p.add_argument('--image',required=True);p.add_argument('--style',choices=STYLES,default='editorial');p.add_argument('--accent',default='#d5ed87');p.add_argument('--frames',type=int,nargs=4,default=(45,48,78,57));p.add_argument('--width',type=int,default=1080);p.add_argument('--height',type=int,default=1920);p.add_argument('--fps',type=int,default=30);p.add_argument('--samples',type=int,default=1);p.add_argument('--detail',type=float,nargs=4,help='optional normalized crop of actual UI');a=p.parse_args();d=build(a.brand,a.hook,a.benefit,a.cta,a.image,a.style,a.accent,a.frames,a.width,a.height,a.fps,a.samples,a.detail);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,indent=2),encoding='utf8')
if __name__=='__main__':main()
