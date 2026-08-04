#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(process.argv[2] || ".");
const readJson = (name) => JSON.parse(readFileSync(resolve(root, name), "utf8"));
const round3 = (value) => Math.round(value * 1000) / 1000;

function parseScript(markdown) {
  const lines = new Map();
  let frame = null;
  for (const line of markdown.split(/\r?\n/)) {
    const heading = line.match(/^##\s+Line\s+\d+.*\(Frame\s+(\d+)\)/i);
    if (heading) {
      frame = Number(heading[1]);
      continue;
    }
    const spoken = line.match(/^\s{4,}(.+)$/);
    if (frame && spoken) lines.set(frame, spoken[1].trim());
  }
  return lines;
}

function durationSeconds(path) {
  const result = spawnSync(
    "ffprobe",
    ["-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
    { encoding: "utf8" },
  );
  const duration = Number(result.stdout.trim());
  if (result.status !== 0 || !Number.isFinite(duration)) {
    throw new Error(`ffprobe failed for ${path}: ${result.stderr.trim()}`);
  }
  return round3(duration);
}

function pauseAfter(token) {
  if (/[.!?][\"']?$/.test(token)) return 0.22;
  if (/[,;:][\"']?$/.test(token) || /—/.test(token)) return 0.11;
  return 0.035;
}

function wordWeight(token) {
  const letters = token.replace(/[^A-Za-z0-9]/g, "").length;
  return 0.8 + Math.sqrt(Math.max(1, letters));
}

function approximateWords(text, duration) {
  const tokens = text.split(/\s+/).filter(Boolean);
  const pauses = tokens.map(pauseAfter);
  const intro = 0.06;
  const outro = 0.12;
  const pauseTotal = pauses.slice(0, -1).reduce((sum, value) => sum + value, 0);
  const usable = Math.max(0.5, duration - intro - outro - pauseTotal);
  const weights = tokens.map(wordWeight);
  const weightTotal = weights.reduce((sum, value) => sum + value, 0);
  let cursor = intro;
  return tokens.map((text, index) => {
    const start = cursor;
    const end = Math.min(duration - outro, start + (usable * weights[index]) / weightTotal);
    cursor = end + (index === tokens.length - 1 ? 0 : pauses[index]);
    return { id: `w${index}`, text, start: round3(start), end: round3(end) };
  });
}

const script = parseScript(readFileSync(resolve(root, "SCRIPT.md"), "utf8"));
const product = readJson("audio_meta.json");
const engine = readJson("audio_engine_meta.json");
const voices = [];

for (const [frame, text] of [...script.entries()].sort((a, b) => a[0] - b[0])) {
  const relativePath = `assets/voice/${String(frame).padStart(2, "0")}.wav`;
  const absolutePath = resolve(root, relativePath);
  if (!existsSync(absolutePath)) throw new Error(`missing narration for frame ${frame}: ${absolutePath}`);
  const duration = durationSeconds(absolutePath);
  voices.push({ frame, id: String(frame).padStart(2, "0"), path: relativePath, duration_s: duration, words: approximateWords(text, duration) });
}

product.voices = voices.map(({ frame, path, duration_s, words }) => ({ frame, path, duration_s, words }));
engine.voices = voices.map(({ id, path, duration_s, words }) => ({ id, path, duration_s, words }));
engine.total_duration_s = round3(voices.reduce((sum, voice) => sum + voice.duration_s, 0));

writeFileSync(resolve(root, "audio_meta.json"), `${JSON.stringify(product, null, 2)}\n`);
writeFileSync(resolve(root, "audio_engine_meta.json"), `${JSON.stringify(engine, null, 2)}\n`);

console.log(`caption timings: ${voices.length} frames, ${voices.reduce((sum, voice) => sum + voice.words.length, 0)} words, ${engine.total_duration_s}s voice`);
