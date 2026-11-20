# V6 — Voice acting, provider-specific script compilation and handoff

Read before any TTS generation or manual handoff. The exact original Voice Design description in guide 24 was authored and successfully tested by the user, including the generated voice. This is user-reported validation, not a new independent listening test. Treat it as the preferred preset for suitable campaigns and never edit it by default. It is not narration or an acting tag. No need to regenerate an already saved voice.

## 1. Make the voice sound like a character, not an advertisement
1. Write natural **clean narration** first. Choose one conflict, payoff and CTA. Each spoken line must sound plausible if said out loud; avoid fake enthusiasm, empty "revolutionary" words and repeated rhetorical questions.
2. Write a performance arc per narrative beat: intimate curiosity → dry annoyance → realization → playful confidence → quiet landing. This is one possible arc, not a universal template. For a serious product, prefer calm → concern → relief. Each emotional change must follow a story event.
3. Mark the operative word in each phrase in planning notes, then decide whether a tag, punctuation or simply word choice communicates the emphasis. Do not annotate every word. Start with roughly 1–4 audible acting changes per 15–30 seconds; more only when a dialogue genuinely requires them. No random laughs, breathing or moans. A real reaction should have a cause. Use adult, nonsexual delivery suitable for the audience.
4. Compile one clean script and one exact provider-ready copy block. Only send the selected provider's block and tutorial to the user; offer alternatives only on request. Separate voice design description, narration, provider instructions and timing notes. Never put editing directions into TTS. Do not discard an existing supplied voiceover or alter its script.
5. Audition a short hook + payoff with the chosen voice/model before a full paid generation when practicable. Tag adherence depends on voice/model and generation. Use credits only with authorization. If the user already reports the preset works, do not demand another audition of the design itself; check the new narration.

## 2. Supported model routes (official docs checked 2026-11-19)
- ElevenLabs Eleven v4 and v3 understand bracketed delivery cues. Prefer v4 if actually available and compatible; v3 is valid. Examples of documented cues: `[curious]`, `[mischievously]`, `[sarcastic]`, `[excited]`, `[whispers]`, `[chuckles]`, `[sighs]`, `[laughs]`, `[short pause]`. These are natural-language cues, not guaranteed fixed controls. v3/v4 do not use SSML breaks; other models may require different syntax. Verify the selected UI model and provider docs. If no expressive model is available use plain text, not literal spoken brackets.
- Fish Audio S2 Pro / S2.1 Pro accepts open-ended bracketed instructions locally before a phrase, e.g. `[speaking slowly]`, `[whispering]`, `[slightly sarcastic, rising tone]`. Use one clear cue per change. Fish legacy S1 used parenthetical cues, and its documented retirement is December 31, 2026; do not default to it. S2 API does not automatically convert legacy tags. Fish Drama 3 is a separate model; consult its current guide instead of guessing compatibility. Verify model names/availability at generation time.
- The provider does not need visual directions or a script explanation. Use the user's language for spoken text; use short, clear acting descriptions in the same language or English if supported. Never ask to use all tags simply because they exist.
- Preserve the original tested holographic prompt exactly. Only offer a clean alternative if the user requests it or an actual generated take has distracting artifacts, and label it as an alternative. Avoid doubling the holographic effects in post.

Sources: https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/how-do-audio-tags-work-with-eleven-v3-and-v4 ; https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices ; https://fish.audio/de/blog/fish-audio-s2-fine-grained-ai-voice-control-at-the-word-level/?articleLocale=en ; https://github.com/fishaudio/docs/blob/main/developer-guide/best-practices/emotion-control.mdx ; https://github.com/fishaudio/docs/blob/main/developer-guide/getting-started/changelog.mdx . Follow provider terms and eligibility in guide 21.

## 3. Translate delivery intent, not tags blindly
| Intent | Eleven v3/v4 | Fish S2/S2.1 | Use when |
|---|---|---|---|
| Curiosity | `[curious]` | `[curious, rising tone]` | Hook is a genuine question |
| Dry humor | `[sarcastic]` | `[slightly sarcastic]` | Contradiction or understated joke |
| Mischief | `[mischievously]` | `[playful, sly tone]` | A clever reveal, never random |
| Quiet aside | `[whispers]` | `[whispering]` | A short confidential phrase; keep intelligible |
| Relieved exhale | `[sighs]` | `[sigh]` | Frustration or resolving tension |
| Brief chuckle | `[chuckles]` | `[chuckling]` | An actual humorous beat |
| Excitement | `[excited]` | `[excited]` | A deserved payoff, not a feature list |
| Reflective | `[thoughtful]` | `[thoughtful, measured tone]` | Let a discovery land |
| Reset | `[short pause]` | `[short pause]` | If punctuation alone doesn't produce a pause |

Fish free-form examples and some Eleven cues are suggested directions, not a verified exhaustive preset list. The compiler uses these as conservative suggestions. A tag is an instruction, never a promise to create an exact sound or timing. Do not stack contradictory cues. For a pause essential to an edit, place silence in post after alignment rather than relying on a tag duration.

## 4. Use the bundled compiler
Copy `templates/voice-performance-v6.json`, replace all beat text with locked real narration and remove empty or unused beats. Set provider and model to the actual selected model. Run:
```
python scripts/compile_voice.py voice-plan.json --out creative/voice
```
It emits `narration.txt`, `provider-input.txt`, `caption-source.txt`, `performance.json`. Use `provider-input.txt` for TTS only; caption-source is clean words, not aligned subtitle timings. It rejects unsupported model/provider pairs, embedded stage tags, missing text, invalid cues and accidental narration edits when a `locked_text` is supplied. It intentionally does not generate or listen to audio. If user gave exact script, preserve punctuation and wording; use explicit paragraph boundaries without rephrasing. For unsupported providers manually follow documented syntax or plain route.

## 5. What to send the user
If agent cannot generate authorized TTS: give one compact message with the chosen provider's instructions, exact original description only if creating a new designed voice, copyable compiled narration, and a request for dry original WAV/MP3. No music or FX baked into VO except inherent voice texture. Do not expose account keys, force signups, or make user edit anything. If multiple files needed, supply filenames and exact corresponding text. User never needs to remove tags or join takes. If the voice is already supplied skip this entire request.

## 6. Full take vs split takes
Continuous take by default preserves phrasing, speech rhythm and character. Split only at strong sentence/scene boundaries, provider limits, an isolated faulty utterance or a deliberately contrasting emotion. Reuse same voice/model/settings. Save filenames VO-01, VO-02; verify each by listening if possible and compare transcript to clean narration. Join with short room-free gaps (start 80–160 ms; tune to natural sound), no crossfade over spoken syllables. Preserve raw files. Correct mispronounced names, accidentally spoken tags, clipped breath, exaggerated effects, missing words or unearned emotional shifts. Regenerate the smallest defective part. Do not fake listening or transcribe from the script alone. If no ASR/alignment tool, use honest phrase timing from verified files and mark unverified pronunciation.

## 7. Editing after actual voice exists
Generate captions from spoken words, never from provider tags. Match words after ASR/forced alignment; preserve genuine interjections only if intended. Map each actual delivery pivot to a visual beat: anticipation on inhale, action on stressed word, reveal after short pause, hold through semantic payoff. Music and SFX should leave the most important syllables clear. Do not force visuals to predicted TTS durations. Use final actual audio timings for frames. Peak/loudness checks do not prove acting quality. If the quiet voice is unintelligible, lower the music before overcompressing the voice. Never add fake glitch sounds on every syllable. Use the release gate with evidence of an actual listen or flag the missing capability.
