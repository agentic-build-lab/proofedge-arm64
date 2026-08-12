---
format: 1920x1080
duration: 168.767s
message: "ProofEdge turns AI-generated migrations into auditable evidence, with private local reasoning and measured optimization on real Arm64."
arc: "PAS + Demo Loop: trust gap -> proof promise -> concrete defect -> evidence gates -> security -> Arm64 A/B -> frozen release gate -> local value -> reproducibility -> CTA"
audience: "Arm challenge judges, ML systems engineers, and developer-infrastructure teams"
mode: autonomous
music: none
captions: true
---

## Video direction

- Palette system: use the normative `frame.md` roles only — canvas `#0E1319`, display text `#F3EFE7`, ProofEdge amber `#F3A712` as the sole focal accent, and `#63D6C5` only in its assigned muted/supporting-text role. Geist carries display and body; numeric cells use tabular figures.
- Motion grammar: one paused, seek-safe timeline per frame; smooth long-tail settles (`power3` family), explicit `fromTo` entrances, and phrase-by-phrase reveals on the matching voice cue across the back half. No default bounce. Internal seams are velocity-matched; the harness owns frame exits.
- Composition: reserve the bottom 17% for captions. Every content frame uses a dominant focal element, at least three depth roles, and the ProofEdge page’s measured, high-contrast editorial restraint. Captured product screens are the visual source of truth; overlays may annotate but never rewrite them.
- Rhythm: Frames 1–5 develop quickly; Frame 6 is the deliberate scrutiny/held comparison; Frame 7 resumes with the release gate; Frame 8 breathes; Frame 9 is the long evidence traversal; Frame 10 holds the repository and demo long enough to read.
- Negative list: no invented figures, logos, customer claims, fake terminal output, neon AI gradients, bokeh, drop-shadow-heavy cards, endless loops, lazy breathing, back-half camera drift, slideshow front-loading, or screensaver motion.

## Frame 1 — The trust gap

- scene: Outcome-language questions replace one another, then resolve on “Evidence is hard.”
- voiceover: "AI can rewrite a migration in minutes. But when a parameter disappears, an edge case shifts, or a test quietly changes, how do you prove behavior survived?"
- duration: 11.307s
- transition_in: cut
- status: animated
- src: compositions/frames/01-trust-gap.html
- type: hook
- persuasion: Pain validation
- beat: tension + skepticism
- blueprint: kinetic-type-beats (Adapt)
- asset_candidates:
- focal: outcome-language typography
- roles: typography = foreground; evidence rule = supporting; restrained dot field = background
- sfx: impact-bass-1, click-soft

narrativeRole: Open on the judge’s real outcome risk, not on the product or its implementation.
keyMessage: Fast migration generation is not the same as preserved behavior.

Adapt: keep the fixed-center statement relay and locked final beat; extend the windows to let each failure mode arrive on its spoken cue, with no playful overshoot.
Scene 1 (0.0–2.2s): “AI can rewrite” arrives as a left-anchored two-line display block in the top 60% via per-word staggered reveal (`dynamic-content-sequencing`); a thin amber rule self-draws beneath it (`svg-path-draw`). Asymmetric 70/30, low density, three depth planes.
Scene 2 (2.2–5.2s): “a parameter disappears” replaces the lower line by hard-cut word swap (`discrete-text-sequence`); a function argument chip snaps out at the far right, timed to “disappears.” The headline stays pinned; only the variable evidence slot changes.
Scene 3 (5.2–8.3s): “edge case shifts” and “test quietly changes” cycle in the same slot, one cue at a time, with brief motion-blur streaks resolving sharp (`motion-blur-streak`); the amber rule steps from intact to broken to muted.
Scene 4 (8.3–11.307s): the prior text clears at peak velocity into “How do you prove behavior survived?”; “Evidence is hard.” lands beneath in amber via kinetic beat-slam (`kinetic-beat-slam`), then the frame holds completely still for the question.

## Frame 2 — Evidence before confidence

