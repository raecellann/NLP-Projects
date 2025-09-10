import { NlpService } from "./src/services/NlpService.js";
import { ScraperService } from "./src/services/ScraperService.js";
import { DatasetRepository } from "./src/repositories/DatasetRepository.js";

(async () => {
  const datasetRepo = new DatasetRepository({ samplePerCsv: process.env.SAMPLE_PER_CSV ? parseInt(process.env.SAMPLE_PER_CSV, 10) : undefined });
  const nlp = new NlpService();
  await nlp.initialize(() => datasetRepo.loadAll());
  const scraper = new ScraperService();
  const args = process.argv.slice(2);
  const textFlagIndex = args.findIndex(a => a === "--text");
  if (textFlagIndex !== -1) {
    const raw = args[textFlagIndex + 1] || "";
    if (!raw) {
      console.error("--text requires a value, e.g. --text \"Your article text...\"");
      return;
    }
    const result = nlp.analyzeWithRules(raw);
    console.log(`📝 Input: ${raw.slice(0, 120)}...`);
    console.log(`➡️ Predicted: ${result.predictedCategory} (rules conf: ${result.rulesConfidence.toFixed(2)})`);
    console.log(result.redFlags.length ? `⚠️ Red flags: ${result.redFlags.join(", ")}` : "No obvious red flags");
    return;
  }
  const textModelIndex = args.findIndex(a => a === "--text-model");
  if (textModelIndex !== -1) {
    const raw = args[textModelIndex + 1] || "";
    if (!raw) {
      console.error("--text-model requires a value, e.g. --text-model \"Your article text...\"");
      return;
    }
    const result = nlp.analyzeWithModel(raw);
    console.log(`📝 Input: ${raw.slice(0, 120)}...`);
    console.log(`➡️ Predicted: ${result.predictedCategory}`);
    console.log(result);
    return;
  }
  if (args.length > 0) {
    for (const url of args) {
      try {
        console.log(`🔗 Fetching: ${url}`);
        const text = await scraper.scrapeArticleText(url);
        const result = nlp.analyzeWithRules(text);
        console.log(`📰 ${text.slice(0, 100)}...`);
        console.log(`➡️ Predicted: ${result.predictedCategory} (rules conf: ${result.rulesConfidence.toFixed(2)})`);
        console.log(result.redFlags.length ? `⚠️ Red flags: ${result.redFlags.join(", ")}` : "No obvious red flags");
        console.log("");
      } catch (e) {
        console.error(`❌ Failed for ${url}:`, e && e.message ? e.message : e);
        if (e && e.response) {
          console.error(`HTTP ${e.response.status}`);
        }
        if (e && e.stack) {
          console.error(e.stack);
        }
      }
    }
    return;
  }

  const dataset = await datasetRepo.loadAll();
  console.log(`✅ Loaded ${dataset.length} samples`);

  dataset.slice(0, 5).forEach((sample) => {
    const result = nlp.analyzeWithModel(sample.text);
    console.log(`📰 ${sample.text.slice(0, 80)}...`);
    console.log(`➡️ Actual: ${sample.label}, Predicted: ${result.predictedCategory}`);
    console.log(result);
    console.log("");
  });
})();
