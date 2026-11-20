#!/usr/bin/env python3
"""Curated typography discovery + installed-font resolver. Never distributes fonts."""
import argparse,json,subprocess,shutil,os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
def catalog():return json.loads((ROOT/'assets/font-catalog-v34.json').read_text())['families']
def installed():
 out={}
 def add(family,style,path):
  if Path(path).is_file():out.setdefault(family.casefold(),[]).append((style,path))
 if shutil.which('fc-list'):
  r=subprocess.run(['fc-list','--format','%{family}\t%{style}\t%{file}\n'],capture_output=True,text=True,check=True)
  for line in r.stdout.splitlines():
   try:f,s,p=line.split('\t',2)
   except ValueError:continue
   for name in f.split(','):add(name,s,p)
 else:
  for root in [Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts',Path(os.environ.get('LOCALAPPDATA','~')).expanduser()/'Microsoft/Windows/Fonts',Path.home()/'Library/Fonts',Path('/Library/Fonts'),Path('/System/Library/Fonts'),Path.home()/'.local/share/fonts']:
   if root.is_dir():
    for p in root.rglob('*'):
     if p.suffix.lower() in ('.ttf','.otf','.ttc'):
      try:f,s=ImageFont.truetype(str(p),20).getname();add(f,s,str(p))
      except OSError:pass
 return out
def resolve(family,style,db):
 rows=db.get(family.casefold(),[]);wanted=style.casefold()
 if not rows:raise ValueError(f'not installed: {family}')
 exact=[p for s,p in rows if wanted in [x.strip().casefold() for x in s.split(',')]]
 if not exact:raise ValueError(f'no exact {style} face for {family}; inspect available styles')
 return sorted(exact)[0]
PAIRINGS={
 'luxury':[('Boska','Inter'),('Instrument Serif','Manrope'),('Bodoni Moda','DM Sans')],
 'tech':[('Space Grotesk','Geist'),('Satoshi','IBM Plex Mono'),('Unbounded','Inter')],
 'playful':[('Fredoka','Nunito Sans'),('Lilita One','Rubik'),('Comfortaa','Manrope')],
 'editorial':[('Bricolage Grotesque','Newsreader'),('Clash Display','DM Sans'),('Fraunces','Instrument Sans')],
 'impact':[('Archivo Black','Inter'),('Anton','Public Sans'),('League Spartan','Manrope')],
 'metal':[('Archivo Black','Inter'),('League Spartan','Manrope'),('Dela Gothic One','DM Sans')]
}
def pairs(mood,db):
 return [{'hero':a,'support':b,'both_installed':a.casefold() in db and b.casefold() in db} for a,b in PAIRINGS[mood]]
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True);l=sub.add_parser('list');l.add_argument('--role');l.add_argument('--installed',action='store_true');l.add_argument('--search');q=sub.add_parser('pairs');q.add_argument('mood',choices=PAIRINGS);r=sub.add_parser('resolve');r.add_argument('family');r.add_argument('--style',default='Regular');r.add_argument('--alias',default='hero');b=sub.add_parser('board');b.add_argument('output',type=Path);b.add_argument('--role');b.add_argument('--text',default='Make it matter.');b.add_argument('--style',default='Regular');a=p.parse_args();db=installed()
 if a.cmd=='pairs':print(json.dumps(pairs(a.mood,db),indent=2));return
 if a.cmd=='resolve':print(json.dumps({'fonts':{a.alias:resolve(a.family,a.style,db)}}));return
 rows=[x for x in catalog() if not a.role or x['role']==a.role];rows=[dict(x,installed=x['family'].casefold() in db) for x in rows]
 if a.cmd=='list':print(json.dumps([x for x in rows if (not a.installed or x['installed']) and (not a.search or a.search.casefold() in x['family'].casefold()+' '+x['role'].casefold())],indent=2));return
 matches=[]
 for row in rows:
  try:matches.append((row,resolve(row['family'],a.style,db)))
  except ValueError:pass
 if not matches:raise SystemExit('No matching local fonts: install authorized faces first.')
 im=Image.new('RGB',(920,len(matches)*108+35),'#11141a');d=ImageDraw.Draw(im);label=ImageFont.truetype(matches[0][1],16)
 for i,(row,path) in enumerate(matches):
  y=i*108+15;f=ImageFont.truetype(path,58);f=ImageFont.truetype(path,max(12,int(58*min(1,860/max(1,f.getlength(a.text))))));d.text((24,y),row['family']+' / '+a.style,font=label,fill='#9daec6');d.text((24,y+23),a.text,font=f,fill='#f0f2f6');d.line((24,y+98,896,y+98),fill='#353b45')
 a.output.parent.mkdir(parents=True,exist_ok=True);im.save(a.output)
if __name__=='__main__':main()
