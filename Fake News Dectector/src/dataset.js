// src/dataset.js
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import csv from "csv-parser";

export async function loadDataset() {
  const data = [];

  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const trueCsvPath = path.join(__dirname, "data", "True.csv");
  const fakeCsvPath = path.join(__dirname, "data", "Fake.csv");

  const perCsvEnv = process.env.SAMPLE_PER_CSV;
  const perCsvLimit = perCsvEnv ? parseInt(perCsvEnv, 10) : NaN;

  // Load True news
  await new Promise((resolve) => {
    let resolved = false;
    let realCount = 0;
    const trueStream = fs.createReadStream(trueCsvPath);
    const done = () => { if (!resolved) { resolved = true; resolve(); } };
    trueStream
      .on("close", done)
      .on("error", done)
      .pipe(csv())
      .on("data", (row) => {
        const title = (row.title || row.headline || "").toString().trim();
        const body = (row.text || "").toString().trim();
        const combined = [title, body].filter(Boolean).join(". ");
        if (combined) {
          data.push({ text: combined, label: "real" });
          realCount += 1;
          if (!Number.isNaN(perCsvLimit) && perCsvLimit > 0 && realCount >= perCsvLimit) {
            trueStream.destroy();
          }
        }
      })
      .on("end", done);
  });

  // Load Fake news
  await new Promise((resolve) => {
    let resolved = false;
    let fakeCount = 0;
    const fakeStream = fs.createReadStream(fakeCsvPath);
    const done = () => { if (!resolved) { resolved = true; resolve(); } };
    fakeStream
      .on("close", done)
      .on("error", done)
      .pipe(csv())
      .on("data", (row) => {
        const title = (row.title || row.headline || "").toString().trim();
        const body = (row.text || "").toString().trim();
        const combined = [title, body].filter(Boolean).join(". ");
        if (combined) {
          data.push({ text: combined, label: "fake" });
          fakeCount += 1;
          if (!Number.isNaN(perCsvLimit) && perCsvLimit > 0 && fakeCount >= perCsvLimit) {
            fakeStream.destroy();
          }
        }
      })
      .on("end", done);
  });

  // Post-process: deduplicate by normalized text
  const seen = new Set();
  const deduped = [];
  for (const item of data) {
    const key = (item.text || "").toLowerCase().replace(/\s+/g, " ").trim();
    if (!key) continue;
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.push(item);
  }

  // Optional: balance classes by downsampling to the minority count
  if (process.env.BALANCE === "1") {
    const real = deduped.filter(d => d.label === "real");
    const fake = deduped.filter(d => d.label === "fake");
    const minCount = Math.min(real.length, fake.length);
    const take = (arr) => arr.sort(() => Math.random() - 0.5).slice(0, minCount);
    return [...take(real), ...take(fake)].sort(() => Math.random() - 0.5);
  }

  return deduped;
}