- scene: The real ProofEdge hero pulls back into the product’s source, target, plan, and ledger promise.
- voiceover: "ProofEdge compares the source with the migration, maps their public contracts, proposes differential tests, and produces an evidence ledger. Private code stays local. Every conclusion stays traceable."
- duration: 13.781s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/02-evidence-before-confidence.html
- type: product_intro
- persuasion: Risk reversal
- beat: relief + clarity
- blueprint: zoom-out-workspace-reveal (Adapt)
- asset_candidates: assets/scroll-000.png — captured ProofEdge hero and native Arm64 evidence strip
- focal: assets/scroll-000.png
- roles: scroll-000.png = background and final containing whole; exact reconstructed headline crop = foreground; contract chips = supporting
- sfx: whoosh-cinematic, chime

narrativeRole: Land the product promise by the second beat and make local, auditable reasoning the defining value.
keyMessage: ProofEdge converts migration uncertainty into traceable evidence without exporting private code.

Adapt: keep the single decelerating zoom-out signature, but protect the one-times capture from raster enlargement by opening on an exact DOM reconstruction of its headline and resolving to the real screenshot at native scale.
Scene 1 (0.0–2.5s): extreme close-up on the exact “Evidence before confidence” headline reconstruction; “source” and “migration” appear as two small numbered chips while the world is already authored behind it. Full-bleed detail, no browser chrome.
Scene 2 (2.5–6.2s): contract-map and differential-test labels reveal beside the headline as the VO names them; the single camera pull begins, using viewport-change (`viewport-change`) with strong deceleration and no zoom-in anywhere.
Scene 3 (6.2–10.5s): the one zoom-out completes onto the real `scroll-000.png` at native 1920×1080 scale; the screenshot becomes a wide left-weighted surface and the evidence-ledger card resolves in the open right third. Camera locks permanently.
Scene 4 (10.5–13.781s): “PRIVATE CODE STAYS LOCAL” and “EVERY CONCLUSION TRACEABLE” illuminate sequentially as amber proof chips; the screenshot remains still and readable, with only one low-amplitude keyword glow (`asr-keyword-glow`) on “traceable.”

## Frame 3 — One missing argument

- scene: The captured source and target functions hold side by side; the missing optional argument becomes the focal defect and the evidence ledger answers.
- voiceover: "Here’s a frozen public case. The source accepts an optional refund reason. The migration removes that argument, yet still claims compatibility. ProofEdge cites both lines, proposes the boundary test, and refuses the unsupported claim."
- duration: 17.173s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/03-one-missing-argument.html
- type: feature_showcase
- persuasion: Show-don’t-tell proof
- beat: curiosity + control
- blueprint: device-surface-showcase (Adapt)
- asset_candidates: assets/scroll-027.png — captured source/target/evidence console; assets/scroll-053.png — captured code defect flowing into measured evidence
- focal: assets/scroll-027.png
- roles: scroll-027.png = foreground persistent product surface; scroll-053.png = supporting second screen state; defect annotation = foreground
- sfx: click, error, chime

narrativeRole: Prove the product with one memorable semantic defect rather than a feature list.
keyMessage: ProofEdge catches a concrete compatibility break and shows exactly why it matters.

Adapt: keep the persistent-surface, cursorless stepwise-flow signature; use two real captured states and a static camera so no fabricated click path is implied.
Scene 1 (0.0–3.0s): `scroll-027.png` establishes as an 80%-width clipped product window in the top caption-safe zone; the source and target columns are clean while all unrelated page copy is softly masked. Split-screen hierarchy inside one persistent surface.
Scene 2 (3.0–7.5s): as “optional refund reason” is spoken, the source signature receives an amber line highlight sweep (`css-marker-patterns`); the target column stays muted and unchanged.
Scene 3 (7.5–12.0s): the held surface advances to `scroll-053.png` by same-center scale-swap (`scale-swap-transition`); the missing argument on the target receives a red directional chip while “claims compatibility” appears as a crossed claim badge.
Scene 4 (12.0–17.173s): a narrow evidence-ledger panel expands from the screenshot’s ledger region (`anchored-layout-expand`), revealing source line, target line, boundary test, and `UNSUPPORTED` sequentially; camera stays locked and the final receipt holds.

## Frame 4 — AI proposes, evidence disposes

