"""Run independently: NUMBA_ENABLE_CUDASIM=1 python tests/gpu_parity_v35.py
On real CUDA run without simulator. Non-square grids exercise partial blocks.
"""
import sys,json,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'starter/contact3d'),str(ROOT/'starter/composite_film')]
from render_backend import Backend
import volume,text3d
from render import camera,raster
from compositor import Engine,validate
from numba import config

class Parity(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gpu=Backend('cuda',allow_simulator=bool(config.ENABLE_CUDASIM))
 def test_volume(self):
  X,Y=np.meshgrid(np.linspace(-1.2,1.2,17,dtype=np.float32),np.linspace(-1.1,1.1,9,dtype=np.float32))
  for k in range(9):
   args=(X,Y,k,.75,.6,.42,.12,.2,.35,.1,.05,.2,1.45,.12,.3,.45)
   a=volume.maps(*args);b=self.gpu.run('volume',volume.maps,*args);np.testing.assert_allclose(b,a,atol=.003,rtol=.003);self.assertGreater(b[:,:,5].sum(),0)
 def test_type(self):
  X,Y=np.meshgrid(np.linspace(-1,1,17,dtype=np.float32),np.linspace(-.8,.8,9,dtype=np.float32));y,x=np.mgrid[-20:21,-20:21];atlas=(np.sqrt(x*x+y*y)-13).astype(np.float32)
  for material in range(5):
   args=(X,Y,atlas,.05,.3,.08,.2,.4,1.0,.9,1.1,.02,.05,1.2,.4,.2,material,np.ones(3,np.float32))
   a=text3d.render(*args);b=self.gpu.run('text',text3d.render,*args);np.testing.assert_allclose(a,b,atol=.1,rtol=.001);self.assertGreater(b[:,:,3].sum(),0)
 def test_contact(self):
  o,r=camera(37,23);balls=np.array([[1.5,1.0,1.,.55,.67,.67],[2.4,1.1,-1.,.61,.61,.61]],np.float64);colors=np.array([[.2,.4,.8],[.8,.3,.1]],np.float32);args=(o,r,balls,colors);a=raster(*args);b=self.gpu.run('contact',raster,*args);np.testing.assert_allclose(a,b,atol=1);self.assertGreater(b.std(),5)
 def test_compositor(self):
  p={'width':36,'height':64,'fps':30,'duration':1,'layers':[{'id':'g','kind':'glass_object','active':[0,1],'w':300,'h':300,'geometry':'sphere','quality':.5,'softbody':{'preset':'jelly','events':[{'time':0,'strength':.5}]}},{'id':'t','kind':'text3d','active':[0,1],'text':'O','size':160,'x':360,'y':400,'quality':.5,'atlas_resolution':320}]};validate(p,ROOT);a=Engine(p,ROOT,Backend('cpu')).frame(.1);b=Engine(p,ROOT,self.gpu).frame(.1);np.testing.assert_allclose(a.astype(float),b.astype(float),atol=2)
if __name__=='__main__':unittest.main(verbosity=2)
