# Third-Party Notices

ProofEdge interoperates with, but does not vendor or redistribute, these benchmark inputs:

| Component | Pinned identity | Upstream terms |
| --- | --- | --- |
| `llama.cpp` | commit `67d5978bb1ba490070ddbd2a7c59c7ec5a60b7cc` | [MIT](https://github.com/ggml-org/llama.cpp/blob/master/LICENSE) |
| Qwen2.5-Coder-1.5B-Instruct GGUF | revision `f86cb2c1fa58255f8052cc32aeede1b7482d4361`, Q4_0 SHA-256 `aa8353…16e` | [Apache-2.0](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/blob/f86cb2c1fa58255f8052cc32aeede1b7482d4361/LICENSE) |
| KleidiAI | version embedded by the pinned `llama.cpp` checkout | [Upstream license directory](https://github.com/ARM-software/kleidiai/tree/main/LICENSES) |
| Geist / Geist Mono | tag `1.8.0`, commit `91158e012bdc4abd59fa066d0eae9fc11c2c9f24` | [SIL Open Font License 1.1](videos/proofedge-launch/assets/fonts/OFL.txt) |
| `kokoro-onnx` | local narration tooling; generated audio only is retained | [MIT](https://github.com/thewh1teagle/kokoro-onnx/blob/main/LICENSE) |
| Kokoro-82M | local text-to-speech model used to generate narration | [Apache-2.0](https://huggingface.co/hexgrad/Kokoro-82M) |
| HyperFrames bundled sound effects | twelve hash-identified files embedded in the edited launch film | [Pixabay Content License](https://pixabay.com/service/license-summary/) |

The workflow downloads these components directly from their upstream public repositories. Any
redistribution must preserve the notices and terms supplied by those upstream projects.

Python and JavaScript development dependencies are not bundled in the source repository. Their
exact resolved versions are recorded in `requirements-dev.lock` and `demo/package-lock.json`.
Bundled HyperFrames sound-effect source files are not redistributed as standalone assets; they
are resolved from the installed media library and embedded in the edited launch film. Exact file
hashes, cue records, and the distribution boundary are documented in
[`videos/proofedge-launch/SFX_PROVENANCE.md`](videos/proofedge-launch/SFX_PROVENANCE.md).
