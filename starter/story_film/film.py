#!/usr/bin/env python3
"""Configurable long-form motion editorial. No GUI. Local flite is scratch narration only."""
import argparse, json, math, subprocess, wave, re, os, hashlib
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor

KINDS={'files','scatter','type','assemble','reframe','detail','split','callback','end','fold'}
def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def lerp(a,b,x):return a+(b-a)*x
def run(a):subprocess.run(list(map(str,a)),check=True,stdout=subprocess.DEVNULL)
def validate(p,base):
    assert p['fps'] in (24,25,30,60) and 320<=p['width']<=2160 and p['height']%2==0 and p['width']%2==0 and abs(p['width']/p['height']-9/16)<.02,'Requires positive 9:16 even raster'
    assert 60<=p['bpm']<=180 and 5<=len(p['beats'])<=30
    for k in ('accent','foreground','background'):ImageColor.getrgb(p[k])
    assert (base/p['image']).is_file()
    def rect_ok(c):
        assert len(c)==4 and 0<=c[0]<c[2]<=1 and 0<=c[1]<c[3]<=1,'Invalid normalized crop'
    for c in p.get('crops',[]):rect_ok(c)
    for b in p['beats']:
        for c in b.get('crops',[]):rect_ok(c)
        for k in ('crop','left_crop','right_crop'):
            if k in b:rect_ok(b[k])
        assert b['kind'] in KINDS and 0.8<=b['min']<=12 and b['voice'].strip()
        if b['kind']=='type':assert 1<=len(b['lines'])<=5 and all(x.strip() for x in b['lines'])
        if b['kind']=='detail':
            x,y,z,w=b['crop'];assert 0<=x<z<=1 and 0<=y<w<=1
        if b['kind']=='files':assert 2<=len(b['items'])<=6
    return p

