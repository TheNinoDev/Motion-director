#!/usr/bin/env python3
"""Inspect the real CUDA environment; optionally launch the renderer parity suite."""
import argparse,json,sys,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'starter/composite_film'))
from render_backend import probe

def main():
 p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');p.add_argument('--simulate',action='store_true');a=p.parse_args();info=probe();print(json.dumps(info,indent=2),flush=True)
 if a.simulate or a.test:
  if a.test and not a.simulate and not info['available']:raise SystemExit('No real CUDA device available. Use --simulate to test logic, not performance.')
  env=os.environ.copy();env['NUMBA_ENABLE_CUDASIM']='1' if a.simulate else '0';raise SystemExit(subprocess.call([sys.executable,str(ROOT/'tests/gpu_parity_v35.py')],env=env))
if __name__=='__main__':main()
