#!/usr/bin/env python3
"""Deterministic, data-driven 2D compositor. Python/Pillow + FFmpeg, no GUI."""
import argparse, json, math, pathlib, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont, ImageOps
P=pathlib.Path
EASING={'linear':lambda x:x,'out':lambda x:1-(1-x)**3,'inout':lambda x:4*x*x*x if x<.5 else 1-(-2*x+2)**3/2,'hold':lambda x:0}
DEFAULT={'x':0,'y':0,'scale':1,'opacity':1,'rotation':0,'reveal':1}
def require(v,msg):
    if not v: raise ValueError(msg)
def validate(doc, root):
    w,h,fps=(doc[k] for k in ('width','height','fps'))
    require(all(isinstance(k,int) and k>0 for k in (w,h,fps)), 'positive integer dimensions/fps required')
    require(w%2==h%2==0,'even sizes required for yuv420p')
    require(bool(doc['shots']),'no shots')
    for s in doc['shots']:
        n=s['frames']; require(isinstance(n,int) and n>0,'positive integer shot length')
        for l in s['layers']:
            require(l['type'] in ('image','text','rect','cursor'),'unknown layer')
            if l['type']=='image': require((root/l['src']).is_file(),f"missing asset {l['src']}")
            if l['type'] in ('image','rect'): require(all(isinstance(l[k],int) and l[k]>0 for k in ('w','h')),'positive layer size')
            if l['type']=='text': require(bool(l['text']) and l.get('size',48)>0,'empty text or bad font size')
            for prop,keys in l.get('animate',{}).items():
                require(prop in DEFAULT,f'unknown property {prop}'); require(bool(keys),'missing keys')
                times=[k[0] for k in keys]; require(times==sorted(set(times)) and all(isinstance(t,int) and 0<=t<n for t in times),'invalid keyframe times')
                for k in keys:
                    require(len(k) in (2,3) and isinstance(k[1],(int,float)) and math.isfinite(k[1]),'bad keyframe value')
                    require(len(k)==2 or k[2] in EASING,'bad easing')
                    if prop=='scale': require(0<k[1]<=8,'scale outside range')
                    if prop in ('opacity','reveal'): require(0<=k[1]<=1,'opacity/reveal outside range')
    return sum(s['frames'] for s in doc['shots'])
def property_at(l,p,f):
    keys=l.get('animate',{}).get(p,[])
    if not keys:return l.get(p,DEFAULT[p])
    if f<=keys[0][0]:return keys[0][1]
    for a,b in zip(keys,keys[1:]):
        if f<b[0]:
            q=EASING[b[2] if len(b)>2 else 'linear']((f-a[0])/(b[0]-a[0]));return a[1]+(b[1]-a[1])*q
    return keys[-1][1]
def make_layer(l,root,font):
    k=l['type']
    if k=='image':
        im=ImageOps.fit(Image.open(root/l['src']).convert('RGBA'),(l['w'],l['h']),Image.Resampling.LANCZOS,centering=tuple(l.get('crop_center',[.5,.5])))
        if l.get('radius',0):
            m=Image.new('L',im.size);ImageDraw.Draw(m).rounded_rectangle((0,0,im.width-1,im.height-1),l['radius'],fill=255); im.putalpha(m)
        return im
    if k=='rect':
        im=Image.new('RGBA',(l['w'],l['h']));ImageDraw.Draw(im).rounded_rectangle((0,0,im.width-1,im.height-1),l.get('radius',0),fill=l.get('color','#ffffff'),outline=l.get('outline'),width=l.get('stroke',1));return im
    if k=='cursor':
        im=Image.new('RGBA',(38,48)); ImageDraw.Draw(im).polygon([(3,2),(3,35),(13,26),(21,44),(29,40),(21,24),(35,24)],fill='white',outline='black',width=2);return im
    ft=ImageFont.truetype(str(root/l['font']) if 'font' in l else font,l.get('size',48)); box=ImageDraw.Draw(Image.new('RGB',(1,1))).multiline_textbbox((0,0),l['text'],font=ft,spacing=l.get('spacing',4));im=Image.new('RGBA',(max(1,box[2]-box[0]+4),max(1,box[3]-box[1]+4)));ImageDraw.Draw(im).multiline_text((2-box[0],2-box[1]),l['text'],font=ft,fill=l.get('color','white'),spacing=l.get('spacing',4));return im
def render_frame(s,cache,w,h,f):
    im=Image.new('RGBA',(w,h),s.get('background','#101014'))
    for l,base in zip(s['layers'],cache):
        a={p:property_at(l,p,f) for p in DEFAULT};
        if a['opacity']<=0 or a['reveal']<=0:continue
        layer=base.copy()
        if a['reveal']<1:
            edge=round(layer.width*a['reveal']); layer.paste((0,0,0,0),(edge,0,layer.width,layer.height))
        if a['scale']!=1:layer=layer.resize((max(1,round(layer.width*a['scale'])),max(1,round(layer.height*a['scale']))),Image.Resampling.BICUBIC)
        if a['rotation']:layer=layer.rotate(-a['rotation'],Image.Resampling.BICUBIC,expand=True)
        if a['opacity']!=1:layer.putalpha(layer.getchannel('A').point(lambda q:round(q*a['opacity'])))
        # center anchoring maintains match during zoom; negative coords are intentionally clipped.
        x=round(a['x']-layer.width/2);y=round(a['y']-layer.height/2);im.alpha_composite(layer,(x,y))
    return im.convert('RGB')
def main():
    p=argparse.ArgumentParser();p.add_argument('plan',type=P);p.add_argument('output',type=P);p.add_argument('--font',default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf');p.add_argument('--frame',type=int);p.add_argument('--audio',type=P);a=p.parse_args();doc=json.loads(a.plan.read_text());root=a.plan.resolve().parent;n=validate(doc,root);w,h,fps=(doc[k] for k in ('width','height','fps'));a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.frame is not None:require(0<=a.frame<n,'frame out of range')
    if a.audio:
        require(a.audio.is_file(),'audio missing'); duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(a.audio)]));require(abs(duration-n/fps)<=max(.1,2/fps),'audio and timeline durations mismatch: explicitly align/pad mix first')
    proc=None
    if a.frame is None:
        cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-']
        if a.audio:cmd+=['-i',str(a.audio),'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k']
        cmd+=['-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','fast','-movflags','+faststart',str(a.output)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    offset=0
    try:
        for s in doc['shots']:
            if a.frame is not None and not offset<=a.frame<offset+s['frames']:offset+=s['frames'];continue
            cache=[make_layer(l,root,a.font) for l in s['layers']]
            if a.frame is not None:render_frame(s,cache,w,h,a.frame-offset).save(a.output);return
            for f in range(s['frames']):proc.stdin.write(render_frame(s,cache,w,h,f).tobytes())
            offset+=s['frames']
    finally:
        if proc:
            proc.stdin.close();require(proc.wait()==0,'ffmpeg failed')
    print(f'{n} frames, {n/fps:.3f}s, {a.output}')
if __name__=='__main__':main()