def audio(p,base,out,external=None,song=None):
    fps=p['fps'];sr=48000; chunks=[];meta=[];at=0
    # One clip per spoken phrase: exact phrase boundaries, no invented word alignment.
    for i,b in enumerate(p['beats']):
        target=out/f'voice-{i:02}.wav'
        if external:
            src=external/f'{i:02}.wav'; assert src.is_file(),src
            run(['ffmpeg','-v','error','-y','-i',src,'-ac','1','-ar',sr,target])
        else:
            txt=out/f'line-{i:02}.txt';txt.write_text(b['voice'])
            # FFmpeg's filter uses a relative file path, avoid escaped user script interpolation.
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f'flite=textfile={txt.name}:voice=slt','-ar',str(sr),'-ac','1',target.name],cwd=out,check=True)
        with wave.open(str(target)) as w: v=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768
        # Align to musical half-beat grid and leave breathing room. No stretching speech.
        grid=60/p['bpm']/2; dur=max(b['min'],len(v)/sr+.34);frames=math.ceil(math.ceil(dur/grid)*grid*fps-1e-8);n=round(frames*sr/fps)
        a=np.zeros(n,np.float32);start=round(.12*sr);a[start:start+len(v)]=v
        chunks.append(a);meta.append({'index':i,'start_frame':at,'frames':frames,'voice_start':at/fps+.12,'voice_end':at/fps+.12+len(v)/sr,'voice':b['voice']});at+=frames
    voice=np.concatenate(chunks); n=len(voice); t=np.arange(n,dtype=np.float64)/sr
    # Original restrained instrumental: sub pulse, soft harmonic bed, offbeat hat.
    beat=60/p['bpm']; ph=t%beat; env=np.exp(-ph*12);kick=.105*env*np.sin(2*np.pi*(48*ph+4*(1-np.exp(-ph*25))))
    rng=np.random.default_rng(240);noise=rng.normal(0,1,n);hat=(noise-np.roll(noise,1))*.009*np.exp(-((t+beat/2)%beat)*55)
    chord=np.array([110,130.8128,98,146.8324]);idx=(t/(beat*8)).astype(int)%4;freq=chord[idx];phase=np.cumsum(freq)/sr*2*np.pi
    pad=(np.sin(phase)+.35*np.sin(phase*1.5)+.22*np.sin(phase*2.0))*.025*(.7+.3*np.sin(t*.7))
    music=kick+hat+pad
    if song:
        raw=subprocess.check_output(["ffmpeg","-v","error","-i",str(song),"-f","f32le","-ac","1","-ar",str(sr),"-"]); source=np.frombuffer(raw,"<f4"); assert len(source)>=n,"Chosen music excerpt is shorter than film; choose a longer excerpt or explicit edit"; music=source[:n].copy(); music*=.055/max(.03,float(np.sqrt(np.mean(music**2))))
    for b in meta[1:]:
        start=round(b['start_frame']/fps*sr);m=min(n-start,round(.22*sr));q=np.arange(m)/sr;music[start:start+m]+=.055*np.exp(-q*19)*np.sin(2*np.pi*(150*q-160*q*q))
        a=max(0,start-round(.16*sr));m=start-a; q=np.arange(m)/max(1,m);music[a:start]+=.026*q*q*noise[a:start]
    # Smooth voice-aware ducking.
    from scipy.ndimage import maximum_filter1d,gaussian_filter1d
    block=480; sizes=math.ceil(n/block);r=np.sqrt(np.mean(np.pad(voice,(0,sizes*block-n)).reshape(-1,block)**2,axis=1));r=gaussian_filter1d(maximum_filter1d(r,17),4);duck=np.interp(np.arange(n),np.arange(sizes)*block,1-.55*np.minimum(1,r/.08))
    fade=np.clip((n-np.arange(n))/(sr*.7),0,1);mix=np.stack([voice*.88+music*duck*fade,voice*.88+music*duck*fade],axis=1);mix*=min(1,.88/max(.001,np.max(np.abs(mix))))
    for name,dat in [('mix',mix),('voice',voice),('music',music)]:
        with wave.open(str(out/f'{name}.wav'),'wb') as w:w.setnchannels(2 if dat.ndim==2 else 1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(dat,-1,1)*32767).astype('<i2').tobytes())
    (out/'timing.json').write_text(json.dumps(meta,indent=2));return meta

