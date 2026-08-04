import type { Metadata } from "next";
import { ProofConsole } from "./ProofConsole";

export const metadata: Metadata = {
  title: "ProofEdge — Evidence before confidence",
  description:
    "A local-first migration assurance agent with auditable evidence and reproducible native Arm64 benchmarks.",
};

const repoUrl = "https://github.com/agentic-build-lab/proofedge-arm64";
const evidenceUrl = `${repoUrl}/blob/main/benchmarks/results/gha-30830782393-summary.json`;

export default function Home() {
  return (
    <main>
      <header className="nav shell">
        <a className="brand" href="#top" aria-label="ProofEdge home">
          <span className="brand-mark">PE</span>
          <span>ProofEdge</span>
        </a>
        <div className="nav-links">
          <a href="#evidence">Evidence</a>
          <a href="#architecture">Architecture</a>
          <a href={repoUrl} target="_blank" rel="noreferrer">
            Source <span aria-hidden="true">↗</span>
          </a>
        </div>
      </header>

      <section id="top" className="hero shell">
        <div className="eyebrow">
          <span className="pulse" /> Cloud AI · Native Arm64 · Local-first
        </div>
        <h1>
          Migrations are easy to generate.
          <span> Evidence is hard.</span>
        </h1>
        <p className="hero-copy">
          ProofEdge compares a source system with its migration, designs differential tests,
          rejects unsupported claims, and produces an auditable evidence ledger—without sending
          private code off the Arm64 machine.
        </p>
        <div className="hero-actions">
          <a className="button primary" href="#console">
            Inspect the proof <span aria-hidden="true">↓</span>
          </a>
          <a className="button secondary" href={evidenceUrl} target="_blank" rel="noreferrer">
            Open raw evidence <span aria-hidden="true">↗</span>
          </a>
        </div>
        <div className="trust-row" aria-label="Verified project facts">
          <div>
            <span className="metric">Neoverse N2</span>
            <span>genuine aarch64 runner</span>
          </div>
          <div>
            <span className="metric">1.06 GB</span>
            <span>identical Q4_0 model</span>
          </div>
          <div>
            <span className="metric">ABBA</span>
            <span>same-host runtime design</span>
          </div>
          <div>
            <span className="metric">MIT</span>
            <span>reproducible and open</span>
          </div>
        </div>
      </section>

      <section id="console" className="console-section shell">
        <div className="section-intro">
          <p className="kicker">The 30-second proof</p>
          <h2>One migration. Three evidence gates.</h2>
          <p>
            This browser demo replays the credential-free deterministic path. Repository content
            is data, not instruction; local-model suggestions pass through the same ledger gate.
          </p>
        </div>
        <ProofConsole />
      </section>

      <section id="evidence" className="evidence-section shell">
        <div className="section-intro compact">
          <p className="kicker">Measured, not massaged</p>
          <h2>We kept the failed profile—then confirmed the fix.</h2>
          <p>
            An exploratory profile regressed decode by 0.70%, and that result remains public. A
            separately frozen profile then passed an independent four-process ABBA confirmation:
            same VM, model bytes, quantization, workload, and threads; only
            <code> GGML_CPU_KLEIDIAI</code> changed.
          </p>
        </div>

        <div className="benchmark-grid">
          <article className="benchmark-card">
            <div className="benchmark-heading">
              <div>
                <span className="label">Prompt processing · pp1024</span>
                <strong>+0.56%</strong>
              </div>
              <span className="status positive">confirmed</span>
            </div>
            <div className="bar-row">
              <span>Baseline</span>
              <div className="bar-track"><i style={{ width: "99.44%" }} /></div>
              <b>96.74 t/s</b>
            </div>
            <div className="bar-row optimized">
              <span>KleidiAI</span>
              <div className="bar-track"><i style={{ width: "100%" }} /></div>
              <b>97.28 t/s</b>
            </div>
            <p>Descriptive within-process bootstrap range: +0.45% to +0.66%.</p>
          </article>

          <article className="benchmark-card">
            <div className="benchmark-heading">
              <div>
                <span className="label">Token generation · tg128</span>
                <strong>+4.28%</strong>
              </div>
              <span className="status positive">confirmed</span>
            </div>
            <div className="bar-row">
              <span>Baseline</span>
              <div className="bar-track"><i style={{ width: "95.90%" }} /></div>
              <b>35.24 t/s</b>
            </div>
            <div className="bar-row optimized">
              <span>KleidiAI</span>
              <div className="bar-track"><i style={{ width: "100%" }} /></div>
              <b>36.75 t/s</b>
            </div>
            <p>Descriptive within-process bootstrap range: +3.68% to +4.91%.</p>
          </article>
        </div>

        <div className="evidence-links">
          <span><b>Hardware:</b> 4-core Arm Neoverse N2, SVE2 + I8MM</span>
          <span><b>Model:</b> Qwen2.5-Coder 1.5B Q4_0, SHA-pinned</span>
          <a href={evidenceUrl} target="_blank" rel="noreferrer">
            Confirmation summary + evidence link <span aria-hidden="true">↗</span>
          </a>
        </div>
      </section>

      <section id="architecture" className="architecture shell">
        <div className="section-intro compact">
          <p className="kicker">Defense in depth</p>
          <h2>AI proposes. Evidence disposes.</h2>
        </div>
        <div className="flow" aria-label="ProofEdge processing architecture">
          <article>
            <span>01</span>
            <h3>Bounded ingestion</h3>
            <p>Symlinks, binaries, dependency trees, oversized files, and excess bytes are rejected.</p>
          </article>
          <i aria-hidden="true">→</i>
          <article>
            <span>02</span>
            <h3>Contract map</h3>
            <p>Public APIs, tests, OpenAPI responses, risk markers, and declared claims become typed facts.</p>
          </article>
          <i aria-hidden="true">→</i>
          <article>
            <span>03</span>
            <h3>Local planning</h3>
            <p>A compact model on llama.cpp proposes high-value differential tests from numbered excerpts.</p>
          </article>
          <i aria-hidden="true">→</i>
          <article>
            <span>04</span>
            <h3>Evidence gate</h3>
            <p>Every cited path and line is validated. Hallucinated references are rejected and counted.</p>
          </article>
        </div>
      </section>

      <section className="principles shell">
        <p className="kicker">Built to be falsifiable</p>
        <div className="principle-grid">
          <h2>ProofEdge does not ask you to trust its answer.</h2>
          <div>
            <p>It gives you the test, the source line, the target line, the model and runtime hashes, the raw timings, and the limitation that could invalidate the result.</p>
            <a className="text-link" href={repoUrl} target="_blank" rel="noreferrer">
              Reproduce from source <span aria-hidden="true">→</span>
            </a>
          </div>
        </div>
      </section>

      <footer className="footer shell">
        <div className="brand"><span className="brand-mark">PE</span><span>ProofEdge</span></div>
        <p>Evidence before confidence. Built for the Arm Create: AI Optimization Challenge.</p>
        <a href={repoUrl} target="_blank" rel="noreferrer">GitHub ↗</a>
      </footer>
    </main>
  );
}
