#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const cueTimes = new Map([
  ["01:impact-bass-1", 0.0], ["01:click-soft", 8.3],
  ["02:whoosh-cinematic", 2.5], ["02:chime", 10.5],
  ["03:click", 3.0], ["03:error", 7.5], ["03:chime", 12.0],
  ["04:riser", 0.0], ["04:click-soft", 6.0], ["04:chime", 16.1],
  ["05:error", 3.6], ["05:impact-bass-1", 10.2],
  ["06:whoosh-short", 0.0], ["06:click-soft", 9.5], ["06:chime", 25.0],
  ["07:riser", 0.0], ["07:click-soft", 3.0], ["07:chime", 11.5],
  ["08:impact-bass-2", 0.0], ["08:click-soft", 11.0],
  ["09:whoosh", 0.0], ["09:click-soft", 9.1], ["09:chime", 15.3],
  ["10:typing", 2.5], ["10:key-press", 6.3], ["10:chime", 7.4],
]);

for (const path of ["audio_meta.json", "audio_engine_meta.json"]) {
  const document = JSON.parse(fs.readFileSync(path, "utf8"));
  for (const cue of document.sfx ?? []) {
    const frame = cue.id ?? cue.frame;
    const name = cue.name ?? pathModuleName(cue.file);
    const key = `${String(frame).padStart(2, "0")}:${name}`;
    if (!cueTimes.has(key)) throw new Error(`Missing timing for ${key}`);
    cue.offset_s = cueTimes.get(key);
  }
  fs.writeFileSync(path, `${JSON.stringify(document, null, 2)}\n`, "utf8");
}

console.log(`Applied ${cueTimes.size} authored SFX cue timings.`);

function pathModuleName(file) {
  return path.basename(file, path.extname(file));
}
