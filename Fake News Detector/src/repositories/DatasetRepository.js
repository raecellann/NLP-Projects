import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import csv from "csv-parser";

export class DatasetRepository {
  constructor(options = {}) {
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    this.dataDir = options.dataDir || path.join(__dirname, "../data");
    this.samplePerCsv = options.samplePerCsv;
  }

  async #loadCsv(filePath, label) {
    const rows = [];
    const perLimit = this.samplePerCsv;
    await new Promise((resolve) => {
      let resolved = false;
      let count = 0;
      const stream = fs.createReadStream(filePath);
      const done = () => { if (!resolved) { resolved = true; resolve(); } };
      stream.on("close", done).on("error", done)
        .pipe(csv())
        .on("data", (row) => {
          const title = (row.title || row.headline || "").toString().trim();
          const body = (row.text || "").toString().trim();
          const combined = [title, body].filter(Boolean).join(". ");
          if (combined) {
            rows.push({ text: combined, label });
            count += 1;
            if (Number.isFinite(perLimit) && perLimit > 0 && count >= perLimit) {
              stream.destroy();
            }
          }
        })
        .on("end", done);
    });
    return rows;
  }

  async loadAll() {
    const trueCsvPath = path.join(this.dataDir, "True.csv");
    const fakeCsvPath = path.join(this.dataDir, "Fake.csv");
    const real = await this.#loadCsv(trueCsvPath, "real");
    const fake = await this.#loadCsv(fakeCsvPath, "fake");
    return [...real, ...fake];
  }
}


