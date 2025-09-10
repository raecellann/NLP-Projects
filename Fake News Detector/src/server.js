import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import { NlpService } from "./services/NlpService.js";
import { ScraperService } from "./services/ScraperService.js";
import { DatasetRepository } from "./repositories/DatasetRepository.js";
import { AnalyzeController } from "./controllers/AnalyzeController.js";
import { createAnalyzeRouter } from "./routes/analyzeRoutes.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

const datasetRepo = new DatasetRepository({ samplePerCsv: process.env.SAMPLE_PER_CSV ? parseInt(process.env.SAMPLE_PER_CSV, 10) : undefined });
const nlp = new NlpService();
await nlp.initialize(() => datasetRepo.loadAll());
const scraper = new ScraperService();
const analyzeController = new AnalyzeController({ nlp, scraper });
app.use("/api", createAnalyzeRouter(analyzeController));

// Serve static UI
app.use(express.static(path.join(__dirname, "../public")));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🌐 Server listening on http://localhost:${PORT}`);
});


