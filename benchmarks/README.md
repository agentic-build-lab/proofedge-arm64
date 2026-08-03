# Benchmark Protocol

ProofEdge separates claims that are often accidentally conflated:

1. **Runtime A/B:** the same Q4_0 model and `llama.cpp` commit, built with
   `GGML_CPU_KLEIDIAI=OFF` and `ON` on one native Arm64 VM.
2. **Serving configuration:** fixed runtime with one setting changed at a time.
3. **Workflow optimization:** whole-repository context versus evidence-selected context, with the
   same model and runtime.
4. **Composite product result:** only after the first three layers and the quality gate pass.

The native runtime workflow uses an ABBA block order to reduce bias from host drift. Every block
keeps `llama-bench` JSON, stderr, `/usr/bin/time -v`, environment metadata, source/model hashes,
and build logs. QEMU, FVP, and other emulators are never performance evidence.

The first pinned model is the official Apache-2.0
`Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF` Q4_0 artifact. Q4_0 is deliberate: current
`llama.cpp` KleidiAI CPU paths support it, allowing a same-model causal comparison. Q4_K_M may be
evaluated separately but will not be described as a KleidiAI result.

The workflow is manual because it downloads a 1.07 GB public model and builds two runtimes. It
runs on GitHub's `ubuntu-24.04-arm` standard runner: native 4-vCPU Arm64 hardware, not emulation.

