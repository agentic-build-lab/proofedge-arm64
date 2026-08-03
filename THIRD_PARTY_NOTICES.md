# Third-Party Notices

ProofEdge interoperates with, but does not vendor or redistribute, these benchmark inputs:

| Component | Pinned identity | Upstream terms |
| --- | --- | --- |
| `llama.cpp` | commit `67d5978bb1ba490070ddbd2a7c59c7ec5a60b7cc` | [MIT](https://github.com/ggml-org/llama.cpp/blob/master/LICENSE) |
| Qwen2.5-Coder-1.5B-Instruct GGUF | revision `f86cb2c1fa58255f8052cc32aeede1b7482d4361`, Q4_0 SHA-256 `aa8353…16e` | [Apache-2.0](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/blob/f86cb2c1fa58255f8052cc32aeede1b7482d4361/LICENSE) |
| KleidiAI | version embedded by the pinned `llama.cpp` checkout | [Upstream license directory](https://github.com/ARM-software/kleidiai/tree/main/LICENSES) |

The workflow downloads these components directly from their upstream public repositories. Any
redistribution must preserve the notices and terms supplied by those upstream projects.

Python and JavaScript development dependencies are not bundled in the source repository. Their
exact resolved versions are recorded in `requirements-dev.lock` and `demo/package-lock.json`.
