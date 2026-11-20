#!/usr/bin/env python3
"""Editable continuous showroom. Use actual product assets for production."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

def k(*p):return [list(x) for x in p]
def build(brand='FORM',headline='Make it yours.',detail='One space. Your rules.',image='assets/v14-concept.png'):
    layers=[]
    def L(id,kind,size,x,y,**kw):layers.append(dict(id=id,kind=kind,size=size,x=x,y=y,**kw))
    L('dots','grid',[1080,1760],540,920,color='#5f8aaf40',step=52,dot=1.5,depth=.25,opacity=k((0,.3),(65,.6),(156,.35),(179,.1)))
    L('light','gradient',[1040,1150],k((0,340),(58,730,'inout'),(125,390,'inout'),(179,540)),k((0,650),(58,890,'inout'),(125,1000),(179,860)),color='#425ccf50',depth=.3,opacity=k((0,.4),(30,.8),(75,.5),(120,.65),(179,.3)))
    L('spark','particles',[950,970],540,900,color='#a8c8ff60',depth=.4,count=65,seed=21,scale=k((0,.8),(45,1.1,'out'),(86,.9,'inout'),(145,1.4,'inout')),rotation=k((0,-4),(145,11)),opacity=k((0,.25),(45,.65),(90,.3),(142,.6),(155,0)),reveal_axis='dissolve',reveal=k((0,.2),(25,1,'out'),(132,1),(153,0,'inout')))
    L('line','line',[850,5],540,254,color='#658daf70',depth=0,reveal=k((0,0),(20,1,'out')))
    L('label','text',[760,40],485,210,text=f'{brand.upper()}  /  STUDIO NOTES',font_size=27,color='#a5b6d5',depth=0,decorative=True)
    L('index','text',[150,40],890,210,text='01 — 03',font_size=24,color='#a5b6d5',align='right',depth=0,decorative=True)
    L('orbit','ring',[740,740],540,920,color='#9fb8f15c',stroke_width=3,scale=k((0,.55),(34,1,'out'),(55,1.15,'inout'),(88,.75,'inout'),(125,1.2),(160,.3,'inout')),tilt=k((0,0),(54,48),(90,0),(130,-38),(160,0)),rotation=k((0,-20),(179,20)),glow=.4,opacity=k((0,.55),(44,.42),(64,.1),(102,.65),(157,.12),(179,0)))
    L('hero','text',[900,440],540,k((0,900),(23,900),(45,560,'inout'),(86,560),(105,430,'out')),text=headline.replace(' it ', ' it\n'),font_size=232,align='center',scale=k((0,1.12),(22,1,'out'),(45,.68,'inout'),(86,.68),(105,.45,'out')),reveal=k((0,.3),(16,1,'out')),opacity=k((0,1),(90,1),(105,0,'inout')),metal=k((0,.75),(28,.2),(45,0)),glow=k((0,.6),(26,.1),(45,0)),end=106)
    L('support','text',[810,95],540,k((0,1180),(25,1150,'out'),(45,680,'inout')),text='A LITTLE LESS ORDINARY.',font_size=43,color='#a5b6d5',align='center',reveal=k((0,0),(10,0),(28,1,'out')),opacity=k((0,0),(10,1),(38,1),(53,0,'out')),end=54)
    L('panel','image',[855,680],k((28,1060),(53,540,'out'),(89,480),(125,540,'inout'),(150,540)),k((28,1200),(53,1080,'out'),(89,970),(125,950,'inout'),(150,960)),src=image,radius=35,tilt=k((28,-48),(53,0,'out'),(85,14),(125,0,'inout')),rotation=k((28,12),(53,0,'out'),(85,-4),(125,0,'inout')),scale=k((28,.75),(53,1,'out'),(68,1.14,'inout'),(90,.90,'inout'),(125,1.04),(150,.72,'inout')),opacity=k((28,0),(45,1,'out'),(131,1),(145,0,'inout')),shadow=.9,glow=.24,trail=.5,start=28,end=147)
    L('focus-ring','ring',[140,140],820,1135,color='#b4d3ff',stroke_width=4,depth=1,glow=.5,scale=k((73,.25),(87,1.45,'out')),opacity=k((73,0),(76,.85),(87,0,'out')),start=73,end=88)
    L('caption','text',[880,135],540,k((51,1510),(65,1490,'out'),(113,1490),(130,1430,'inout')),text=detail,font_size=65,color='#f1f4ff',align='center',reveal=k((51,0),(72,1,'out')),opacity=k((51,0),(60,1),(131,1),(144,0)),start=51,end=152)
    for i,(label,x,y,rot) in enumerate([('IDENTITY',245,590,-11),('DESIGN',820,680,10),('LINKS',290,1370,-7)]):
        st=94+i*5; xs=k((st,x+(-210 if i!=1 else 220)),(st+18,x,'out'),(148,540,'inout'));ys=k((st,y+100),(st+18,y,'out'),(148,960,'inout'));rs=k((st,rot*2),(st+18,rot,'out'),(148,0));op=k((st,0),(st+15,1),(131,1),(143,0));L('chip'+str(i),'rect',[282,100],xs,ys,rotation=rs,color='#13243b',stroke='#96b4fa',radius=20,opacity=op,glow=.45,trail=.65,start=st,end=152);L('chiptext'+str(i),'text',[260,80],xs,ys,rotation=rs,color='#eaf1ff',text=label,font_size=34,align='center',opacity=op,start=st,end=152)
    L('mark','text',[920,270],540,890,text=brand.upper(),font_size=216,align='center',metal=.7,glow=.35,scale=k((147,.65),(158,1.08,'out'),(170,1,'inout')),reveal=k((147,0),(159,1,'out')),opacity=k((147,0),(155,1)),start=147)
    L('end-copy','text',[840,80],540,1090,text=headline,font_size=52,align='center',color='#b7c8e7',reveal=k((153,0),(167,1,'out')),start=153)
    L('footer','line',[850,5],540,1610,color='#658daf70',depth=0,reveal=k((0,0),(20,1,'out')))
    L('footlabel','text',[850,40],540,1653,text='MOTION STUDY  /  CONCEPT ONLY',font_size=25,color='#8198bb',depth=0,decorative=True)
    return dict(version=1,width=1080,height=1920,fps=30,shots=[dict(id='continuous-showcase',engine='layers',frames=180,content=dict(background='#080b13',ambient=dict(color='#355080',strength=.32),camera=dict(zoom=k((0,1.03),(40,1),(85,1.06),(128,1),(179,1))),layers=layers))])
def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--brand',default='FORM');p.add_argument('--headline',default='Make it yours.');p.add_argument('--detail',default='One space. Your rules.');p.add_argument('--image',default='assets/v14-concept.png');a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(build(a.brand,a.headline,a.detail,a.image),indent=2))
if __name__=='__main__':main()
