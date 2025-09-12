import fs from "fs";
import path from "path";

export class ResultLogger {
  constructor(options = {}) {
    const baseDir = options.baseDir || path.join(process.cwd(), "logs");
    const useJsonArray = process.env.LOG_RESULTS_JSON === "1";
    this.useJsonArray = useJsonArray;
    const fileName = options.fileName || (useJsonArray ? "analyses.json" : "analyses.jsonl");
    this.logFilePath = path.join(baseDir, fileName);
    this.ensureDirectoryExists(baseDir);
    if (useJsonArray) {
      this.ensureJsonArrayFile();
    }
  }

  ensureDirectoryExists(directoryPath) {
    try {
      if (!fs.existsSync(directoryPath)) {
        fs.mkdirSync(directoryPath, { recursive: true });
      }
    } catch {
      // avoid impacting main flow
    }
  }

  append(entry) {
    try {
      const payload = {
        timestamp: new Date().toISOString(),
        ...entry
      };
      if (this.useJsonArray) {
        const current = JSON.parse(fs.readFileSync(this.logFilePath, "utf8"));
        current.push(payload);
        fs.writeFileSync(this.logFilePath, JSON.stringify(current, null, 2), { encoding: "utf8" });
      } else {
        fs.appendFileSync(this.logFilePath, JSON.stringify(payload) + "\n", { encoding: "utf8" });
      }
    } catch {
      // swallow errors
    }
  }

  ensureJsonArrayFile() {
    try {
      if (!fs.existsSync(this.logFilePath)) {
        fs.writeFileSync(this.logFilePath, "[]", { encoding: "utf8" });
      } else {
        // Ensure it's a valid array JSON; if not, reset to []
        try {
          const content = fs.readFileSync(this.logFilePath, "utf8");
          const parsed = JSON.parse(content);
          if (!Array.isArray(parsed)) {
            fs.writeFileSync(this.logFilePath, "[]", { encoding: "utf8" });
          }
        } catch {
          fs.writeFileSync(this.logFilePath, "[]", { encoding: "utf8" });
        }
      }
    } catch {
      // ignore
    }
  }
}


