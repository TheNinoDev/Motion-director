# 107 — Copy, performance, audio packet: actual outputs (V55)

Use 103 for full audio policy and 24 for the exact user-authored voice prompt. This guide is the last-mile contract, not a competing provider catalog. Provider names/model availability/cues/terms change. Check current official documentation when possible at the time of a real production. Do not silently convert historical facts into present claims. Examples in this guide are fictional and illustrate writing, not verified provider support or product facts.

## 1. Write for an edit, not for a brochure
For an original campaign, test three opening mechanisms and two substantially different complete scripts before selecting. Distinguish the hook from the headline: the first spoken sentence may be a reaction, an unfinished thought, a surprising observation or an action; the visual hook can begin earlier or contradict it in a truthful way. A strong visual hook does not require a slogan. Use short spoken clauses, contractions where natural, and selective pauses. The answer to the curiosity must come from the actual product, not just a logo.

Editorial tests, in order:
1. Would a real person say this in the target language? Delete promotional filler, unnecessary brand repetition, and phrases that exist only to list features.
2. Is the specific tension, consequence or surprising behavior visible? If the name could be swapped with any competitor, make it more concrete.
3. Does every subsequent phrase develop the premise? If the proof is the third line, the first two should set it up, not introduce two unrelated features.
4. Is every product statement supported by actual evidence or clearly identified illustration? No fake testimonials, guarantees, competitor allegations or invented metrics.
5. Does the last phrase pay off the opening and, when appropriate, include a natural next action? Avoid a forced CTA if the story already lands and user wants a brand spot.
6. Estimate approximate spoken length including pauses, but don't invent timecodes. A short story can be stronger than a long one. Use real recording to time final edit. If duration is a hard constraint, audition and revise before locking; don't solve it by making the voice unnaturally fast.

### Three fictional hook mechanisms, one verified behavior
Assumed demonstration evidence: a note app has manual color labels and a matching label filter, and the sample data contains a note named “Packing list”.
- Question: “Where's my packing list?” (viewer follows search).
- Contradiction: “I color-coded everything. Still couldn't find it.” (viewer discovers filtering; avoid implying app malfunction).
- Action: “Blue. There you are.” (start on a visible filter interaction, reveal what blue means).

The mechanisms have different visual setups; choose based on the actual capture and tone. A possible complete direction for the first: “Where's my packing list? Nope. Also nope. Wait, I marked it blue. There it is.” It is intentionally short: wrong results, remembered fact, filtered proof, relief. For a hard longer duration, develop an additional *meaningful* beat or hold real proof, not generic filler. If real product has no matching filter, abandon this draft instead of fabricating a result. Don't reuse this phrasing for unrelated apps.

## 2. Acting direction is performance, not punctuation
Give each meaningful phrase an intention. E.g. question with rising curiosity; first rejection dry and quick; second shorter and more resigned; realization softer and slower; resolution genuine relief, not a shouted sales pitch. Treat pauses, stress and delivery as a continuous arc. Select compatible provider cues only after verification. A neutral connector can be untagged; a one-line locked script may need one cue or none. Do not multiply emotional labels merely to satisfy a heuristic. Do not append “(sadly)” inside TTS unless the selected provider actually supports it in that format.

For a verified compatible ElevenLabs expressive model, illustrative TTS paste could be:
```text
[curious] Where's my packing list?
[sarcastic] Nope. Also nope.
[thoughtful] Wait, I marked it blue.
[excited] There it is.
```
For an appropriate verified Fish S2 route an illustrative equivalent could be `[curious, rising tone]` before the question and `[slightly sarcastic]` before the rejection, with supported natural language cues appropriate to the remaining lines. The actual handoff must include **all lines** in selected-provider syntax; an abbreviated tag example is never the deliverable. Follow official support and local cue mapping (90), and report a mismatch rather than changing locked words. Never label these examples as coming from a live provider check. Audition for accidental spoken tags, incorrect pronunciation, shrill tone, excessive artifacts and rushed pacing. If the route cannot be verified, provide complete clean text plus separate phrase directions now, and specify what provider/model choice remains. Human narration: no inline machine tags unless the user specifically wants them as direction.

