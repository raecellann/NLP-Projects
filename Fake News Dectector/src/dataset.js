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

  return data;
}