- scene: Four gates execute in sequence: bounded ingestion, contract map, local planning, and reference validation, ending on an auditable receipt.
- voiceover: "The workflow has four gates. Bounded ingestion rejects unsafe or excessive content. Deterministic analysis builds typed facts. A compact local model proposes only a small test plan. Then every cited path and line is validated before it can enter the ledger."
- duration: 19.221s
- transition_in: crossfade
- status: animated
- src: compositions/frames/04-evidence-gates.html
- type: feature_showcase
- persuasion: Mechanism transparency
- beat: trust + confidence
- blueprint: agent-progress-theater (Adapt)
- asset_candidates: assets/scroll-080.png — captured measured benchmark and four-stage evidence architecture
- focal: four-gate receipt stack
- roles: scroll-080.png = supporting captured architecture plate; gate receipts = foreground; progress rail = background structure
- sfx: riser, click-soft, chime

narrativeRole: Explain how the system earns trust without asking the viewer to trust the model itself.
keyMessage: The model proposes; deterministic gates decide what becomes evidence.

Adapt: keep the machine-working-to-receipt signature, replace playful loader theater with restrained evidence gates, and let the captured architecture plate authenticate the final state.
Scene 1 (0.0–3.0s): “THE WORKFLOW HAS FOUR GATES” docks top-left; a thin scan rail starts beneath with one finite rotating amber arc (`svg-icon-enrichment`). No cursor or menu.
Scene 2 (3.0–7.0s): “Bounded ingestion” appears as a card, then flips from `SCANNING` to `REJECTS UNSAFE / EXCESSIVE`; its status state changes discretely (`discrete-text-sequence`) and the spinner stops at completion.
Scene 3 (7.0–12.0s): “Deterministic contract map” and “Local plan ≤ 2 tests” arrive one per spoken cue via staggered soft entrances (`spring-pop-entrance` in low-overshoot register); a numbered excerpt strip remains visible behind them.
Scene 4 (12.0–16.0s): “PATH + LINE VALIDATION” expands into a receipt whose four rows check off one by one; each check self-draws (`svg-path-draw`) exactly as the VO reaches “validated.”
Scene 5 (16.0–19.221s): `scroll-080.png` fades in as the supporting architectural proof plate while the foreground collapses to one lockup: “AI PROPOSES. EVIDENCE DISPOSES.” All machine motion stops and the held receipt reads.

## Frame 5 — Repository content is data

- scene: An injection string hits the repository boundary, becomes a hash placeholder, and fails to cross into executable or trusted instruction space.
- voiceover: "Repositories are untrusted data, not instructions. ProofEdge rejects binaries, symlinks, dependency trees, oversized files, and injection bait. Model output must match a closed schema, cite scanned paths, and pass evidence checks."
- duration: 17.344s
- transition_in: squeeze
- status: animated
- src: compositions/frames/05-repository-is-data.html
- type: benefit_highlight
- persuasion: Risk reversal
- beat: security + control
- blueprint: grid-card-assemble (Adapt)
- asset_candidates:
- focal: closed-schema trust boundary
- roles: threat cards = midground; trust boundary = foreground; numbered scan grid = background
- sfx: error, impact-bass-1

narrativeRole: Turn security hardening into a product benefit for private engineering workflows.
keyMessage: Local operation is paired with strict trust boundaries, not treated as a security shortcut.

Adapt: keep the accumulating card-array signature, but each item mutates from repository content into an explicit reject reason before the final closed-schema gate lands.
Scene 1 (0.0–3.0s): “REPOSITORIES ARE DATA, NOT INSTRUCTIONS” assembles left-aligned in the upper half; a numbered excerpt panel sits behind it with the injection string already redacted to a hash placeholder.
Scene 2 (3.0–8.0s): four threat cards — binaries, symlinks, dependency trees, oversized files — arrive directly into a two-by-two grid, one per VO cue (`center-outward-expansion` short-path form); each flips from `SEEN` to `REJECTED` after arrival.
Scene 3 (8.0–13.0s): an “INJECTION BAIT” card and a “CLOSED SCHEMA” card populate the second row; path and line chips fill left-to-right (`stat-bars-and-fills`) only when their corresponding validation is named.
Scene 4 (13.0–17.344s): the array clears inward to one foreground gate: `SCANNED PATH + VALID LINE + CLOSED SCHEMA`; an amber outline seals around it via SVG self-draw (`svg-path-draw`) and holds still.

