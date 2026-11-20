# 112 — The next useful reply: intake, copy and production handoff (V57)

Current operational guide for intake, script and audio. Root SKILL.md controls scope. The detailed V55/V56 guides are optional lookups, not extra steps. Examples below assume fictional products or describe an explicitly unverified route. A real agent must use actual client facts and verify any external service information at execution time. Do not recite these examples to the client instead of doing their job.

## 1. Decide once, then produce

Read the latest user message and existing project. Keep a short private record of the known decisions, permissions, current deliverable and smallest outstanding dependency. Distinguish an observed product fact from a supplied claim and an editorial metaphor. A public site is not permission to use private assets, spend money, or claim its features work without evidence. If the page cannot be inspected, use supplied proof and ask for the smallest missing artifact. Do not pretend a URL was opened.

Use the following priority order when one message contains several requests:

1. Explicit scope locks (e.g. "script only", "keep the exact words", "no music", "do not redesign the UI").
2. Essential missing facts that cannot reasonably be inferred or delegated (e.g. no identifiable product; incompatible language directions; rights for a required track). Ask a targeted question only for those.
3. Deliverable already possible: write it or perform the work now. Do not wait for missing unrelated inputs.
4. Remaining reversible creative choices: choose a reasonable default, briefly disclose if consequential, and continue. Do not ask the client for an animation engine, a font, a tag dictionary or camera coordinates.
5. Genuine missing authorization, asset or capability: deliver feasible work, state the precise blocker and specify the smallest next user action. Do not claim a final export, successful audition or confirmed license.

### Select the response envelope

| What the client supplied | What the answer actually contains | What not to do |
|---|---|---|
| Product name/URL only, full ad requested | Inspected observation and one recommended story if possible; only unresolved consequential questions, normally grouped into a few natural questions | Ten creative preferences; promise a later render; claim untested capabilities |
| Sufficient brief, no audio, asks agent to choose | Selected concept + complete spoken copy + usable voice/music acquisition package if needed; exact missing stems | Ask which hook, which song, which model if the choice was delegated |
| Complete brief, audio volunteered | Inspect files, preserve decisions, align and create the requested artifact with actual tools | Return a new questionnaire or ask the user to regenerate good audio |
| Script only / locked wording | Full requested written artifact; expressive paste version when applicable; clean version when requested; keep locked words | Force soundtrack selection, video review, or full-ad pipeline |
| No narration or no music explicitly | Respect it; supply only relevant picture/audio steps; no forced voice or soundtrack | Hide an unwanted voice or add music without permission |
| Existing render criticized | Identify actual defect and its scene/time; fix with available source; verify changed result | Add generic effects; change unrelated copy; claim editable access from MP4 alone |

Do not ask to confirm the same choice in different words. If the client says "you decide", handle style, motion, creative story and reasonable default length unless a hard constraint is unknown. Distribution scope and permissions may still matter. If a choice can be safely reversed, proceed with a clearly marked assumption rather than stall.

### Worked first answer (not a universal questionnaire)

Case: a fictional scheduling app. The inspected UI establishes drag-to-move a calendar event, but not automatic conflict resolution. The user says: "Make a cool video for this." An appropriate reply is: "I'd center it on moving a meeting with one drag, rather than listing the app's features. The opening could show a calendar slot sliding into place. Is this aimed at individual users or teams, and should the voiceover be English or German? Do you have a voice/music track already, or should I choose an audio route? Where will it be published?" Omit already-known questions. If the client says "you decide, English TikTok, no audio", do not ask again. Choose a coherent angle and supply the copy and audio package in the next response. Do not claim the product detects overlapping meetings unless independently verified.

## 2. Copy: select a reason to keep watching

For a new campaign, explore three genuinely different hook mechanisms (e.g. an unexpected outcome, a physical action or a relatable tension), not three adjectives for the same headline. Draft two distinct complete narrative approaches internally. Evaluate natural speech, specificity, evidence, visual action and payoff. Ship the strongest full draft, unless the user asks to see alternatives. Do not force multiple drafts for a locked change or a script already supplied.

Make the first phrase a natural thought or meaningful action; establish a question or expectation for the clip to resolve. Use plain, audience-appropriate English when requested. Avoid "Meet the ultimate...", "unlock the power", "seamless", fabricated personal reviews, unsupported comparisons, and ending with an unrelated generic CTA. These words are not categorically forbidden if they have a specific justified purpose. A simple demo can be a stronger story than manufactured drama. A product name can arrive early when necessary for comprehension; a static logo is not automatically a hook.

As a short fictional scheduling example (assumed drag behavior only):

Clean words: "Not at nine. There. Eleven works. That's the meeting moved." This can work as a short clip driven by a real action. For a 24-second target, don't stretch these words using awkward silence or invent functions. Develop a complete different script with a second meaningful beat, or use a deliberate visual/music-led opening and payoff that fit the runtime. Read it conversationally and revise redundant clauses. Time estimates are provisional until an actual take exists.

## 3. Deliver the actual audio packet, not a task list

If audio is not already supplied/generatable with authorized tools, use this order in one user-visible answer. Do not use placeholders in a real final handoff. If a fact cannot be verified, say precisely which item remains uncertain and supply the usable parts, rather than fabricating the missing values.

