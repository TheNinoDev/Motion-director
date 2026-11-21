# 142 — Sound is an edit layer, not a last-minute decoration (v67)

## Evidence and limits

The user compared the 24.6-second `RobloxLARP-Script-Protection(2).mp4` against Claude's `robloxlarp-script-protection.mp4` and asks for **more and better SFX**, not only more events. The two renders substantially share underlying audio (a simple sample-aligned mono waveform comparison was about 0.91 correlated, without source separation). This proves common sound material, **not** how many SFX either editor used; source speech, music, processing, limiting and distinct cues are inseparable in a mastered soundtrack. Do not claim to have counted isolated SFX from mixed MP4s. The uploaded filmstrips do visibly show missed opportunities for picture-driven micro-events. Audit with eyes *and ears*, ideally with the original individual voice, music and effects stems.

## The director owns a soundtrack storyboard

Before rendering a major scene, assign **visual event → perceptual material → sonic gesture → role in the mix**. Include the entry/exit or sound prelap to the next scene. Examples (not copyable timing presets):

- A code card is grabbed: brief textured *friction* while it starts moving; one *tear/snap* as it loses its owner; short low *impact* on the landing. Avoid a whoosh simply because the card moves.
- A code fragment breaks into tiles: sparse high-frequency *ticks/rattle* in a short accelerating cascade, then one restrained *click* or *ping* on resolution. Do not lay one homogeneous static swoosh under the entire three seconds.
- A key is selected: a deliberate UI *click* on contact, very short tonal *confirmation* only if the state actually changes, with lower-level movement/focus SFX beneath as justified.
- A shape takes over the next shot: an approaching air sweep can begin **before** the cut, carry through it, then land with a different material impact **after** the cut. The effect's tail crosses the scene boundary. Do not use the same loud sweep on every seam.
- Endcard: optional short musical landing and a quiet tactile detail; no arbitrary crescendo that masks the product name or narration.

**Mandatory for a film with supplied narration and music:** read the actual supplied files, don't ask for them again; establish real event times from script/voice/music; score each important visual action and designed scene bridge for whether SFX would help, what precise kind, and whether already-covered music transients make additional SFX unnecessary. When user specifically wants stronger SFX, include a richer *intentional* sound vocabulary; never pad the track with meaningless repeated whooshes.

## Choose a sound family based on a physical or graphic relationship

| Visual event | Material implication | Suitable audio family | What to avoid |
|---|---|---|---|
| Moving or throwing sheet | paper, air, surface | `paper`, `brush`, soft `whoosh` | enormous sub hit for tiny card |
| Theft, rip, sharp state change | fracture/contact | `snap`, `impact`, `drop` | serene chime that contradicts danger |
| Rapid code remap | granular digital detail | `tick`, `glitch`, `rattle` | continuous loud static |
| Lens/light/clean reveal | smooth electronic shimmer | `glint`, `sweep`, `chime` | harsh gunshot-like transient |
| Button/key contact | tactile button/toggle | `click`, `tick`, quiet `pulse` | high-volume impact for all UI |
| Major transfer/scene takeover | directional movement and arrival | layered `whoosh`/`sweep` + distinct destination sound | random generic wipe whoosh |
| Closure/success | satisfying resolution | `chime`, `glint` with restrained tail | huge riser beneath spoken brand name |

**Two layers are often better than ten effects:** a low, soft body gives weight; a controlled brighter transient gives tactile definition. Make these layers differ in length, spectrum and attack. A third environmental/graphic detail should be justified. Don't stack full-spectrum noise with voice and lyrics.

## Real Motion Director toolchain (verified package paths)

- `starter/sound_design/render.py`: the actual packaged deterministic 48kHz stereo SFX renderer. Existing kinds `click`, `impact`, `whoosh`, `chime`, `riser`, `drop` remain; v67 adds `snap`, `paper`, `brush`, `tick`, `rattle`, `glint`, `glitch`, `sweep`, `pulse`. These are useful **scratch/original layers**, not a replacement for an experienced sound designer, recorded Foley, or a licensed premium SFX library.
- `examples/sfx-story-v67.json`: editable timecoded demonstration with differentiated materials. `python starter/sound_design/render.py examples/sfx-story-v67.json WORK/sfx.wav`.
- `scripts/event_audio_v46.py` and `scripts/production_v50.py`: preserve original stems and actual handoffs. Read their real schemas before use; do not pretend unknown flags exist.
- `scripts/sfx_story_audit_v67.py`: audit human-authored major visual events and their sound coverage. It checks coverage **on the planning map**; a passing report does not prove a rendered sound is audible, well mixed or legally cleared.

A custom sound can be created from newly recorded Foley or independently licensed samples when the user permits it. Record creator/license/URL/version/scope per external clip. Source website and reference movie remain information-only, not sample libraries; do not lift NOIZ/Claude sounds. No unlicensed copy of film soundtracks.

## Mix behavior, not just amplitudes

1. Keep dry user voiceover and song unchanged as source files; no forced re-recording, no wholesale resynthesis.
2. Separate tracks/stems: VO, music, primary tactile details, transition sweeps, optional sweeteners. Keep each event editable, label it for a scene and action.
3. **Pocket the narration:** voice should remain consistently intelligible. Lower/duck the music around speech; keep fast bright effects off consonants where possible, avoid masking the voice with multi-kHz noise. Never normalize SFX by stealing all headroom from music/voice.
4. **Prelap and tails:** subtle sweep or friction can start 80–250ms before an action; a click lands close to actual contact; a ringing/sustained tail can cross a visual cut for continuity. Those are editorial starting points, not mandatory offsets.
5. **Dynamic contrast:** quieter setup makes a single important hit feel larger. A mix of light/medium/hero events is better than every accent at identical strength. Avoid compression pumping, hard clipping and excessively loud transients; inspect true peak and integrated loudness when tools support it.
6. **Listen to A/B:** master with SFX on/off at the same loudness; then VO solo, music+VO, and full mix, over speakers and earbuds if possible. If the editor has no accessible playback, say so and mark the mix as unauditioned rather than claiming quality.
7. **Render check:** measure audio stream existence, decode successfully, review waveform/transients for possible collisions; measure at least the first hook, one mid-film action, strongest cut, and payoff. Numbers only nominate moments; they do not validate sound quality.

## Reject conditions

- Same `whoosh` on every cut; no material/tactile difference between grabbing, fragmenting and clicking.
- SFX only on slide transitions; actual in-scene object contact is silent.
- Effects enter abruptly, end instantly at shot boundaries, or do not bridge their picture actions.
- A louder mix sounds more energetic but worse than the quieter version; voice becomes less intelligible.
- A report shows many SFX events but the visual events have no logical sound relationships.
- Agent says it reviewed the audio when it only ran `ffprobe`, `ebur128`, waveform plots or measured transient peaks.

Use the existing palette as an adaptable instrument. The story determines **why** a sound occurs, the medium determines **what** it sounds like, and the edit determines **when** it should be heard.
