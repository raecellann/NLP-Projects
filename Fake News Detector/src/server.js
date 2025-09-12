import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import multer from "multer";
import { NlpService } from "./services/NlpService.js";
import { ScraperService } from "./services/ScraperService.js";
import { DatasetRepository } from "./repositories/DatasetRepository.js";
import { AnalyzeController } from "./controllers/AnalyzeController.js";
import { ResultLogger } from "./services/ResultLogger.js";
import { createAnalyzeRouter } from "./routes/analyzeRoutes.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ 
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed'), false);
    }
  }
});

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

const datasetRepo = new DatasetRepository({ samplePerCsv: process.env.SAMPLE_PER_CSV ? parseInt(process.env.SAMPLE_PER_CSV, 10) : undefined });
const nlp = new NlpService();
await nlp.initialize(() => datasetRepo.loadAll());
const scraper = new ScraperService();
const analyzeController = new AnalyzeController({ 
  nlp, 
  scraper, 
  resultLogger: process.env.LOG_RESULTS === "1" ? new ResultLogger() : null 
});
app.use("/api", createAnalyzeRouter(analyzeController, upload));

// Serve static UI
app.use(express.static(path.join(__dirname, "../public")));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🌐 Server listening on http://localhost:${PORT}`);
});


