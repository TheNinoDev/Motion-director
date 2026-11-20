#!/usr/bin/env python3
"""Editable three-beat scaffold: hook, shared motif, product proof, branded resolution."""
import argparse,json
from pathlib import Path

def build(brand,hook,benefit,cta,image,frames=(62,76,78),width=1080,height=1920,fps=30,samples=2,accent='#aec4ff'):
    if len(frames)!=3 or any(type(n) is not int or not 48<=n<=900 for n in frames):raise ValueError('three beat durations must each be 48..900 frames')
    if not 1<=samples<=8:raise ValueError('samples must be 1..8')
    for k,v,m in [('brand',brand,18),('hook',hook,65),('benefit',benefit,70),('cta',cta,45)]:
        if not isinstance(v,str) or not v.strip() or len(v)>m:raise ValueError(f'{k}: expected 1..{m} characters')
    if not image:raise ValueError('provide actual authorized product screenshot')
    if len(accent)!=7 or accent[0]!='#':raise ValueError('accent must be #RRGGBB')
    int(accent[1:],16);shots=[]
    def shot(id,n,bg,overlap=0,transition='cut'):
        ls=[];s=dict(id=id,engine='layers',frames=n,content=dict(background=bg,samples=samples,shutter=.58,layers=ls))
        if overlap:s['transition_in']=dict(kind=transition,frames=overlap)
        shots.append(s)
        def t(p):return round(p*(n-1))
        def K(*args):return [[t(a[0]),*a[1:]] for a in args]
        def L(id,kind,size,x,y,**kw):
            if 'from_' in kw:kw['from']=kw.pop('from_')
            ls.append(dict(id=id,kind=kind,size=size,x=x,y=y,**kw))
        return s,L,K,t
    n=frames[0];s,L,K,t=shot('hook-motif',n,'#090a0c');s['content']['ambient']=dict(color='#263348',strength=.20,x=.5,y=.55)
    L('index','text',[860,42],540,260,text='01  /  '+brand.upper(),font_size=29,color='#9da4af',decorative=True,depth=0)
    L('hairline','line',[850,3],540,310,color='#39414c',reveal=K((0,0),(.28,1,'out')),depth=0)
    L('hook','text',[910,370],540,K((0,730),(.22,710,'out'),(.57,710),(.84,480,'inout')),text=hook,font_size=180,align='left',color='#f6f6f5',scale=K((0,1.0),(.24,1,'out'),(.62,1),(.92,.65,'inout')),opacity=K((0,1),(.68,1),(.94,0,'inout')),reveal=1,depth=0)
    L('swarm','swarm',[875,875],540,K((0,1360),(.40,1240,'out'),(.75,960,'inout')),color=accent,from_='grid',to='ring',count=400,dot=5.0,arc=.31,scatter=.10,drag=.4,seed=124,progress=K((0,0),(.17,0),(.78,1,'inout')),scale=K((0,1.2),(.58,1,'inout'),(.88,.66,'inout'),(1,.66)),opacity=K((0,.60),(.18,1),(.72,1),(.98,0,'out')),glow=.22)
    L('anchor','morph',[820,820],540,960,color=accent,from_='ring',to='circle',progress=0,outline=6,scale=.66,opacity=K((.62,0),(.85,1,'out')),start=t(.62),glow=.18)
    n=frames[1];s,L,K,t=shot('proof-reframe',n,'#eeeeea')
    L('anchor','morph',[820,820],540,960,color='#15171b',from_='ring',to='square',outline=10,progress=K((0,0),(.34,1,'inout')),scale=K((0,.66),(.31,1.24,'inout'),(.56,1.55,'out')),opacity=K((0,1),(.35,.85),(.54,0,'out')),rotation=K((0,0),(.32,-11,'inout')))
    L('number','text',[260,130],220,415,text='02',font_size=106,color='#25292d',reveal=K((0,0),(.20,1,'out')),depth=0,decorative=True)
    L('division','line',[840,3],540,505,color='#939697',reveal=K((.1,0),(.37,1,'out')),depth=0)
    L('benefit','text',[900,255],540,650,text=benefit,font_size=106,color='#121416',align='left',reveal=K((0,0),(.19,0),(.37,1,'out')),depth=0)
    L('panel','image',[950,850],K((.12,720),(.39,540,'out'),(.60,520,'inout'),(.84,540,'inout')),K((.12,1450),(.39,1205,'out'),(.60,1205,'inout'),(.84,1205,'inout')),src=image,radius=28,scale=K((.12,.24),(.38,.94,'out'),(.61,.98,'inout'),(.85,.93,'inout')),rotation=K((.12,-14),(.39,0,'out')),tilt=K((.12,-43),(.39,0,'out')),opacity=K((.12,0),(.26,1,'out')),shadow=.56,start=t(.12),depth=1)
    L('foot','text',[820,54],540,1640,text=brand.upper()+'  /  PRODUCT VIEW',font_size=26,color='#676b70',align='left',reveal=K((.4,0),(.58,1,'out')),decorative=True,depth=0)
    n=frames[2];s,L,K,t=shot('resolution',n,'#0a0b0d',6,'circleclose');s['content']['ambient']=dict(color='#243344',strength=.24,x=.5,y=.46)
    L('path','swarm',[980,980],540,875,color=accent,from_='ring',to='text',text=brand.upper(),count=650,dot=4,arc=.35,scatter=.10,drag=.5,seed=124,progress=K((0,0),(.12,0),(.49,1,'inout')),opacity=K((0,1),(.48,1),(.65,0,'out')),scale=K((0,1.15),(.45,1,'inout')),glow=.15)
    L('logo','morph',[980,980],540,875,color='#f7f8fb',from_='ring',to='text',text=brand.upper(),progress=K((0,0),(.42,1,'inout')),scale=K((0,1.15),(.42,1,'inout')),opacity=K((0,.18),(.37,.35),(.53,1,'out')),metal=K((0,.25),(.45,.65),(.67,0,'out')),glow=.05)
    L('cta','text',[870,135],540,1150,text=cta,font_size=65,color='#e8e9eb',align='center',reveal=K((.3,0),(.46,1,'out')),opacity=K((.3,0),(.46,1)),depth=0)
    L('last-line','line',[480,3],540,1270,color=accent,reveal=K((.42,0),(.52,1,'out')),depth=0)
    return dict(version=1,width=width,height=height,fps=fps,shots=shots)

def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--brand',required=True);p.add_argument('--hook',required=True);p.add_argument('--benefit',required=True);p.add_argument('--cta',required=True);p.add_argument('--image',required=True,help='path relative to output project file');p.add_argument('--frames',nargs=3,type=int,default=(62,76,78));p.add_argument('--width',type=int,default=1080);p.add_argument('--height',type=int,default=1920);p.add_argument('--fps',type=int,default=30);p.add_argument('--samples',type=int,default=2);p.add_argument('--accent',default='#aec4ff');a=p.parse_args();d=build(a.brand,a.hook,a.benefit,a.cta,a.image,a.frames,a.width,a.height,a.fps,a.samples,a.accent);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8')
if __name__=='__main__':main()
