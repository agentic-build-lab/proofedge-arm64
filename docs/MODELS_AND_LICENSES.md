# Models and Licenses

## ProofEdge

Original ProofEdge source, documentation, challenge-created evaluation fixtures, and the public
demo are distributed under the repository's MIT license unless a file says otherwise.

## Qwen model

The benchmark downloads, but does not redistribute:

- Repository: `Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF`
- Revision: `f86cb2c1fa58255f8052cc32aeede1b7482d4361`
- File: `qwen2.5-coder-1.5b-instruct-q4_0.gguf`
- SHA-256: `aa8353e0d0fca3a0041828701e90db7635197400f040676d11d7798665fa316e`
- Declared license: Apache-2.0

The upstream [model card](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF)
and [license](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/blob/f86cb2c1fa58255f8052cc32aeede1b7482d4361/LICENSE)
remain authoritative.

## llama.cpp and KleidiAI

The workflow clones `llama.cpp` at
`67d5978bb1ba490070ddbd2a7c59c7ec5a60b7cc`; it is not vendored or redistributed here.
`llama.cpp` declares the [MIT license](https://github.com/ggml-org/llama.cpp/blob/master/LICENSE).

KleidiAI is pulled through the pinned `llama.cpp` source path when enabled. Arm describes it as
open-source Arm CPU micro-kernels and distributes it under the license files in its upstream
[`LICENSES` directory](https://github.com/ARM-software/kleidiai/tree/main/LICENSES). ProofEdge does
not collapse that directory into a single license label or redistribute its code.

## Demo dependencies and generated media

Exact JavaScript dependency versions are in `demo/package-lock.json`; their upstream licenses
apply. The social-preview image was generated specifically for ProofEdge and contains no stock
asset supplied by a third party.

This inventory is factual project documentation, not legal advice.