**A — Chosen direction.** One or two sentences: central story, audience and approximate duration. State only consequential assumptions. If the user asked only for copy, do not turn this into a pitch.

**B — Voice setup.** Specific verified official provider link, compatible model, existing voice or new original design route, any applicable price/eligibility/rights constraint. If the preferred new holographic voice is appropriate and wanted, open 24-holographic-voice-preset.md and copy the exact original paragraph in a standalone plain-text block. If a saved voice or recorded take exists, omit design entirely. The character description is not the script. Never write fake TTS UI menu paths, model availability, tiers or permissions. Check official documentation or the available actual provider interface. When no verification is possible, say that and use the fallback in section 4.

**C — Complete narration.** The actual complete copy in a plain-text fenced block or native copyable writing artifact. Use one chosen compatible provider's expressive syntax, not a mixture. Put supported tags immediately before each meaningful performance phrase; add contrasts in intention, pacing and energy where they advance the story. Use provider-supported punctuation/pause mechanisms, don't invent `[pause 0.7s]`. No speaker labels, timestamps, SSML, bold tags or editor notes unless the selected model explicitly requires them. Human-readable clean transcript should be separate from tagged text when required for captions or locked copy. Captions never show acting tags.

Illustrative only, assuming a compatible expressive model and verified cues:

```text
[thoughtful] Not at nine.
[playfully] There. Eleven works.
[relieved] That's the meeting moved.
```

The final real block must actually be complete and adapted to verified cue syntax. A provider may render unfamiliar tags aloud; verify syntax and audition before release. A cue per phrase is a useful planning practice, not a quota. Let coherent phrases share an intention; don't add seven tags on every word. If the model accepts only separate instruction fields, supply that field separately rather than pollute the spoken text.

**D — Novice generation and audition.** Explain exactly which text goes into which actual field, how to select or reuse the voice/model, generate, listen, check words and tag leakage/pronunciation, and export the raw voice file. Give a simple remedy for a wrong take: adjust the affected supported cue or punctuation and regenerate the affected segment where available; avoid paid repeats without authorization. Tell the client whether to upload one complete take or clearly ordered stems. Prefer WAV if supported, good-quality MP3 if not; no conversion needed on the client side. The client does not cut, align, normalize, add reverb or mix. If authorized generation is available and delegated, perform it, don't force the client to do these steps unnecessarily.

**E — Music.** Select a relevant candidate or a short, curated set from actual verifiable research; include a current trend candidate when the brief calls for it and a timeless appropriate alternative when feasible. For each real candidate provide title/artist/version, fitting musical moment (build, reveal or payoff, not invented exact timestamps), official listening and lawful acquisition link, evidence of any claimed current trend with date, and rights status for the requested release. Do not imply a playlist, a subscription, a preview stream or a song on TikTok grants commercial sync rights. Distinguish ordinary posts, paid ads, business accounts and cross-platform delivery where relevant. Clearance uncertainty means pending, not permitted. Where only platform-library addition is allowed, supply the portable cut without that music and explain the exact intended separate insertion workflow if supported. Never instruct the user to rip audio or bypass restrictions. If the provider cannot be verified, offer an appropriate lawful library route and music direction without inventing a track.

**F — One clear return action.** Specify only the missing materials, e.g. "Send the raw voice export and the cleared music download, separately. I'll handle the edit and mix in this project once the files are provided." Do not say work is running in the background. If all assets and permissions exist, omit the return request and perform the current production. Never ask for a password or credentials in chat. State genuine blockers separately, not as if the client failed.

## 4. Partial capability does not excuse a broken handoff

| Missing capability | Still deliver now | Do not pretend |
|---|---|---|
| No current provider docs | Full clean script, phrase-by-phrase acting notes, known official homepage only if confident; request/verify selected model before native tags | Exact current syntax, UI controls or account eligibility |
| Verified model supports tags but no generation tool | Full native-tagged script plus exact manual setup and export instructions | Generated/listened audio |
| Research unavailable for music | Concrete soundtrack direction (texture, rhythm, cue roles); lawful licensed-source route if known, status pending | Specific invented tracks, current chart positions or rights |
| Audio file received, cannot listen/ASR | Actual stream metadata if available; use supplied confirmed transcript/timecodes as such, record uncertain segments | Speech accuracy, natural acting, intelligibility or measured word alignment based on waveform alone |
| Existing voice but no music | Preserve voice, prepare only missing music work; plan against available speech | Regenerate voice to satisfy a template |
| No approved audio, user explicitly wants preview | Work on picture as clearly labeled intermediate, using provisional timing if necessary | Final narrated ad or license-cleared export |

Use guide 107 for additional packet detail, guide 103 for deeper music/voice workflows, guide 90 for legacy cue examples (not live provider authority), and 24 for the exact voice prompt. The V50 tools check a subset of these requirements; a validator pass is not permission to omit the complete user-visible packet.

## 5. Five-second outgoing-answer check

Look at the actual draft to be sent, not private notes. If it asks the client for narration, can a novice copy an actual complete text and identify the correct place to paste it? If expressive support was verified, are actual native cues in the block? If music is needed, can the client identify an exact track and legal route or understand honestly why it is pending? Did you deliver the selected story or script rather than describe how you will write it? Did you repeat a answered question? Correct omissions before sending, then return only the result and necessary next action—not this checklist.
