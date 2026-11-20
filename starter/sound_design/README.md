# Procedural sound accents (V15)

A reproducible stereo WAV effects stem, independent of TTS and music. Uses only generated tones and filtered noise, no external samples. It complements actual user-selected voice/music; not a replacement for either. Avoid clicking for every word or constant whooshes.

```bash
python starter/sound_design/render.py examples/sfx-v15.json work/assets/sfx.wav
```

The source plan `{fps,frames,seed,events}` references the **assembled** global timeline after overlap. Each event has `frame`, `duration_frames`, `kind`, `gain_db` (−45 to −3), `pan` (−1 to +1). Supported kinds: `click`, `impact`, `whoosh`, `chime`, `riser`, `drop`. Keep most events below −15 dB and use a few stronger impacts only when warranted; values are peak-amplitude gains, not measured loudness. Start with subtle effects. End within timeline. Renderer emits 48kHz stereo PCM, exact rounded sample count, peak protection, deterministic seed. Mix the stem via unified project `audio:{voice:"assets/voice.wav",music:"assets/song.wav",sfx:"assets/sfx.wav",sfx_volume:0.65}`. `audio.voice` remains mandatory for narrated final. If preview has only `sfx`, it is still a preview. No voice reuse, cloning or copyright claims are inferred. Listen to completed mix and compare speech clarity. No sidechain on SFX, so manual timing/gain is important.

If music has a dominant transient at that moment, skip the SFX. Use a whoosh primarily for intentional fast motion, impact at a decisive shape landing, click at verified actual interaction, chime at relevant resolution, riser before change, drop sparingly on reset. Voice is always priority.
