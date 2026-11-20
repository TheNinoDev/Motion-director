# V31 — solid optical objects

Glass is a material, not an obligatory effect. `glass_object` and `object3d` use the same closed-volume renderer. One persistent timeline ID can change thickness, orientation, shape and every numerical material parameter while interacting optically with actual underlying layers. Use the existing `lens` only for deliberate flat magnifiers; do not substitute lenses for solid objects. For imported triangular meshes use existing `mesh`; this V31 volume renderer does not accept OBJ glass, text extrusion, or arbitrary mesh glass. No new package beyond the previous Numba dependency.

```json
{"id":"crystal","kind":"glass_object","active":[0,4],"x":[[0,200],[4,520,"sine"]],"y":640,"w":280,"h":250,"depth":190,"geometry":"rounded_box","material":"clear","pitch":18,"yaw":[[0,-35],[4,45,"sine"]],"rotate":[[0,12],[4,-12,"sine"]],"phase3d":[[0,0],[2,.75,"sine"],[4,0,"sine"]],"ior":1.45,"roughness":0.08,"quality":0.65}
```

Shapes: box, rounded_box, sphere, ellipsoid, capsule, cylinder, torus, diamond, cone. Sphere uses smallest local radius; use ellipsoid for stretchable spheres. Torus is an elliptical ring with independently set tube depth. Capsule is oriented along local Y. Box/rounded_box can morph toward ellipsoid using phase3d. `twist3d` rotates cross sections as function of Y, `bend3d` bends their centerline. Large deformations can exceed conservative trace estimates; review silhouettes. These are implicit solid surfaces, not billboard textures.

Materials: clear, frosted, smoked, prism, acrylic, chrome, ceramic. The last two are opaque; use `object3d` for either transparent or opaque materials. `material` is static but animatable scalar overrides permit gradual material changes. `color` overrides preset tint (hex). No need to import a pre-rendered graphic. `w,h` are local diameter in design px, `depth` is local thickness in design px. `size_x,size_y,scale_z` change physical dimensions before projection; inherited `scale,scale_x,scale_y` are 2D layout scaling afterward. `pitch,yaw,rotate` use degrees; `light` radians. `x,y`, parent group, opacity, animated masks/reveal, and shadow reuse compositor controls. Render order is bottom to top; draw UI or typography before the optical object, foreground text afterward. Multiple objects can be grouped or individually timed and moved. Depth ordering between independent objects is explicit layer order, not global Z sorting. One object samples the prior composite, not a shared 3D light transport scene. Shadow is a screen-space soft silhouette, clipped to local bounds. No volume track matte or alternate blend modes; use masks or the existing 2D layer tools for complex compositing. Whole-composite time sampling supports volume motion blur with `--samples 2` and `shutter_windows`; per-layer projected blur is not implemented for volume.

Numerical controls (track or scalar): depth 1–1500, size_x/size_y/scale_z .05–5, bevel3d 0–.45 normalized local units, phase3d 0–1, twist3d -2–2, bend3d -.8–.8, ior 1.01–2.3, roughness 0–1, transmission 0–1, absorption 0–5, dispersion 0–.08, background_gap 0–3, reflection 0–2. Static quality .2–1 (internal ROI scale); prefer .6 for preview and .8–1 for detail. Shape and material preset static. Normal physically plausible glass IOR around 1.45–1.55; use low dispersion, strong silhouette, soft light, and controlled background gap before increasing saturation. Don't mistake the total-internal-reflection fallback or screen-plane sampling for path tracing. A glass body has two traced optical interfaces, Fresnel approximation, approximate absorption proportional to path length, and analytic studio reflection. Frost is blurred background sampling, not physically rough transport. There is no recursive inter-object optics, true caustics or scene-wide depth.

## Reproduce
```
python starter/composite_film/volume_compile.py --showcase work/objects.json
python starter/composite_film/compositor.py work/objects.json work/objects --size 540
python starter/composite_film/demo_compile.py work/base
python starter/composite_film/volume_compile.py work/base/timing.json work/v31/plan.json
python starter/composite_film/mix_picture.py work/base/mix.wav work/v31/plan.json work/v31/mix.wav
python starter/composite_film/compositor.py work/v31/plan.json work/v31/render --size 720 --audio work/v31/mix.wav
python -m unittest discover -s tests -p 'test_v31.py'
```
The showcase demonstrates API capabilities, not an advertising template. FORM is a targeted revision, not a generic generator. For different projects author independent timelines based on the product.
