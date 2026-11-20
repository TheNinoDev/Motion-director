# A literal production checklist for a novice agent
Do not load every reference file into a tiny context at once. Read the current phase, write a durable artifact, then move forward. Keep `production-state.json` with stage, status, paths, assumptions, next action. Before continuing, read it and the current files. No stage can mark itself passed without evidence. Never stop at a plan if a user requested an actual render and the tools exist.

| Stage | Inputs | Do this in order | Output / pass condition |
|---|---|---|---|
| 0 | Request | Identify output and existing assets, check cwd/current project, probe tools and free space | state, tool report |
| 1 | Product evidence | Inventory factual claims, target group, brand, assets; ask for one source if all missing | brief + claims with provenance |
| 2 | Brief | 5 angles, 5 hooks, pick best, write and critique narration, reserve unused topics | script.txt, chosen angle, campaign ledger |
| 3 | Script, song | Check rights and audio file decoding; synthesize or accept VO; actual timing, normalize and mix | audio/voiceover.wav, mix.wav, timing JSON |
| 4 | Audio + claims | Plot narrative beats, reference motifs, 3 style frames, exact shot intervals and anchor transitions | shot-plan.json and mood/style decisions |
| 5 | Plan + assets | Choose renderer, smoke test, create scene modules, evaluate font/image load | preview frame and short sample |
| 6 | Working code | Render at reduced resolution, inspect all shots and transitions, revise | preview.mp4, QA notes |
| 7 | Preview passed | Render final, decode, inspect and listen, verify file paths and duration | final.mp4, report |
| 8 | Final | Package source and approved assets, include reproduction command and ledger | user-visible links/files |

## How to act when uncertain
- Feature unknown? Do not invent it. Use verified facts or ask for one missing fact.
- Script feels bad? Run the hook lab and copywriting rewrite pass. Do not use adjectives as a substitute for a story.
- Can't code complex animation? Start with mask reveal, stable baseline, strong layout and one moving focal point; use provided starter then adapt.
- Can't render 3D? Use real product crop or a clean flat object. Never fake 3D with ugly stacked rectangles.
- Can't use a paid voice? Ask for audio or use labeled local scratch VO with permission; no fake final quality.
- Need a genuine professional tool? Discover installed commands or plugin tools, test a 1-second render. Never install packages without permissible environment access; never run untrusted project scripts blindly.
- Do not loop indefinitely. Fix highest impact bug, re-run targeted test, then full validation. After two failed attempts at a nonessential effect simplify it. If major blocker persists, present actual partial work and specific error.

## Work log example
Stage 3 pass: script hash recorded; actual voice duration 18.4 s; music decoded; phrase offsets derived from WAV lengths; mix verified. Word alignment not available, so only phrase-timed text, explicitly disclosed. This is more honest than imaginary millisecond accuracy.
