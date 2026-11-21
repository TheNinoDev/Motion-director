#!/usr/bin/env python3
"""V68 local asset discovery and contact sheet; NEVER fetch external assets or confer rights.

Usage:
  python scripts/asset_scout_v68.py examples/asset-first-v68/illustrations \
    --out work/assets.json --sheet work/assets.jpg --source-class original
  python scripts/asset_scout_v68.py /path/to/project/public/icons --source-class product-site \
    --allow-product-icons --authorization-note 'Owner approved specific site icons for this project' \
    --out work/site-icons.json

This scanner does not decide whether a license covers a planned commercial film.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont, ImageOps

EXTS={'.png','.jpg','.jpeg','.webp','.gif','.svg'}
SKIP_DIRS={'node_modules','.git','.next','dist','build','venv','.venv','__pycache__','cache'}
RISKY_SVG_TAGS={'script','foreignObject','iframe','object','embed','audio','video','image','animate','set','animateMotion','animateTransform'}
REMOTE_PATTERN=re.compile(r'(?:url\s*\(\s*["\']?\s*(?:https?:|file:|data:)|(?:@import|javascript:|<\s*!DOCTYPE))',re.I)


def safe_svg(path):
    """Conservative read-only eligibility scan; production must also sanitize/render safely."""
    from defusedxml import ElementTree as DET
    try:
        raw=path.read_text(encoding='utf-8')
        if len(raw)>5_000_000 or REMOTE_PATTERN.search(raw):
            return False,'remote/executable or oversized content'
        root=DET.fromstring(raw)
        if root.tag.split('}')[-1]!='svg':
            return False,'not SVG root'
        for e in root.iter():
            name=e.tag.split('}')[-1]
            if name in RISKY_SVG_TAGS:
                return False,'unsafe element: '+name
            for k,v in e.attrib.items():
                key=k.split('}')[-1].lower()
                if key.startswith('on') or key in ('href','src') and (not v.startswith('#')):
                    return False,'event handler or external resource'
                if REMOTE_PATTERN.search(v) or 'javascript:' in v.lower():
                    return False,'remote or executable attribute'
        return True,'ok'
    except (OSError,ValueError,ET.ParseError,UnicodeDecodeError,TypeError) as e:
        return False,str(e)[:180]


def candidates(root,max_files=500):
    if root.is_file():
        return [root] if root.suffix.lower() in EXTS else []
    out=[]
    for p in root.rglob('*'):
        if any(x in SKIP_DIRS for x in p.relative_to(root).parts):
            continue
        if p.is_file() and p.suffix.lower() in EXTS and p.stat().st_size<=20_000_000:
            out.append(p)
            if len(out)>=max_files:break
    return sorted(out)


def preview(path):
    try:
        if path.suffix.lower()=='.svg':
            import cairosvg
            from io import BytesIO
            return Image.open(BytesIO(cairosvg.svg2png(url=str(path),output_width=200,output_height=200))).convert('RGBA')
        return Image.open(path).convert('RGBA')
    except (OSError,ValueError,ImportError) as e:
        return None


def scan(root, source_class='original', allow_product_icons=False, authorization_note='', max_files=500):
    root=Path(root).resolve()
    if not root.exists():raise FileNotFoundError(root)
    if source_class=='product-site' and (not allow_product_icons or not authorization_note.strip()):
        raise ValueError('Product-site visuals are information-only by default. Explicit --allow-product-icons AND --authorization-note required for an approved icons directory.')
    rows=[]
    for path in candidates(root,max_files):
        if source_class=='product-site':
            low=path.as_posix().lower()
            if not (any(s in low for s in ('icon','emoji','glyph','pictogram')) or (root.is_dir() and root.name.lower() in {'icons','icon','emojis','glyphs'})):
                continue
        valid,why=(safe_svg(path) if path.suffix.lower()=='.svg' else (True,'ok'))
        rows.append({'path':str(path.relative_to(root)) if root.is_dir() else path.name,
                     'kind':path.suffix.lower().strip('.'),'bytes':path.stat().st_size,
                     'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'safe_to_preview':valid,'check':why,'source_class':source_class,
                     'rights_status':'needs-independent-verification' if source_class!='original' else 'original-verify-creator',
                     'authorization_note':authorization_note if source_class=='product-site' else '',
                     'purpose':'unassigned','used_in_scene':False})
    return {'schema':'motion-director-asset-inventory-v68','root':str(root),'source_class':source_class,
            'files_scanned':len(rows),'usable_previews':sum(x['safe_to_preview'] for x in rows),
            'warning':'Listing or preview does not grant commercial use, remove provenance obligations, or authorize a site screenshot.',
            'assets':rows}


def sheet(root,data,path):
    rows=data['assets'][:60]
    cols=5
    cellw,cellh=230,275
    nrows=max(1,(len(rows)+cols-1)//cols)
    im=Image.new('RGB',(cols*cellw,nrows*cellh),'#101b2d')
    d=ImageDraw.Draw(im)
    font=ImageFont.load_default()
    for i,r in enumerate(rows):
        x=i%cols*cellw;y=i//cols*cellh
        d.rounded_rectangle((x+8,y+10,x+cellw-8,y+cellh-8),radius=18,fill='#233047')
        p=(root/r['path']) if root.is_dir() else root
        if r['safe_to_preview']:
            art=preview(p)
            if art is not None:
                art.thumbnail((185,195),Image.Resampling.LANCZOS)
                paste_x=x+(cellw-art.width)//2;paste_y=y+23+(196-art.height)//2
                im.paste(art,(paste_x,paste_y),art)
        label=r['path'][:31]
        d.text((x+14,y+224),label,font=font,fill='#ffffff')
        d.text((x+14,y+245), 'inspect rights' if r['safe_to_preview'] else 'unsafe SVG',font=font,fill='#ffbf8a' if not r['safe_to_preview'] else '#9ef2cd')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    im.save(path)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--sheet',type=Path)
    ap.add_argument('--source-class',choices=['original','independent-third-party','product-site'],default='original')
    ap.add_argument('--allow-product-icons',action='store_true')
    ap.add_argument('--authorization-note',default='')
    ap.add_argument('--max-files',type=int,default=500)
    a=ap.parse_args()
    d=scan(a.root,a.source_class,a.allow_product_icons,a.authorization_note,a.max_files)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    if a.sheet:sheet(a.root.resolve(),d,a.sheet)
    print(json.dumps({'files_scanned':d['files_scanned'],'usable_previews':d['usable_previews'],'manifest':str(a.out),'sheet':str(a.sheet) if a.sheet else None}))

if __name__=='__main__':main()
