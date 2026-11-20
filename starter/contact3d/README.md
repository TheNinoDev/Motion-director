# V34 presets

Copy `examples/jelly-v34.json` or use `preset: jelly`, `jelly_soft`, `jelly_firm`, `rubber`, `silicone`, `foam`, `heavy` on a body. Defaults live in `presets.py`; explicit properties override them. Secondary damped recovery begins after the actual wall contact ends and is scaled by impact speed. See guide 70. Presets define behavior, not optical material; the contact preview uses studio-colored ellipsoids, not translucent fluid. No new gravity or pair collision solver.

# Contact3D — V33

Run `python starter/contact3d/render.py examples/contact-v33.json work/contact`.
The example is a 5-second 1920×1080/60fps slow-motion laboratory study, not an ad.
Each body has its own initial position `[x,y,z]`, velocity `[vx,vy,vz]`, radius, mass, stiffness, damping and color. Negative vx approaches wall x=0; y,z are tangential; angles are measured from the wall normal. `time_scale` changes playback only. The solver integrates a unilateral spring-damper with a fixed 960 Hz timestep. Compression modifies ellipsoid axes, preserving volume until its minimum normal-radius safety limit. Contact events are derived from the simulation; no authored contact times. Tangential velocity is unchanged. The renderer uses true perspective rays, analytic ellipsoid intersections, a finite-looking slab, shadow approximations and studio highlights. Physics wall is an infinite plane. No gravity, floor contact, inter-body contact, friction, tearing or local mass-spring mesh simulation. Choose nonintersecting paths and keep impacts within the visible slab. The volume shape has a tangent point, not a physically solved flattened contact patch.

`master.mp4` is lossless RGB H.264 (CRF 0; no chroma subsampling). `contacts.json` holds simulation times. `compositor-layers.json` holds reusable keyframed ellipsoid layers for a side-on orthographic view: x maps to horizontal screen normal, z to vertical, y becomes depth. Add the matching visible wall at x=160 design px; 100 design pixels per unit, 640 center y. The exported layers do not recreate the perspective camera. They can be used alongside ordinary compositor text, masks, parent groups and other objects. Do not also add the V32 impulse preset unless deliberately combining independent secondary deformation. Do not use a sphere SDF for nonuniform sizing; use an ellipsoid.

Export a compatible upload copy separately from the lossless master:
`ffmpeg -i work/contact/master.mp4 -c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p -movflags +faststart work/contact/upload.mp4`
For raw uncompressed image data use PNG frame export or raw RGB24; do not call a compressed lossless stream uncompressed. This is a technical silent study.