## Frame 6 — Same task, same model, one switch

- scene: A symmetric baseline/KleidiAI comparison holds constant inputs while two independent ABBA result bands animate in with honest positive and inconclusive labels.
- voiceover: "Now the Arm optimization. Same Neoverse N2 V M, llama.cpp commit, Qwen bytes, Q four zero quantization, workload, and threads. Only KleidiAI changes. Exploratory runs found small prefill gains and mixed decode. Then the precommitted confirmation measured zero point five six percent faster prompt processing and four point two eight percent faster generation. Both quality gates passed."
- duration: 28.821s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/06-same-task-one-switch.html
- type: feature_showcase
- persuasion: Statistical proof
- beat: scrutiny + credibility
- blueprint: comparison-split (Adapt)
- asset_candidates: assets/scroll-080.png — captured honest baseline-versus-KleidiAI benchmark panel
- focal: symmetric baseline/KleidiAI metric pair
- roles: scroll-080.png = dim supporting evidence plate; baseline card = foreground left; KleidiAI card = foreground right; causal-control strip = foreground shared header
- sfx: whoosh-short, click-soft, chime

narrativeRole: Make the causal comparison and its modest scope impossible to misunderstand.
keyMessage: The precommitted selected profile confirmed +0.56% prefill and +4.28% decode throughput with both quality gates passing; earlier mixed evidence remains public.

Adapt: keep mirrored equal-weight cards and the static symmetry; use amber for the optimized focal values, neutral cream for baseline, and reserve red only for the directional “no claim” decode label.
Scene 1 (0.0–5.0s): a shared control strip reveals one condition per phrase — Neoverse N2, identical commit, identical Qwen bytes, Q4_0, workload, threads — across the top 22%; `scroll-080.png` is dimmed behind as a source-authentic plate.
Scene 2 (5.0–10.5s): baseline and KleidiAI cards enter from opposite wings with mirrored book-open tilts (`split-tilt-cards`) and settle into a balanced 50/50 comparison; “ONLY KLEIDIAI CHANGES” locks at their inner seam.
Scene 3 (10.5–16.0s): the two exploratory prefill rows count to `+0.53%` and `+0.84%` while their mixed decode rows remain visible and labeled `RETAINED`; this establishes that selection did not erase inconvenient evidence.
Scene 4 (16.0–24.5s): the precommitted confirmation card overlays both sides and counts to `PP1024 +0.56%` and `TG128 +4.28%`; exact means `96.74 → 97.28` and `35.24 → 36.75 tok/s` fill by ratio (`stat-bars-and-fills`).
Scene 5 (24.5–28.821s): `2/2 QUALITY GATES · VALIDITY 1.0 · COVERAGE 1.0 · CANARY 0 · FALLBACK 0` resolves beneath the pair. Both cards settle flat and hold with no drift or breathing.

## Frame 7 — Optimize the system, freeze the gate

- scene: A funnel compresses context and test-plan size, selects the frozen 4-thread profile, lights the I8MM kernel, then stops at two non-negotiable quality gates.
- voiceover: "Kernels are one layer. ProofEdge compresses context, bounds output, tunes batch sizes, and froze the profile before confirmation. Both golden cases passed with zero canary leakage and zero fallback."
- duration: 14.997s
- transition_in: crossfade
- status: animated
- src: compositions/frames/07-freeze-the-gate.html
- type: benefit_highlight
- persuasion: Quality-preserving optimization
- beat: rigor + confidence
- blueprint: dataviz-countup (Adapt)
- asset_candidates:
- focal: frozen optimized profile and two quality gates
- roles: profile funnel = midground; I8MM kernel badge = foreground; golden-case gates = foreground; decision ledger = background
- sfx: riser, click-soft, chime

