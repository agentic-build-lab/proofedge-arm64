import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the complete public ProofEdge narrative", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  assert.equal(response.headers.get("x-content-type-options"), "nosniff");
  assert.equal(response.headers.get("x-frame-options"), "DENY");
  assert.equal(response.headers.get("referrer-policy"), "no-referrer");
  assert.match(response.headers.get("content-security-policy") ?? "", /frame-ancestors 'none'/);

  const html = await response.text();
  assert.match(html, /<title>ProofEdge — Evidence before confidence<\/title>/i);
  assert.match(html, /Migrations are easy to generate/);
  assert.match(html, /We kept the failed profile—then confirmed the fix\./);
  assert.match(html, /exploratory profile regressed decode by 0\.70%/i);
  assert.match(html, /Run verified replay/);
  assert.match(html, /genuine aarch64 runner/);
  assert.match(html, /Confirmation summary \+ evidence link/);
  assert.match(html, /github\.com\/agentic-build-lab\/proofedge-arm64/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|starter loading/i);
  assert.doesNotMatch(html, /\b[A-Z]:[\\/]/);
  assert.doesNotMatch(html, /Administrator|New project 8/i);
});

test("keeps benchmark claims qualified and production dependencies audited", async () => {
  const [page, consoleSource, layout, packageJson] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/ProofConsole.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
  ]);

  assert.match(page, /\+0\.56%/);
  assert.match(page, /\+4\.28%/);
  assert.match(page, /exploratory profile regressed decode by 0\.70%/i);
  assert.match(page, /same VM, model bytes, quantization, workload, and threads/i);
  assert.match(consoleSource, /browser demo replays|replay fixture/);
  assert.match(consoleSource, /repository code execution/i);
  assert.match(layout, /summary_large_image/);
  assert.match(layout, /\/og\.png/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
  assert.match(packageJson, /"next": "16\.2\.12"/);
  assert.match(packageJson, /"postcss": "8\.5\.25"/);
  assert.match(packageJson, /"sharp": "0\.35\.3"/);
  assert.match(packageJson, /"undici": "7\.29\.0"/);
});

test("self-hosts fonts without leaking build-machine paths", async () => {
  const [styles] = await Promise.all([
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
    access(new URL("../public/fonts/Geist-Variable.woff2", import.meta.url)),
    access(new URL("../public/fonts/GeistMono-Variable.woff2", import.meta.url)),
  ]);

  assert.match(styles, /url\("\/fonts\/Geist-Variable\.woff2"\)/);
  assert.match(styles, /url\("\/fonts\/GeistMono-Variable\.woff2"\)/);
  assert.doesNotMatch(styles, /\b[A-Z]:[\\/]/);
  assert.doesNotMatch(styles, /Administrator|New project 8/i);
});
