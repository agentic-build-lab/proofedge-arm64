# ProofEdge launch film

This directory contains the deterministic HyperFrames source for the 168.767-second challenge
video. It uses ten independently authored frame compositions, a frozen local narration track,
burned-in English captions, real captures of the public ProofEdge demo, and no background music.

## Reproduce

From this directory with the HyperFrames CLI available:

```bash
npx hyperframes lint
npx hyperframes check
npx hyperframes render --skill=product-launch-video --quality high --output renders/video.mp4
```

The exact narration text and time ranges are in `SCRIPT.md`; `audio_meta.json` records word timing
and asset identity. Sound effects are resolved from the installed HyperFrames media library and
are intentionally not redistributed in this source repository.

## Media provenance

- Product images are captures of the project-owned public ProofEdge demo.
- Narration was synthesized offline with `kokoro-onnx` and the `am_michael` voice; no remote or
  paid voice service was used.
- Geist and Geist Mono are frozen at `vercel/geist-font` tag `1.8.0`; hashes and the SIL Open Font
  License are under `assets/fonts/`.
- The final rendered MP4 is published as a release asset rather than committed to Git history.