narrativeRole: Broaden optimization from one kernel toggle to a disciplined, quality-gated system profile.
keyMessage: The selected profile was frozen before confirmation and then passed every frozen output-quality release gate.

Adapt: keep data instruments as the argument, but replace a celebratory hero metric with a release funnel whose final state is conditional on two quality gates.
Scene 1 (0.0–2.5s): “KERNELS ARE ONE LAYER” appears above a compact four-stage funnel; `CONTEXT`, `SCHEMA`, `BATCH`, and `PROFILE` are empty outlined cells.
Scene 2 (2.5–5.5s): context and output cells fill sequentially to `≤ 2 TESTS` and `≤ 4 INPUTS`; progress fills use transform-only bars (`stat-bars-and-fills`) and stop exactly on the spoken bounds.
Scene 3 (5.5–9.0s): the selected profile counts in as `4 THREADS · BATCH 1024 · UBATCH 256 · CHUNK 1`; an I8MM kernel line self-draws into the funnel exit and locks (`svg-path-draw`).
Scene 4 (9.0–12.0s): a commit-shaped “FROZEN BEFORE CONFIRMATION” badge lands; the camera makes one short push-through to the release gate, then fully locks (`coordinate-target-zoom`).
Scene 5 (12.0–14.997s): two gold cards reveal `CASE 1` and `CASE 2`, each with `VALIDITY 1.0`, `COVERAGE 1.0`, `CANARY 0`, and `FALLBACK 0`; after both checks draw, the release pill flips once to `CONFIRMED` and holds without celebration.

## Frame 8 — Why Arm matters

- scene: A compact local model and evidence ledger remain on one Arm64 machine while cloud arrows and private-code exfiltration paths fade away.
- voiceover: "Why Arm? A one point zero six gigabyte local model reasons where the code lives. No repository upload. No remote inference dependency. KleidiAI selects an I eight M M kernel on the measured AArch64 path."
- duration: 16.768s
- transition_in: blur-crossfade
- status: animated
- src: compositions/frames/08-why-arm.html
- type: benefit_highlight
- persuasion: Friction reduction
- beat: privacy + inevitability
- blueprint: fixed-anchor-cycle (Adapt)
- asset_candidates: assets/og-image.png — captured ProofEdge social image for the local-first Arm64 product promise
- focal: fixed local-model core
- roles: og-image.png = dim background product world; local-model core = foreground anchor; privacy/deployment/kernel states = supporting cycle
- sfx: impact-bass-2, click-soft

narrativeRole: Connect the technical optimization to privacy, deployment simplicity, and developer workflow value.
keyMessage: Arm64 enables useful private local reasoning, not merely compatibility.

Adapt: keep the immovable product anchor and cycle three surrounding outcomes at a measured cadence; the anchor never breathes or shifts.
Scene 1 (0.0–2.8s): the fixed anchor `QWEN 1.5B Q4_0 · 1.06 GB · LOCAL` lands center-left over a dimmed crop of `og-image.png`; it pins permanently with zero later movement.
Scene 2 (2.8–6.5s): the adjacent state cycles to `CODE STAYS HERE`; a cloud-upload arrow hard-cuts to a barred outline while the anchor remains untouched (`discrete-text-sequence`).
Scene 3 (6.5–10.0s): the state changes to `NO REMOTE INFERENCE DEPENDENCY`; a loopback endpoint and local ledger card illuminate in amber, growing away from—not over—the anchor.
Scene 4 (10.0–13.0s): the cycle lands on `AARCH64 · SVE2 · I8MM`; a kernel badge draws its internal lane once (`svg-path-draw`) and stops.
Scene 5 (13.0–16.768s): the three outcomes join into the quiet final lockup `PRIVATE · LOCAL · MEASURED ON ARM`; all cycling ceases and the frame holds.

## Frame 9 — Built to be falsifiable

