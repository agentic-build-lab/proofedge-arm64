"use client";

import { useEffect, useState } from "react";

type Phase = "ready" | "running" | "complete";

const findings = [
  {
    code: "CONTRACT",
    title: "Refund reason silently removed",
    detail: "Source accepts reason=None; target accepts order_id only.",
    evidence: "source/pricing.py:8 ↔ target/pricing.py:11",
    tone: "amber",
  },
  {
    code: "INJECTION",
    title: "Repository instruction isolated",
    detail: "“Ignore previous instructions…” remained untrusted text.",
    evidence: "target/REPOSITORY_NOTE.md:3",
    tone: "cyan",
  },
  {
    code: "CLAIM",
    title: "Completeness claim rejected",
    detail: "The cited benchmark artifact does not exist in the scan.",
    evidence: "manifest.json → NONEXISTENT-BENCHMARK.json",
    tone: "red",
  },
];

export function ProofConsole() {
  const [phase, setPhase] = useState<Phase>("ready");
  const [profile, setProfile] = useState<"deterministic" | "local-model">("deterministic");

  useEffect(() => {
    if (phase !== "running") return;
    const timer = window.setTimeout(() => setPhase("complete"), 950);
    return () => window.clearTimeout(timer);
  }, [phase]);

  const run = () => {
    setPhase("running");
  };

  return (
    <div className="proof-console">
      <div className="console-topbar">
        <div className="window-dots" aria-hidden="true"><i /><i /><i /></div>
        <div className="console-title">proofedge / python-refund-v2</div>
        <div className="verified-chip"><span /> replay fixture · public</div>
      </div>

      <div className="console-controls">
        <div className="segmented" aria-label="Analysis profile">
          <button
            className={profile === "deterministic" ? "active" : ""}
            onClick={() => { setProfile("deterministic"); setPhase("ready"); }}
          >
            Deterministic
          </button>
          <button
            className={profile === "local-model" ? "active" : ""}
            onClick={() => { setProfile("local-model"); setPhase("ready"); }}
          >
            Local-model gate
          </button>
        </div>
        <button className="run-button" onClick={run} disabled={phase === "running"}>
          {phase === "running" ? "Verifying…" : phase === "complete" ? "Run again" : "Run verified replay"}
          <span aria-hidden="true">{phase === "running" ? "◌" : "▶"}</span>
        </button>
      </div>

      <div className="console-grid">
        <div className="code-pane">
          <div className="pane-label"><span>SOURCE</span> pricing.py</div>
          <pre aria-label="Source refund function"><code><em>08</em> <b>def</b> refund(order_id, reason=<u>None</u>):{"\n"}<em>09</em>   <b>return</b> &#123;{"\n"}<em>10</em>     <s>&quot;reason&quot;: reason,</s>{"\n"}<em>11</em>     &quot;status&quot;: &quot;accepted&quot;{"\n"}<em>12</em>   &#125;</code></pre>
        </div>
        <div className="code-pane target-pane">
          <div className="pane-label"><span>TARGET</span> pricing.py</div>
          <pre aria-label="Target refund function"><code><em>11</em> <b>def</b> refund(order_id):{"\n"}<em>12</em>   <b>return</b> &#123;{"\n"}<em>13</em>     <mark>&quot;reason&quot;: None,</mark>{"\n"}<em>14</em>     &quot;status&quot;: &quot;accepted&quot;{"\n"}<em>15</em>   &#125;</code></pre>
        </div>
        <div className={`ledger-pane phase-${phase}`} aria-live="polite">
          <div className="pane-label"><span>EVIDENCE LEDGER</span> schema 1.0</div>
          {phase === "ready" && (
            <div className="empty-state">
              <i>PE</i>
              <p>Ready to verify the frozen public fixture.</p>
              <span>No credentials. No repository code execution.</span>
            </div>
          )}
          {phase === "running" && (
            <div className="scan-state">
              <div className="scan-line"><span /> Mapping public contracts</div>
              <div className="scan-line"><span /> Validating evidence paths</div>
              <div className="scan-line"><span /> Isolating repository instructions</div>
            </div>
          )}
          {phase === "complete" && (
            <div className="finding-list">
              {findings.map((finding, index) => (
                <article key={finding.code} style={{ animationDelay: `${index * 90}ms` }}>
                  <span className={`finding-code ${finding.tone}`}>{finding.code}</span>
                  <h3>{finding.title}</h3>
                  <p>{finding.detail}</p>
                  <code>{finding.evidence}</code>
                </article>
              ))}
              <div className="ledger-result">
                <span>3 evidence-backed findings</span>
                <b>{profile === "local-model" ? "AI suggestions gated" : "Static checks passed"}</b>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
