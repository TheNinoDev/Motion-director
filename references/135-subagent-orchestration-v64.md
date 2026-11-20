# 135 — Director-led subagent production (V64)

**Active only when the host actually provides a supported subagent/delegation mechanism.** This is a workflow instruction, not a claim that subagents are installed or a request to fabricate them. The film has ONE accountable director. Divide independent, bounded decisions/work into small production contracts, then integrate and visually verify the results in the same actual Motion Director editing pipeline. Do not delegate an entire video independently to each worker or let assistants build competing renderers.

## The agency model

- **Director (parent agent):** owns the brief, final creative concept, locked spoken copy and user-supplied audio, the one film timeline, accepted visual language, cross-shot continuity, final edit, factual claims, release decision and user communication. The director inspects the work; a report claiming success is not proof.
- **Product fact scout:** read-only research into the requested product, code/project and user-provided context; return a concise supported-claim ledger with evidence, release status, and uncertainties. Websites, local projects and references are INFORMATION ONLY, never a source of imagery or interface/capture assets by default. No independent advertising claims or real-site visual extraction.
- **Story/art-direction scout:** propose two or three genuinely distinct, minimal human-readable visual mechanisms. Describe hero, initiating action, before/after, scale hierarchy and audio/scene purpose. Critique clutter. Do not author a full separate film; final concept belongs to director.
- **Audio/timing scout:** inspect only authorized, already-supplied voice, script and music and prepare a cue map with actually observed or inferred timing clearly differentiated. Preserve original assets, don't re-ask known decisions, don't claim music rights or auditions without evidence. If missing audio choices are consequential, the director conducts the actual user handoff before render.
- **Editor capability/shot worker:** inspect the installed Motion Director readmes/CLI/schemas, select an appropriate existing editor, and make **one small proof or assigned native-editable shot** in an isolated workspace. Return the plan, runnable verification command, rendered still/excerpt and feature inventory. Do not write a 500-line homegrown renderer when the existing compositor can express the action. Do not use all editor capabilities as a quota.
- **Independent film critic:** inspect actual whole-film playback or extracted evidence and the original brief with fresh eyes; report timestamped issues by severity, especially overdecorated layouts, dull loops, unclear narrative, poor pacing and incorrect or invented feature claims. Recommend concrete **subtractions or restagings**, not 'add more effects'. A contact sheet alone is not proof of motion quality.

Not every production needs six workers. Prefer **2–4 non-overlapping assignments** plus the parent director when supported; make more only if the work is genuinely separable. For a tiny clip, revision or constrained environment, one specialized assignment or **none** can be best. Avoid delegation overhead that exceeds the task.

## Correct sequence and synchronization

1. **Preflight by director.** Read actual user brief, existing assets and active `SKILL.md`, resolve required voice/music handoff. Assign a product fact scout and audio/timing scout concurrently **only if independent and tools permit**; share read-only input paths. Neither worker starts editing.
2. **Creative brief freeze.** Director picks ONE visual idea, writes a compact creative contract and audio/scene boundaries, and assigns editor capability scout or shot workers. Parallelize only independent shots or experiments with stable shared constraints. Every worker uses the bundled editor when it fits. Each gets **one shot/sequence, one unique output directory, one bounded task**.
3. **Integration barrier.** Director checks each handoff's files and actual preview, resolves overlapping timing, hierarchy, color, scale and continuity. Reject or reassign weak shots; do not accept merely because they rendered. Only the director or a single appointed integrator writes the master timeline and audio mix.
4. **Review barrier.** After assembling a complete rough cut, ask independent critic for timecoded, viewer-centered review. Director verifies complaints with actual playback, removes unnecessary details and repairs whole-film story flow. Critic has no direct release permission.
5. **Release.** Director verifies output truthfulness, source firewall, audio and actual export; only one release/push owner changes the release files or Git ref. Never claim successful delegation, QA, or export until confirmed by results.

## Exact handoff contract for each worker

Keep work orders short; include only the references required for the job, not the 500-file catalog.

```text
ROLE: [fact-scout / art-scout / audio-scout / editor-shot / QA-critic]
GOAL: one concrete question or deliverable
LOCKED INPUTS: user brief, product claim ledger, exact provided audio/script, duration/aspect, approved concept
ALLOWED SCOPE: read paths; unique output path; explicitly permitted edits
DO NOT: alter locked audio; import website visuals; invent product proof; bypass editor; overwrite other workers' files
OUTPUT: exact paths + concise decisions + observed evidence + unresolved uncertainty
ACCEPTANCE: one test/visual criterion that the director can verify
```

For an editor shot, add: `shot_id`, timecodes/transition anchors, intended focal hero, before/action/after, chosen actual editor engine/schema, preview/render command, and named native features actually used. Unique namespaces for group and layer IDs; no shared mutable outputs. For review, add 3–5 worst moments with exact timestamps and proposals to remove or restage elements.

## Avoid the dangerous patterns

- **Bad:** Spawn 6 agents and ask each to 'make the best ad'; combine six unrelated clips. **Better:** Director chooses one story first; agents work on verifiable, separate parts of that story.
- **Bad:** Product scout also captures website screenshots and uses them as visual assets. **Better:** Research returns only facts and evidence links. Original film art stays original.
- **Bad:** Every worker rewrites a separate video renderer, project root, or audio file. **Better:** Each editor task writes to `work/shot_<id>/` and returns a native plan/excerpt; one integrator assembles.
- **Bad:** Delegate taste, then trust checklists. **Better:** Director compares staged frames and playback, reduces clutter, rejects weak compositions and retains authority.
- **Bad:** 'Subagents not available' means stop work or pretend a team ran. **Better:** Use the exact same roles as sequential internal passes, with no false claim of spawning workers. Prioritize the highest impact step and keep moving.

## Example: supplied 23-second English VO/music, product script protection **in development**

Director freezes supplied narration/music, 9:16 and a single visual argument. Worker A (facts) confirms which capabilities are currently planned versus deployed; worker B (audio) maps phrase boundaries/drop from actual provided files; worker C (editor proof) tests the native compositor on one original code-to-protected-form transformation; worker D (independent QA) enters only after the first complete film. Director alone chooses the visual concept, merges timecodes and makes the final cut. Code and website may inform what the visual *means* but no source screenshot, DOM fragment or copied artwork enters the film. An understated single hero and purposeful pauses are often stronger than many decorative layers.

**Pass condition:** The final editor project has one coherent timeline and is visibly better to watch. The purpose of parallel workers is better attention to individual problems, **not higher asset count, more effects or longer output**.