- scene: Raw logs, hashes, runner metadata, quality reports, and commands traverse into one final evidence artifact.
- voiceover: "Every result ships with raw logs, environment metadata, hashes, repeated samples, quality reports, and limitations. Real AArch64 benchmarks are labeled separately from ordinary continuous integration. Reproduce the claim—or falsify it."
- duration: 18.219s
- transition_in: push-slide UP
- status: animated
- src: compositions/frames/09-falsifiable.html
- type: social_proof
- persuasion: Radical transparency
- beat: trust + authority
- blueprint: transcript-scroll-artifact-reveal (Adapt)
- asset_candidates: assets/full-page.png — full captured ProofEdge demo plate; assets/scroll-100.png — captured architecture, falsifiability promise, and repository CTA
- focal: assets/full-page.png
- roles: full-page.png = foreground traversed evidence surface; scroll-100.png = final artifact and held proof card; evidence labels = supporting
- sfx: whoosh, click-soft, chime

narrativeRole: Turn reproducibility itself into the project’s strongest proof signal.
keyMessage: ProofEdge publishes enough evidence for a skeptical judge to rerun or reject every claim.

Adapt: keep the traverse-to-artifact signature and at most two camera moves; use the exact full-page capture for a one-times vertical journey, then reveal the real closing proof section.
Scene 1 (0.0–3.0s): `RAW EVIDENCE, NOT A CLAIM DECK` docks top-left while `full-page.png` fills the width at native scale beneath it; the first page segment shows hero metadata and runner identity.
Scene 2 (3.0–7.5s): the page performs one smooth upward element scroll (`3d-page-scroll` flat variant), passing source/target proof, ABBA controls, and architecture; hash, environment, and repeated-sample labels reveal only as their source sections enter the viewport.
Scene 3 (7.5–11.5s): the scroll decelerates on the falsifiability section; a compact file-chip list cascades in for raw logs, metadata, hashes, samples, quality, and limitations (`dynamic-content-sequencing`).
Scene 4 (11.5–15.5s): the hinge lands on `REAL AARCH64 WORKFLOW`; a selection highlight sweeps the label, and one rapid decelerating zoom-out reveals `scroll-100.png` as the complete final artifact card (`viewport-change`).
Scene 5 (15.5–18.219s): the artifact locks. `REPRODUCE — OR FALSIFY` self-draws below the repository CTA while ordinary CI and native Arm64 evidence sit as visibly separate lanes; no camera or page motion remains.

## Frame 10 — Inspect the proof

- scene: Reproducible commands type into a terminal pill, then resolve into the ProofEdge lockup, repository, demo URL, and Cloud AI label.
- voiceover: "ProofEdge. Evidence before confidence. Open the demo, inspect the source, and rerun the Arm64 evidence. Built for Cloud A I. Ready to be challenged."
- duration: 11.136s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/10-inspect-the-proof.html
- type: cta
- persuasion: Direct proof invitation
- beat: motivation + confidence
- blueprint: prompt-type-submit-generate (Adapt)
- asset_candidates: assets/scroll-100.png — captured closing ProofEdge brand line and reproducibility CTA
- focal: reproducible terminal pill and final ProofEdge lockup
- roles: scroll-100.png = supporting captured closing proof; terminal pill = foreground; repository/demo URLs = foreground final lockup
- sfx: typing, key-press, chime

narrativeRole: End on a concrete, judge-friendly action rather than a generic marketing line.
keyMessage: The public demo, source, and Arm64 evidence are ready for inspection.

Adapt: keep the terminal-command CTA signature; type two real repository commands, then resolve onto the public demo and source rather than implying an install succeeded on screen.
Scene 1 (0.0–1.8s): the captured `scroll-100.png` appears as a quiet supporting proof plate; “INSPECT THE PROOF” demotes upward to make space for the command surface.
Scene 2 (1.8–5.5s): a small `$` chip stretches into a wide terminal pill (`card-morph-anchor`); `python -m pip install -e .` types with a block caret (`discrete-text-sequence`, `context-sensitive-cursor`).
Scene 3 (5.5–8.8s): the first command clears to `proofedge evaluate --cases evaluation/cases`; no fake output is shown. The caret stops as “rerun the Arm64 evidence” is spoken.
Scene 4 (8.8–11.136s): the terminal contracts into the ProofEdge lockup; the repository address, local demo prompt, and `CLOUD AI · NATIVE ARM64` reveal sequentially, then hold to the final frame.
