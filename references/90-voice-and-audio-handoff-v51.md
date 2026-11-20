# 90 — Voice director and audio acquisition: the client must be able to act

Use after story/copy unless audio already supplied. You are the sound supervisor, not a script vending machine. The client should never have to guess which model, what to paste, where to get a track, or how to export the raw take. Do not require them to edit, normalize, trim, combine, align, or select sound effects. Do not claim to have generated audio unless actual authorized output exists.

## 1. Choose route, not vendor by default
- Already supplied narration: keep raw file and exact words. No new design, no mandatory tags on finished spoken audio. If transcript is missing, inspect/transcribe only with an available legitimate method; ask for transcript if necessary. If a supplied file is already mixed, don't pretend stems exist; ask for originals if necessary for the requested final mix.
- Own recording: provide script + separate acting notes, advice to record in quiet space, no music under recording, export/upload unprocessed file. Tags are direction, not words to read aloud.
- Expressive TTS: select only an eligible provider/model confirmed available to the user, as allowed by its terms, consent and license. Check official current sources if web available; distinguish unverified current UI or price. If no web, say existing references may be out of date and do not assert current eligibility. Respect age/plan requirements; never tell a minor to bypass them or use someone else's credentials. If route unavailable, offer recording or an eligible licensed alternative.
- Agent generation: only with an available authorized tool and delegated choice. Don't spend money, clone voices without consent, claim permission or create accounts. If tool absent, send actual manual handoff now.
- Intentional no narration: no provider or tags; direction and music as appropriate. V50 route limits are in guide 92.

## 2. Performance before tags
For each phrase write intended emotion, why it changes, operative word, pacing/breath and relationship to the last phrase. Decide where a cue actually matters, including a neutral line after an expressive one. A natural performance has escalation and contrast, not maximal emotion. For 15–30 seconds, often 2–4 meaningful shifts, adapt to the story, not quota. Split phrases when a new expression changes the meaning. Use punctuation and whitespace as additional pacing cues. The existing tool requires at least two different non-neutral cues for expressive routes, but that is a technical floor, not the creative target. No random laughter, theatrical sighs or excessive tags; no forced whispered line. Do not include editor instructions, timestamps or shot notes in provider text.

### Exact supported internal cue vocabulary (compile_voice.py)
| Internal cue | ElevenLabs v3/v4 output | Fish S2 output |
|---|---|---|
| neutral | no tag | no tag |
| curious | [curious] | [curious, rising tone] |
| dry | [sarcastic] | [slightly sarcastic] |
| mischief | [mischievously] | [playful, sly tone] |
| quiet | [whispers] | [whispering] |
| sigh | [sighs] | [sigh] |
| chuckle | [chuckles] | [chuckling] |
| excited | [excited] | [excited] |
| reflective | [thoughtful] | [thoughtful, measured tone] |
| pause | [short pause] | [short pause] |

Internal keys are **not** provider syntax. Valid compiler identifiers in existing code: `elevenlabs` / `eleven_v3` or `eleven_v4`, `fish` / `s2-pro` or `s2.1-pro`, `plain` / `plain`. These are local identifiers, not a guarantee that any account exposes the same model label. Older manuals describe other natural-language tags; if using the compiler, restrict structured cues to the supported table, do not insert tags into `beats[].text`. If using a newly verified custom provider outside compiler, provide manual text/handoff, not a forged valid manifest. Plain route only supports `neutral`; store human acting direction in `note`. Read guide 25 for model-specific considerations. Tags are probabilistic instructions; actual output must be listened to. No SSML for the described expressive routes. Provider docs in 21/25/87 are references, verify availability and usage terms when selecting.

### Example, fictional file app (not a reusable client script)
ElevenLabs paste-ready block with approved clean words and deliberate cue sequence:
```
[curious] Why are there three final files?
[sarcastic] Final. Final-two. Final-actually-final.
[thoughtful] Oh. This is the one I sent.
[excited] Found it.
```
Fish alternative for the same words (only show the selected route to the client):
```
[curious, rising tone] Why are there three final files?
[slightly sarcastic] Final. Final-two. Final-actually-final.
[thoughtful, measured tone] Oh. This is the one I sent.
[excited] Found it.
```
Director notes belong outside these blocks: emphasize THREE, accelerate the repeated names slightly, soften at discovery, finish with small relief (if excited is too strong, audition another supported delivery). Never read these notes aloud. Captions use exact clean words, no tags. In a real production, fully replace fictional text and align to actual take. A provider-neutral script-only request can use separate directions per line even when the route is unknown; don't present unverified tags as guaranteed.

