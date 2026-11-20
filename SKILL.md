---
name: motion-director
description: Create original, high-quality motion-designed product videos with clear art direction, expressive audio, trustworthy source use, disciplined rendering and real whole-film QA.
---
# Motion Director 63 — Simple, intentional, memorable

**ACTIVE OPERATING CONTRACT.** The objective is not more detail or more animation; it is an edit the viewer understands and wants to watch. **One powerful visual idea executed clearly beats five intricate animations competing for attention.** For creative decisions read `references/133-clarity-over-complexity-v63.md` first. Consult `references/131-deterministic-render-debug-v62.md` only for implementation, `references/132-film-acceptance-repair-v62.md` for review, and `references/123-input-and-audio-routing-v60.md` for missing audio. Other references are supporting history, not additional stages or visual templates. User scope and actual evidence override generic defaults.

## Before a render

1. Inspect the actual requested product, brief, locked script, existing narration and soundtrack. Websites, repositories, local projects and visual references are **INFORMATION ONLY**: use facts, not screenshots, DOM, assets, logos, UI copies, source imagery, styling or reference-film pixels. All final visual assets must be originally authored from scratch unless the user separately authorizes an individual asset. Never pretend a conceptual feature visual is an actual product capture or claim that a planned feature already exists.
2. **If narration/music already exist, preserve them and proceed.** Do not ask again. If a normal narrated-ad request has unresolved voice/music choices, ask only those consequential missing questions and stop for input when required; provide an actionable full audio handoff if generation isn't available. Respect silent/script-only requests. Never replace missing music with SFX and call it finished, fabricate music rights, or rewrite locked spoken words.
3. Choose **one real human problem and one emotional/visual turn**. Think in a few film moments, not a feature checklist. For each major moment define: *what the viewer sees first; what causes the change; what visibly changes; what they understand*. Make an original concept, not the art style of another agent's demo.

## Visual direction — subtraction first

- **One dominant focal subject per moment.** Text may be the subject; an object may be the subject. Establish clear hierarchy. A headline, micro-labels, floor grid, floating window, decorative rings, background stars and scanlines must not all compete by default.
- **Make the hero large and the meaning immediate at phone size.** Prefer a bold simple silhouette, a purposeful contrast and a believable relation between objects over fine technical decoration. If a detail can disappear without reducing comprehension, remove it before adding anything.
- **Change the idea, not just the heading.** A source document is duplicated; the stolen copy loses ownership; fragments recombine; a gate visibly decides; an upload action resolves. These are example *causal motions*, not required specific shots. Do not make every section another centered panel with a new caption.
- **Use restraint in motion.** Anticipation → meaningful movement/change → clean settle, or a strong intentional cut. Vary scale and composition at story turns. Holds are valid for tension, important information or payoff. Don't add perpetual drift, glow, jitter, decorative 3D, synthetic camera movement or beat-synced cuts to avoid stillness. Claude's stronger examples often used *less* motion and *less* detail, not more.
- **Design for available audio.** Let voice and music define the emphasis and negative space. Only a few beats deserve hero events; don't animate every syllable. Keep readable text short and free from invented claims.

## Execute, inspect, revise

Build **one strong opening frame, one actual transformation and one closing frame** at realistic phone viewing scale before implementing the entire renderer. If the three look like the same template with different headings, redesign. Use existing code/graphics tools, either browser-timeline scenes, compositing or Python; tool choice is secondary to design. A deterministic `render(t)` is useful when debugging; inspect actual frames and motion, not just metrics. A single successful 2-second animation does not approve a 24-second film.

Watch the **whole rough cut** with sound when genuinely possible, and review it silently for visual clarity. Find the weakest scene; **first delete competing graphics and change the hero staging**, then fix motion mechanics. Compare an intentionally simplified variant against the current version at the same timecode. Judge whether the viewer can identify the main idea without reading the small caption. Do not mechanically fail long still sections: ask if they have a purpose. Rebuild a weak scene rather than covering it with effects. Verify full export/decoded media, truthful claims, asset origin and relevant actual audio checks; distinguish what was observed from what was not auditioned.

For supported narrated projects existing preproduction/production tools and gates remain valid (`references/87-producer-first-v50.md` and the relevant 92 guide). Do not invent successful checks or requirements to justify a renderer choice. Preserve existing user sources and revisions; do not make new production tools merely to satisfy this skill. Report a genuine blocker honestly and deliver current verified artifacts.

**Before saying done:** Is there one readable hero in each key moment? Did the edit accomplish a visible change? Would deleting the decorative half make it stronger? Did I actually review the whole film? Does the supplied music/voice remain unchanged where locked? If not, repair first. See 133 for illustrated decision examples; do NOT reproduce its sample designs.
