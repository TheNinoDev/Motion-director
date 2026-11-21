#!/usr/bin/env python3
"""Import locally installed Solar static SVGs. Solar artwork CC BY 4.0 (480 Design)."""
import argparse,json,re
from pathlib import Path
from xml.etree import ElementTree as ET
BAD={'script','foreignObject','iframe','image','animate','animateTransform','set','audio','video'}
def safe_svg(svg):
    if len(svg)>512000 or re.search(r'<!DOCTYPE|<!ENTITY',svg,re.I):raise ValueError('unsafe SVG DTD/size')
    root=ET.fromstring(svg)
    if root.tag.split('}')[-1]!='svg':raise ValueError('SVG root required')
    for e in root.iter():
        if e.tag.split('}')[-1] in BAD:raise ValueError('unsafe SVG element')
        for k,v in e.attrib.items():
            name=k.split('}')[-1].lower()
            if name.startswith('on') or name in ('href','src') or re.search(r'url\s*\(|@import|javascript:|data:|https?://',v,re.I):raise ValueError('unsafe SVG link/style')
    return root
def find(source,term):
    return sorted(p.relative_to(source).as_posix() for p in source.glob('**/*.svg') if term.lower() in p.stem.lower())
def import_one(source,style,name,out,primary='#16426A',secondary='#7DE6D3',size=360):
    if not all(re.fullmatch('[a-z0-9][a-z0-9-]*',x) for x in [style,name]):raise ValueError('bad icon name/style')
    if not all(re.fullmatch('#[0-9A-Fa-f]{6}',x) for x in [primary,secondary]):raise ValueError('bad colors')
    f=source/style/(name+'.svg')
    raw=f.read_text(encoding='utf-8');safe_svg(raw)
    colors={'--solar-color':primary,'--solar-secondary-color':secondary,'--solar-secondary-opacity':'0.45'}
    raw=re.sub(r'var\(\s*(--solar-(?:color|secondary-color|secondary-opacity))\s*(?:,\s*[^)]+)?\)',lambda m:colors[m.group(1)],raw).replace('currentColor',primary)
    safe_svg(raw)
    out.mkdir(parents=True,exist_ok=True)
    outsvg=out/(name+'-'+style+'.svg');outpng=out/(name+'-'+style+'.png')
    outsvg.write_text(raw,encoding='utf-8')
    import cairosvg
    cairosvg.svg2png(bytestring=raw.encode(),write_to=str(outpng),output_width=size,output_height=size)
    note={'name':name,'style':style,'source':str(f),'author':'480 Design','license':'CC BY 4.0','attribution':'Solar Icons by 480 Design, colors modified','size':size}
    (out/(name+'-'+style+'.json')).write_text(json.dumps(note,indent=2),encoding='utf-8')
    return note
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--find');p.add_argument('--style',default='bold-duotone');p.add_argument('--name');p.add_argument('--out',type=Path,default=Path('work/solar'));p.add_argument('--primary',default='#16426A');p.add_argument('--secondary',default='#7DE6D3');p.add_argument('--size',type=int,default=360);a=p.parse_args()
    if a.find:print('\n'.join(find(a.source,a.find)))
    elif a.name:print(json.dumps(import_one(a.source,a.style,a.name,a.out,a.primary,a.secondary,a.size),indent=2))
    else:p.error('--name or --find required')