## 3. Voice Design vs Text to Speech: explicitly explain the distinction
Voice Design sets the character/timbre; it is not the campaign text. Text to Speech generates the spoken campaign from selected voice/model and tagged script. If user already has the desired voice, skip Voice Design. For a compatible playful/holographic direction, first use the exact user-authored, previously user-tested description in `24-holographic-voice-preset.md` — copy the original paragraph byte-for-byte, not the optional variant. Put it in its own block. Never claim it clones a real character or guarantees the same result. Do not regenerate a successful saved voice without cause. If a new take is distorted, correct the take or offer clean alternative with agreement. If using Fish or another provider, describe matching traits and choose authorized voice; do not claim that ElevenLabs description is a Fish-specific control unless verified.

## 4. What the client receives — a complete manual handoff
Use their chat language for instructions and requested language for actual narration. Do not send an instruction file alone. In the same response after choices known, provide:
1. Exact chosen provider, eligible route, direct official website/tool link (verify current path if possible), model to select, what to do if it is not available. Never imply that the user has a paid plan or must buy one.
2. If new voice design needed: exact separate prompt and where it belongs; audition options using a real campaign excerpt, save chosen voice. No design step for an existing voice.
3. Actual final copyable tagged narration (or clean text + human notes), not a sample, not placeholders. Explain tags are not part of captions. Tell user to paste only that block in TTS, not Voice Design prompt or director notes.
4. Generate, listen to first and last phrases and emphasis, regenerate only if necessary; download/export original WAV or MP3 via the actual supported interface. If current UI labels unknown, say “use the available download/export control”; do not invent button location. Upload untouched raw file. If user already supplied it, skip.
5. Actual chosen music and rights/acquisition steps (below). Upload separately only if lawful to obtain/use raw file. No mixing on user side. SFX selection/mix is yours.
6. End with what you will do *when receiving the files in a new turn*: align, edit, mix and create the output; no claim work runs now in background.

Example conversation (illustrative): “For the voice, open https://elevenlabs.io/ if your account is eligible. Select your saved voice in Text to Speech, select the verified expressive model, paste the block below, then generate. Listen for the dry delivery on the second phrase and the softer discovery on the third. Export the original MP3/WAV through the available download option. Don't remove the tags manually or add music. Upload the dry take here. I'll handle timing, sound design and editing once it's provided.” In actual use add exact tagged narration and applicable music instructions, not just this text. Official model and eligibility links are in guide 87/21/25. If no provider works, offer feasible recording path with same approved words.

## 5. Music research and rights are editorial tasks
Start with the film's intended mood, rhythmic shape, spoken density, desired energy pivot and distribution. Research real tracks rather than asking client to find one. Present 2–3 candidates when a choice is needed: a current/rising candidate only with actual dated evidence in relevant region/platform, and a strong evergreen/cleared option. Trending does not mean available for advertising. No invented titles, artist versions, stats, source links, availability, or claims of free licensing. In the absence of browsing or verified source information, explicitly state that you cannot confirm a current trending track and give an eligible way to choose lawful music without pretending you researched it. If user asks original music, use available authorized tools or request an actual eligible stem; don't invent generated audio.

Each candidate includes track + artist/version, official listening link, mood/story function, what section would support opening/reveal/landing (proposed cue points only until inspected), evidence of trend if claimed, coverage/uncertainty of commercial rights, source and lawful acquisition route. A dated official chart or platform trend page can support trend; a streaming page alone doesn't. Check attribution, platform, monetized use, edits, synchronization and ad/paid placement terms. Verify music and voice rights separately. Do not provide instructions to rip or evade licensed access. If commercial platform library licenses apply only to in-platform insertion, don't bake them into a claimed portable commercial master. Explain how user can add through platform only if allowed; V50 public release gate cannot represent that case fully. Offer a cleared alternative. No assumption that a sound reused on TikTok is legally licensed off-platform.

After selecting (user or delegation), give exact path to lawful acquisition and needed permissions; link to source and license info. If no download or export permitted, don't request an MP3 from an unauthorized downloader. If buying/license payment is required, present cost if actually known and ask before committing. Own the music edit after receiving the stem. If no music requested, record explicit decision; do not demand a song or fill `music_waiver` with fabricated consent.

## 6. When audio arrives
Preserve raw stems and names; check real stream, length, audio quality, pronunciation, accidental spoken tags, dead air, clipped/distorted peaks, levels, background leakage and rights. If unable to audition, disclose it; do not fill `audition_observation` as if you heard it. Run actual audio inspection, obtain measured phrase boundaries from verified ASR/forced alignment/manual listening and correct misheard words against approved script. Store exact phrase text in same order, actual SHA-256 and times in existing alignment template. Estimates are planning only, not verified alignment. Use locked script and real take length for design; if audio changes, realign. Mix dialogue first, then music using meaningful cues, then purposeful SFX; avoid covering words. Inspect final mix and picture together, check endings/cuts and avoid long unintended tail. V50 mixer does not guarantee professional loudness nor independent listening; technical evidence is additional. User doesn't have to do any of this.
