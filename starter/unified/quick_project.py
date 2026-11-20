#!/usr/bin/env python3
"""Make an editable four-shot starting plan; does NOT invent voice copy or claims.

Agent provides four VERIFIED phrases and an optional authentic screenshot.
This is an initial timing scaffold; final duration must follow actual voiceover.
"""
import argparse, json, shutil, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('hook','proof','brand','cta'):p.add_argument('--'+key,required=True)
    p.add_argument('--screenshot',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--width',type=int,default=540);p.add_argument('--height',type=int,default=960)
    p.add_argument('--fps',type=int,default=30)
    a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True)
    if not 160<=a.width<=2160 or not 160<=a.height<=3840 or a.width%2 or a.height%2 or not 10<=a.fps<=60:raise ValueError('Invalid raster / fps')
    if any(not 1<=len(getattr(a,k).strip())<=105 for k in ('hook','proof','brand','cta')):raise ValueError('Text must be 1–105 chars')
    if a.screenshot:
        if not a.screenshot.is_file():raise ValueError('Screenshot not found')
        if a.screenshot.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):raise ValueError('Screenshot must be PNG/JPG/WebP')
        assetdir=a.out.parent/'assets';assetdir.mkdir(exist_ok=True)
        source=assetdir/('screenshot'+a.screenshot.suffix.lower());shutil.copy2(a.screenshot,source)
        proof={'id':'02-proof','engine':'ui','frames':a.fps*2,'transition_in':{'kind':'dissolve','frames':min(6,a.fps//4)},
          'content':{'background':'#08090b','layers':[
             {'type':'image','src':str(source.relative_to(a.out.parent)),'x':a.width//2,'y':a.height//2,'w':int(a.width*.78),'h':int(a.height*.55),'radius':12,'animate':{'scale':[[0,1.6],[a.fps,1.0,'inout']]}},
             {'type':'text','text':a.proof,'size':max(14,int(a.width*.055)),'x':a.width//2,'y':int(a.height*.83),'color':'#fff'}]}}
    else:
        proof={'id':'02-proof','engine':'type','frames':a.fps*2,'transition_in':{'kind':'dissolve','frames':min(6,a.fps//4)},
               'content':{'kind':'hero','text':a.proof,'chrome':False}}
    out={'version':1,'title':'DRAFT SCAFFOLD — timing and claims must be verified','width':a.width,'height':a.height,'fps':a.fps,
         'shots':[
           {'id':'01-hook','engine':'type','frames':int(a.fps*1.5),'content':{'kind':'hero','text':a.hook,'chrome':False}},
           proof,
           {'id':'03-motif','engine':'material','frames':a.fps,'content':{'kind':'metal','text':a.brand[:1].upper(),'caption':a.brand,'roughness':.18,'reflection':.4}},
           {'id':'04-payoff','engine':'type','frames':a.fps*2,'transition_in':{'kind':'dissolve','frames':min(6,a.fps//4)},
            'content':{'kind':'hero','text':a.brand,'subtitle':a.cta,'chrome':False}}
         ]}
    a.out.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
    print('DRAFT:',a.out,'— use actual speech timings before final production')

if __name__=='__main__':
    try:main()
    except (ValueError,OSError) as e:sys.exit('ERROR: '+str(e))