## 3. The actual user-visible packet (only applicable blocks)
This is a response structure; do not send placeholder brackets, an empty table, or the instructions themselves. Populate with real inspected evidence, selected copy and links. Use the user's spoken language inside copy and chat language for directions. If they request script only, deliver just selected copy and appropriate acting notes. If they already supplied raw files, skip instructions to produce them again. For a new full ad with missing audio:

**Story** — one sentence of the selected premise, why it fits the actual verified feature, approximate planned length if useful. State whether text is proposed or locked.

**Voice setup** — choose one suitable eligible provider and official link, current model/voice selection (verified or explicitly uncertain), any relevant access/rights condition. If user has a saved authorized voice, select that; do not ask them to recreate it. If a new suitable holographic voice is needed, copy the *entire exact* original paragraph in 24 here in its own copy-only block and give current supported Voice Design instructions. If Voice Design needs preview text, supply real campaign excerpt separately. Explain how to hear/save a chosen voice. Never use the character description as the words spoken in the ad. Never require a paid upgrade or sign-up without consent; account eligibility and commercial permissions matter.

**Paste into Text to Speech** — provide full selected-provider tagged script in a distinct block containing only TTS input. Include the actual words, not “insert the script above”. When applicable provide a clean archived or separate version of the same words for editing/captions. Do not let clean and tagged versions drift. If provider is unsupported/unknown, the paste block is clean, with a clear reason and separate actual acting notes. Do not withhold copy while researching.

**Generate / listen / export** — instruct the user specifically to select the voice and actual supported model, paste the block, generate, listen for exact words/names/emotion/pauses, retry only if necessary, and download via supported WAV or MP3 export. If known provider length limits apply, split at sensible natural boundaries, provide each complete numbered copy block and matching file name, and preserve order. Do not instruct user to trim, EQ, normalize, mix or add effects. If you have access and authorized delegated generation, create the actual raw audio instead of asking for transfers.

**Music** — recommend a real verified track and alternatives suited to the story when research available. Give song/artist/exact version, official listen and legal acquisition links, specific rhythm/texture fit and role in hook/proof/payoff, rights source and scope (public ad, organic vs paid, platform, territory, export, attribution, allowed edits as applicable). Current trend claims need dated evidence for relevant audience/platform/region; an evergreen option need not pretend to be trending. Don't send generic genre words as if they were a real recommendation. If no current evidence or no access, clearly say so and offer an official lawful library route and specific selection criteria, without guessing clearance or claiming recommendation verified. Platform-only sound means insertion within that platform as permitted, not ripping and muxing into a universal MP4. Use authorized separate files only. Never ask the user to source a random song when they delegated that work and research is available.

**Send back** — name the exact missing original files: e.g. `voice.wav` or `voice.mp3`, `music.wav` or `music.mp3` if cleared for export. If they need to send multiple takes, name which and order. Ask only unresolved permission that materially matters. Explain you will do selection of music region, alignment, cutting, effects, mixing and visual motion; do not promise async work. If a user has actual authorized stems already, inspect and continue. If they cannot generate audio, provide the feasible alternatives (existing authorized recording, own dry recording, an available eligible route, or explicitly requested intermediate picture-only cut), not fake audio.

## 4. Before return, check the packet from the recipient's side
A novice should be able to follow it without asking where to paste, which field is voice description, where to find the song, whether tags are included, which files to return, or whether they must edit them. In the case of genuinely unknown UI/model availability, say what is verified and what needs user confirmation rather than invent menu names. If voice generation is available but permissions are not, distinguish authorization from technical ability. No passwords/API keys in chat. Keep original sources unchanged.

After delivery of the files, inspect actual streams and duration, then actual speech and music where supported. Technical metadata is not audition. If exact pronunciation or approved text differs, resolve it before picture lock; don't silently rewrite. Measure sync against actual words and musical accents; draft time estimates are provisional. Preserve dry VO and music separately. If a corrected audio take changes duration, invalidate timing of dependent markers and rerender only as needed. See 97 for honest release states.