class Canvas:
    def __init__(self,p,base):
        self.p=p;self.W=p['width'];self.H=p['height'];self.s=self.W/720;self.ui=Image.open(base/p['image']).convert('RGB');self.bg=p['background'];self.fg=p['foreground'];self.ac=p['accent'];self.fonts={};self.crops={};self.cached={}
        self.faces={k:next((str(x) for x in candidates if x.is_file()),None) for k,candidates in {'bold':[Path('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')],'regular':[Path('/usr/share/fonts/opentype/inter/Inter-Regular.otf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path('C:/Windows/Fonts/arial.ttf')]}.items()}
        for k,v in p.get('fonts',{}).items():self.faces[k]=str((base/v).resolve())
        assert all(self.faces.values()),'Supply bold and regular fonts in fonts config'
    def font(self,size,weight='bold'):
        k=(max(8,round(size*self.s)),weight)
        if k not in self.fonts:self.fonts[k]=ImageFont.truetype(self.faces[weight],k[0])
        return self.fonts[k]
    def text(self,im,text,x,y,sz,color=None,weight='bold',maxw=636,anchor='lt',opacity=1):
        if not text or opacity<=0:return
        f=self.font(sz,weight);d=ImageDraw.Draw(im);length=d.textlength(text,font=f)
        if length>maxw*self.s:f=self.font(sz*maxw*self.s/length,weight)
        if opacity<1:
            rgb=np.array(ImageColor.getrgb(color or self.fg));bg=np.array(ImageColor.getrgb(self.bg));color=tuple(np.round(bg+(rgb-bg)*opacity).astype(int))
        d.text((round(x*self.s),round(y*self.s)),text,font=f,fill=color or self.fg,anchor=anchor)
    def rect(self,im,xy,fill=None,outline=None,width=1,r=0):
        ImageDraw.Draw(im).rounded_rectangle(tuple(round(v*self.s) for v in xy),radius=round(r*self.s),fill=fill,outline=outline,width=max(1,round(width*self.s)))
    def line(self,im,xy,fill,width=1):ImageDraw.Draw(im).line([tuple(round(v*self.s) for v in p) for p in xy],fill=fill,width=max(1,round(width*self.s)))
    def image(self,im,src,cx,cy,w,angle=0,alpha=1):
        size=(max(1,round(w*self.s)),max(1,round(w*self.s*src.height/src.width)));pic=src.resize(size,Image.Resampling.BICUBIC).convert('RGBA')
        if angle:pic=pic.rotate(angle,Image.Resampling.BICUBIC,expand=True)
        if alpha<1:pic.putalpha(pic.getchannel('A').point(lambda x:int(x*alpha)))
        im.paste(pic,(round(cx*self.s-pic.width/2),round(cy*self.s-pic.height/2)),pic)
    def crop(self,c):
        key=tuple(c)
        if key not in self.crops:self.crops[key]=self.ui.crop(tuple(round(v*(self.ui.width if i%2==0 else self.ui.height)) for i,v in enumerate(c)))
        return self.crops[key]
    def metal(self,im,text,cx,cy,sz,t,scale=1):
        # Animated studio-like bands on a text mask; deliberately 2.5D, not a geometric mesh.
        f=self.font(sz);box=f.getbbox(text);w=min(self.W,box[2]-box[0]+12);h=box[3]-box[1]+12
        key=(text,sz)
        if key not in self.cached:
            m=Image.new('L',(w,h));ImageDraw.Draw(m).text((6-box[0],6-box[1]),text,font=f,fill=255);self.cached[key]=m
        m=self.cached[key];yy,xx=np.ogrid[:m.height,:m.width];z=.9*yy/m.height+.25*xx/m.width
        band=.18+.5*np.exp(-((z-.31-.20*math.sin(2*t))/.08)**2)+.72*np.exp(-((z-.62+.14*math.sin(2*t))/.04)**2)+.20*np.exp(-((z-.92)/.10)**2)
        rgb=np.uint8(np.clip(band[...,None]*np.array([245,247,251]),0,255));pic=Image.fromarray(rgb,'RGB');pic.putalpha(m)
        if scale!=1:pic=pic.resize((max(1,round(pic.width*scale)),max(1,round(pic.height*scale))),Image.Resampling.BICUBIC)
        im.paste(pic,(round(cx*self.s-pic.width/2),round(cy*self.s-pic.height/2)),pic)
    def motif_crops(self,b):return [self.crop(x) for x in b.get('crops',self.p.get('crops',[[.045,.28,.505,.61],[.54,.28,.955,.61],[.035,.63,.5,.71],[.51,.63,.965,.71]]))]

    def frame(self,b,t,duration,idx):
        u=t/duration;h=self.H/self.s;W=720; bg=self.bg;fg=self.fg;ac=self.ac;k=b['kind'];inv=b.get('invert',False)
        im=Image.new('RGB',(self.W,self.H),ac if inv else bg); ink=bg if inv else fg
        if b.get('folio',False):
            self.text(im,self.p['name'],42,52,18,ink);self.text(im,f'{idx+1:02}  /  FIELD NOTES',678,54,13,ink,'regular',anchor='rt')
            self.line(im,[(42,87),(678,87)],'#46494a' if not inv else '#a0af61')
        if k=='files':
            for j,ln in enumerate(b.get('lines',['HOW DO YOU','SHOW YOUR','WORK?'])):
                a=ease((t-j*.13)/.3);self.text(im,ln,42,150+j*93+40*(1-a),98,ac if j==2 else fg,opacity=a)
            for j,name in enumerate(b['items']):
                a=ease((t-.23-j*.22)/.4); y=550+j*83+(1-a)*50
                if a>0:
                    self.rect(im,(42,y,678,y+67),'#191b1c','#434746',r=4);self.rect(im,(58,y+16,91,y+50),ac,r=3);self.text(im,str(j+1).zfill(2),75,y+33,12,bg,anchor='mm');self.text(im,name,112,y+18,29,maxw=500);self.text(im,'↗',643,y+19,28,ac,anchor='rt')
            # Cursor travels to last item, without pretending this is the product UI.
            if t>.7:
                x=lerp(620,430,ease((t-.7)/.9));y=lerp(455,805,ease((t-.7)/.9));self.line(im,[(x,y),(x+16,y+35),(x+22,y+22),(x+35,y+18),(x,y)],fg,2)
        elif k=='scatter':
            self.metal(im,b.get('number','04'),360,lerp(330,410,ease((u-.45)/.2)),330,t,lerp(1.05,.65,ease((u-.4)/.3))); self.text(im,b['title'],42,130,86,ac) if u>.55 else None
            cards=self.motif_crops(b)
            for j,card in enumerate(cards):
                a=ease((t-.25-j*.10)/.55);f=ease((u-.5)/.5);x=360+(j%2-.5)*lerp(70,310,a)+20*math.sin(u*3+j);y=760+(j//2-.5)*lerp(60,290,a)-f*42;self.image(im,card,x,y,lerp(160,330,a)*(1+.06*f),angle=lerp(0,[-11,10,7,-8][j%4],a),alpha=a)
            self.text(im,b.get('micro','01  /  02  /  03  /  04'),360,1070,29,fg,'regular',anchor='mt')
        elif k=='type':
            lines=b['lines'];start=h*.38-len(lines)*41
            for j,line in enumerate(lines):
                a=ease((t-j*.23)/.35); color=ink if inv or j!=b.get('highlight',-1) else ac
                if a>0:
                    # explicit moving clipping mask reveals whole glyph shape, no opacity-only.
                    layer=Image.new('RGB',im.size,ac if inv else bg); self.text(layer,line,42,start+j*110+40*(1-a),107,color,maxw=636)
                    box=(0,round((start+j*110)*self.s),self.W,round((start+j*110+115)*self.s));im.paste(layer.crop(box),(box[0],box[1]))
            self.text(im,b.get('micro',''),42,h-180,19,ink,'regular')
        elif k=='assemble':
            self.text(im,b['title'],42,142,110,ac)
            # Actual UI develops from aligned slats; final placement matches opening of next shot.
            x0=42;y0=385;wid=636;a=ease((t-.28)/(duration*.65)); src=self.ui.resize((round(wid*self.s),round(wid*self.s*self.ui.height/self.ui.width)),Image.Resampling.LANCZOS)
            for j in range(12):
                lo=j*src.width//12;hi=(j+1)*src.width//12; stripe=src.crop((lo,0,hi,src.height));f=ease((t-.1-j*.045)/(duration*.58));x=x0*self.s+lo+(1-f)*(j-5.5)*25*self.s;y=y0*self.s+(1-f)*math.sin(j*1.6)*155*self.s;im.paste(stripe,(round(x),round(y)))
            self.text(im,b.get('micro',''),42,1010,26,fg,'regular')
        elif k=='fold':
            # Pre-rendered actual 3D mesh clip. This is generated from the supplied screenshot,
            # not a downloaded reference asset. Match output dimensions and timing.
            import cv2
            cap=self.cached.get(('mesh',idx));assert cap is not None,'Missing mesh shot'
            frame=round(t*self.p['fps']);prev=self.cached.get(('mesh_index',idx),-1)
            if frame!=prev+1:cap.set(cv2.CAP_PROP_POS_FRAMES,frame)
            ok,img=cap.read();assert ok,'Mesh shot decode failed';self.cached[('mesh_index',idx)]=frame
            im=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)).resize((self.W,self.H),Image.Resampling.LANCZOS)
            # Deliberately no headline during the optical transition. Typography arrives at the landing.
            a=ease((u-.65)/.2)
            self.text(im,b['title'],42,130,95,fg,opacity=a)
        elif k=='reframe':
            a=ease(t/(duration*.7));self.image(im,self.ui,360,lerp(690,675,a),lerp(1050,636,a));
            self.text(im,b['title'],42,114,111,fg);self.text(im,b.get('micro',''),45,238,28,ac,'regular');self.text(im,self.p['domain'],42,1120,19,fg,'regular')
        elif k=='detail':
            a=ease(t/(duration*.65)); crop=self.crop(b['crop']);
            # full frame crop to readable detail then settles in contextual width.
            if b.get('detail_mode')=='stack':
                for j,cr in enumerate(b['crops']):
                    f=ease((t-.25-j*.4)/.55); self.image(im,self.crop(cr),360,540+j*210+90*(1-f),lerp(750,636,f),alpha=f)
            else:
                self.image(im,crop,lerp(390,360,a),lerp(560,625,a) if b.get('layout')=='bottom' else lerp(680,660,a),lerp(1240,710,a));
            if b.get('layout')=='bottom':
                self.text(im,b['title'],42,925,86,fg);self.text(im,b['second'],42,1014,78,ac)
            else:
                self.text(im,b['title'],42,150,108,fg);self.text(im,b['second'],42,265,103,ac);self.line(im,[(42,405),(678,405)],'#555955');
            if b.get('layout')!='bottom':
                self.text(im,'PRODUCT DETAIL',42,1090,19,fg,'regular');self.text(im,f'{idx+1:02}',678,1090,19,ac,anchor='rt')
        elif k=='split':
            a=ease(t/.7);im.paste(ImageColor.getrgb(ac),(0,0,self.W,round(self.H*.48)));self.text(im,b['title'],42,125,100,bg);self.image(im,self.crop(b.get('left_crop',self.p.get('crops',[[.045,.28,.505,.61],[.54,.28,.955,.61]])[0])),lerp(520,360,a),400,620)
            self.text(im,b['second'],42,660,87,fg);self.image(im,self.crop(b.get('right_crop',self.p.get('crops',[[.045,.28,.505,.61],[.54,.28,.955,.61]])[1])),lerp(195,360,a),930,620)
        elif k=='callback':
            a=ease((t-.35)/(duration*.56));self.metal(im,b.get('number','04') if a<.7 else b.get('result_number','01'),360,235,260,t,1-.12*a);
            # Shared four rectangles contract into a single aligned object.
            crops=self.motif_crops(b)
            for j,c in enumerate(crops):
                x=lerp(170+380*(j%2),360,a);y=lerp(530+240*(j//2),660,a);self.image(im,c,x,y,lerp(285,636,a),alpha=1 if j==3 else 1-a)
            if a>.45:self.image(im,self.ui,360,660,636,alpha=ease((a-.45)/.55))
            self.text(im,b['title'],42,1030,96,ac)
        elif k=='end':
            # Leave the CTA fixed for the final 1.5 seconds.
            a=ease(t/.5);self.text(im,self.p['name'],360,445,175,fg,anchor='mt',opacity=a);self.text(im,b['title'],360,675,64,ac,anchor='mt');self.line(im,[(210,780),(510,780)],'#777e64');self.text(im,self.p['domain'],360,823,22,fg,'regular',anchor='mt');self.text(im,'FICTIONAL PRODUCT STUDY' if self.p.get('fictional') else b.get('footer',''),360,1090,18,fg,'regular',anchor='mt')
        return im

def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--voice-dir',type=Path);ap.add_argument('--size',type=int);ap.add_argument('--music',type=Path,help='Authorized local music excerpt, must cover film');ap.add_argument('--stills-only',action='store_true');args=ap.parse_args();base=args.plan.resolve().parent;p=validate(json.loads(args.plan.read_text()),base);out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if args.size:p['height']=round(p['height']/p['width']*args.size/2)*2;p['width']=args.size
    meta=audio(p,base,out,args.voice_dir.resolve() if args.voice_dir else None,args.music.resolve() if args.music else None);c=Canvas(p,base); fps=p['fps'];
    for i,(b,m) in enumerate(zip(p['beats'],meta)):
        if b['kind']!='fold':continue
        import cv2
        target=out/f'mesh-{i:02}.mp4'
        spec={'width':min(540,p['width']),'height':round(min(540,p['width'])*p['height']/p['width']/2)*2,'fps':fps,'shots':[{'kind':'sheet','material':'texture','src':str((base/p['image']).resolve()),'crop':[0,0,1,1],'frames':m['frames'],'resolution':75,'quality':.78,'phase':[[0,0],[1,1]],'bend':[[0,2.0],[.7,.25],[1,0]],'twist':[[0,1.8],[.75,.12],[1,0]],'yaw':[[0,.9],[1,0]],'pitch':[[0,.3],[1,0]],'roll':[[0,-.25],[1,0]],'zoom':[[0,1.65],[1,1.0]],'bg':p['background'],'samples':1,**b.get('mesh',{})}]}
        config=out/f'mesh-{i:02}.json';encoded=json.dumps(spec,indent=2)
        # Source bytes and renderer version participate in the cache key.
        digest=hashlib.sha256((base/p['image']).read_bytes()+ (Path(__file__).resolve().parents[1]/'mesh_motion'/'render.py').read_bytes()+encoded.encode()).hexdigest()
        keyfile=out/f'mesh-{i:02}.sha256'
        if not (target.is_file() and config.is_file() and config.read_text()==encoded and keyfile.is_file() and keyfile.read_text()==digest):
            config.write_text(encoded);run(['python',Path(__file__).resolve().parents[1]/'mesh_motion'/'render.py',config,target,'--font',c.faces['bold']]);keyfile.write_text(digest)
        c.cached[('mesh',i)]=cv2.VideoCapture(str(target))

    sheet=Image.new('RGB',(5*144,math.ceil(len(meta)/5)*276),'#242424');sd=ImageDraw.Draw(sheet)
    for i,(b,m) in enumerate(zip(p['beats'],meta)):
        im=c.frame(b,m['frames']/fps*.66,m['frames']/fps,i);im.thumbnail((144,256));x=(i%5)*144;y=(i//5)*276;sheet.paste(im,(x,y));sd.text((x+4,y+258),f'{m["start_frame"]/fps:.1f}s {b["kind"]}',fill='white')
    sheet.save(out/'contact-sheet.jpg',quality=93)
    if args.stills_only:return
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{c.W}x{c.H}','-r',str(fps),'-i','-','-i',str(out/'mix.wav'),'-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(out/'film.mp4')],stdin=subprocess.PIPE)
    for i,(b,m) in enumerate(zip(p['beats'],meta)):
        for f in range(m['frames']):proc.stdin.write(c.frame(b,f/fps,m['frames']/fps,i).tobytes())
        print(f'Rendered {i+1}/{len(meta)}: {b["kind"]}',flush=True)
    proc.stdin.close();assert proc.wait()==0
    lines=[]
    def fmt(s):ms=round(s*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    for i,m in enumerate(meta):lines.extend([str(i+1),f'{fmt(m["voice_start"])} --> {fmt(m["voice_end"])}',m['voice'],''])
    (out/'captions.srt').write_text('\n'.join(lines));(out/'script.txt').write_text('\n'.join(x['voice'] for x in meta));print('COMPLETE',sum(x['frames'] for x in meta)/fps,flush=True)
if __name__=='__main__':main()
