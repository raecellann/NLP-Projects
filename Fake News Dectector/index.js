import { loadDataset } from "./src/dataset.js";
import { detectNews, detectNewsRules } from "./src/nlp.js";
import { scrapeArticleText } from "./src/scrape.js";
import { trainTfidfLogReg, predictWithTrained } from "./src/tfidf_logreg.js";

(async () => {
  const args = process.argv.slice(2);
  // --text-tfidf "raw text here" → use TF-IDF + Logistic Regression
  const tfidfIdx = args.findIndex(a => a === "--text-tfidf");
  if (tfidfIdx !== -1) {
    const raw = args[tfidfIdx + 1] || "";
    if (!raw) {
      console.error("--text-tfidf requires a value, e.g. --text-tfidf \"Your article text...\"");
      return;
    }
    const trained = await trainTfidfLogReg();
    const pred = predictWithTrained(trained, raw);
    console.log(`📝 Input: ${raw.slice(0, 120)}...`);
    console.log(`➡️ Predicted (tfidf): ${pred.predictedCategory}`);
    console.log({ prediction: pred, metrics: trained.metrics });
    return;
  }
  // --text "raw text here" → use rules directly
  const textFlagIndex = args.findIndex(a => a === "--text");
  if (textFlagIndex !== -1) {
    const raw = args[textFlagIndex + 1] || "";
    if (!raw) {
      console.error("--text requires a value, e.g. --text \"Your article text...\"");
      return;
    }
    const result = detectNewsRules(raw);
    console.log(`📝 Input: ${raw.slice(0, 120)}...`);
    console.log(`➡️ Predicted: ${result.predictedCategory} (rules conf: ${result.rulesConfidence.toFixed(2)})`);
    console.log(result.redFlags.length ? `⚠️ Red flags: ${result.redFlags.join(", ")}` : "No obvious red flags");
    return;
  }

  // --text-model "raw text here" → use trained model
  const textModelIndex = args.findIndex(a => a === "--text-model");
  if (textModelIndex !== -1) {
    const raw = args[textModelIndex + 1] || "";
    if (!raw) {
      console.error("--text-model requires a value, e.g. --text-model \"Your article text...\"");
      return;
    }
    const result = detectNews(raw);
    console.log(`📝 Input: ${raw.slice(0, 120)}...`);
    console.log(`➡️ Predicted: ${result.predictedCategory}`);
    console.log(result);
    return;
  }
  if (args.length > 0) {
    for (const url of args) {
      try {
        console.log(`🔗 Fetching: ${url}`);
        const text = await scrapeArticleText(url);
        const result = detectNewsRules(text);
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

  const dataset = await loadDataset();
  console.log(`✅ Loaded ${dataset.length} samples`);

  dataset.slice(0, 5).forEach((sample) => {
    const result = detectNews(sample.text);
    console.log(`📰 ${sample.text.slice(0, 80)}...`);
    console.log(`➡️ Actual: ${sample.label}, Predicted: ${result.predictedCategory}`);
    console.log(result);
    console.log("");
  });
})();
