"""Optional CUDA rendering with strict selection, bounded transfers and honest telemetry.
CPU remains the reference. The CUDA simulator is opt-in for tests only.
"""
import os, math, warnings, json
from collections import Counter
from pathlib import Path
import numpy as np

SUPPORTED=('volume','text','contact')
def probe():
    result={'available':False,'simulator':False,'devices':[],'reason':None}
    try:
        from numba import cuda, config
        result['simulator']=bool(config.ENABLE_CUDASIM)
        if result['simulator']:
            result['reason']='CUDA simulator is not physical GPU hardware';return result
        if not cuda.is_available():
            result['reason']='CUDA driver/device unavailable';return result
        for i in range(len(cuda.gpus)):
            with cuda.gpus[i]:
                d=cuda.get_current_device();name=d.name
                result['devices'].append({'index':i,'name':name.decode() if isinstance(name,bytes) else str(name),'compute_capability':list(d.compute_capability)})
        result['available']=bool(result['devices'])
    except Exception as exc:result['reason']=f'{type(exc).__name__}: {exc}'
    return result

class Backend:
    def __init__(self,mode='auto',device=0,tile_mib=64,allow_simulator=False):
        if mode not in ('auto','cpu','cuda'):raise ValueError('backend must be auto, cpu or cuda')
        if device<0 or not 4<=tile_mib<=512:raise ValueError('invalid device or tile budget (4–512 MiB)')
        self.mode=mode;self.device=device;self.tile_mib=tile_mib;self.counts=Counter();self.failures={};self.cuda=None;self.simulator=False;self.selected='cpu';self.reason=None
        if mode=='cpu':return
        try:
            from numba import cuda, config
            self.simulator=bool(config.ENABLE_CUDASIM)
            if self.simulator and not allow_simulator:raise RuntimeError('simulator is for tests only, not GPU rendering')
            if not cuda.is_available():raise RuntimeError('CUDA driver/device unavailable')
            cuda.select_device(device);self.cuda=cuda;self.selected='cuda-simulator' if self.simulator else 'cuda'
        except Exception as exc:
            self.reason=f'{type(exc).__name__}: {exc}'
            if mode=='cuda':raise RuntimeError('CUDA requested but unavailable: '+self.reason) from exc
            warnings.warn('Auto backend: CPU fallback: '+self.reason,RuntimeWarning)
    def report(self):
        return dict(requested=self.mode,selected=self.selected,device=self.device if self.cuda else None,simulator=self.simulator,reason=self.reason,kernel_calls=dict(self.counts),fallbacks=self.failures,supported=list(SUPPORTED),cpu_only=['2D compositing','physics simulation','mesh rasterizer','other legacy engines','video encoding'])
    def save(self,path):Path(path).write_text(json.dumps(self.report(),indent=2),encoding='utf-8')
    def run(self,kind,cpu,*args):
        if kind not in SUPPORTED:raise ValueError(kind)
        if self.cuda is not None and kind not in self.failures:
            try:
                result=self._gpu(kind,args);self.counts[f'{kind}:{self.selected}']+=1;return result
            except Exception as exc:
                if self.mode=='cuda':raise RuntimeError(f'CUDA {kind} render failed: {exc}') from exc
                self.failures[kind]=f'{type(exc).__name__}: {exc}';warnings.warn(f'{kind} CUDA failed; CPU fallback: {exc}',RuntimeWarning)
        result=cpu(*args);self.counts[f'{kind}:cpu']+=1;return result
    def _gpu(self,kind,args):
        import cuda_kernels as k
        cu=self.cuda;block=(16,8)
        def upload(a):return cu.to_device(np.ascontiguousarray(a))
        def launch(kernel,shape,dt,params):
            h,w,c=shape;out=cu.device_array(shape,dtype=dt)
            kernel[((w+block[0]-1)//block[0],(h+block[1]-1)//block[1]),block](*params,out)
            return out.copy_to_host()
        if kind=='contact':
            o,rays,balls,colors=args;h,w,_=rays.shape
            # Full-frame rays retain correct background coordinates. Explicit memory guard.
            if not self.simulator:
                free,_=cu.current_context().get_memory_info()
                if rays.nbytes+h*w*3+balls.nbytes+colors.nbytes>free*.65:raise MemoryError('contact render exceeds GPU memory budget; reduce AA or use CPU')
            return launch(k.contact_kernel,(h,w,3),np.uint8,[upload(a) for a in args])
        X,Y,*rest=args;h,w=X.shape;channels=6 if kind=='volume' else 4
        # Upload immutable parameters once per render call, split pixel grids into row tiles.
        # Tile size bounds transfers, not all driver/compiler allocations.
        bytes_per_row=w*(X.dtype.itemsize+Y.dtype.itemsize+channels*4)
        budget=self.tile_mib*1024**2
        if not self.simulator:
            free,_=cu.current_context().get_memory_info();fixed=sum(a.nbytes for a in rest if isinstance(a,np.ndarray));budget=min(budget,int(free*.55)-fixed)
        if budget<bytes_per_row:raise MemoryError('insufficient GPU memory for one tile row')
        rows=max(1,min(h,budget//bytes_per_row));fixed=[upload(a) if isinstance(a,np.ndarray) else a for a in rest];out=np.empty((h,w,channels),np.float32)
        kernel=k.volume_kernel if kind=='volume' else k.text_kernel
        for start in range(0,h,rows):
            end=min(h,start+rows);out[start:end]=launch(kernel,(end-start,w,channels),np.float32,[upload(X[start:end]),upload(Y[start:end]),*fixed])
        return out
