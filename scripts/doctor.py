#!/usr/bin/env python3
"""Report locally discoverable tools; presence is not a successful integration test."""
import importlib.util,json,shutil,sys
print(json.dumps({'python':sys.version,'executables':{k:shutil.which(k) for k in ['ffmpeg','ffprobe','node','npm','blender','espeak','espeak-ng','piper','whisper','whisper-cli','hyperframes']},'python_modules':{k:importlib.util.find_spec(k) is not None for k in ['PIL','cv2','numpy','playwright','whisper','faster_whisper','numba']},'warning':'Discoverability only. Verify versions, permissions, available voices and actual render.'},indent=2))
