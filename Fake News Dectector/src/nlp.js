import natural from "natural";
import vader from "vader-sentiment";
import { loadDataset } from "./dataset.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

// Create tokenizer and classifier
const tokenizer = new natural.WordTokenizer();
let classifier = new natural.BayesClassifier();

// Text preprocessing: lowercase, remove stopwords, stem
function preprocess(text) {
  const lower = text.toLowerCase();
  const tokens = tokenizer.tokenize(lower);
  const filtered = tokens.filter(t => !natural.stopwords.includes(t));
  const stemmed = filtered.map(t => natural.PorterStemmer.stem(t));
  return stemmed.join(" ");
}

// Load dataset from CSV and train with simple train/test split
async function trainFromCsvAndEvaluate() {
  const dataset = await loadDataset();
  if (!dataset || dataset.length === 0) {
    return { trained: false, metrics: null };
  }

  // Shuffle
  let shuffled = [...dataset].sort(() => Math.random() - 0.5);

  // Optional: sample subset for faster dev training
  const sampleEnv = process.env.SAMPLE_SIZE;
  const sampleSize = sampleEnv ? parseInt(sampleEnv, 10) : NaN;
  if (!Number.isNaN(sampleSize) && sampleSize > 0 && sampleSize < shuffled.length) {
    shuffled = shuffled.slice(0, sampleSize);
  }
  const splitIndex = Math.max(1, Math.floor(shuffled.length * 0.8));
  const trainSet = shuffled.slice(0, splitIndex);
  const testSet = shuffled.slice(splitIndex);

  // Train
  trainSet.forEach(item => {
    const doc = preprocess(item.text);
    classifier.addDocument(doc, item.label);
  });
  classifier.train();

  // Evaluate
  let correct = 0;
  const confusion = { fake: { fake: 0, real: 0 }, real: { fake: 0, real: 0 } };
  testSet.forEach(item => {
    const doc = preprocess(item.text);
    const pred = classifier.classify(doc);
    if (pred === item.label) correct += 1;
    confusion[item.label][pred] += 1;
  });
  const accuracy = testSet.length > 0 ? correct / testSet.length : 1;

  // Basic precision/recall for "fake"
  const tp = confusion.fake.fake;
  const fp = confusion.real.fake;
  const fn = confusion.fake.real;
  const precision = tp + fp === 0 ? 1 : tp / (tp + fp);
  const recall = tp + fn === 0 ? 1 : tp / (tp + fn);

  const metrics = { size: dataset.length, trainSize: trainSet.length, testSize: testSet.length, accuracy, precisionFake: precision, recallFake: recall, confusion };
  if (testSet.length > 0) {
    console.log("[NLP] Trained on CSV", metrics);
  }
  return { trained: true, metrics };
}

// Try to load a cached model to avoid retraining
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const modelPath = path.join(__dirname, "./model.json");
let trainingSummary;

// Allow skipping training entirely (rule-based only)
const skipTraining = process.env.NO_TRAIN === "1";

if (skipTraining) {
  trainingSummary = { trained: false, metrics: { noTrain: true } };
} else if (fs.existsSync(modelPath)) {
  try {
    const json = JSON.parse(fs.readFileSync(modelPath, "utf-8"));
    classifier = natural.BayesClassifier.restore(json);
    trainingSummary = { trained: true, metrics: { loadedFromCache: true } };
  } catch {
    trainingSummary = await trainFromCsvAndEvaluate();
    try { fs.writeFileSync(modelPath, JSON.stringify(classifier.toJSON())); } catch {}
  }
} else {
  trainingSummary = await trainFromCsvAndEvaluate();
  try { fs.writeFileSync(modelPath, JSON.stringify(classifier.toJSON())); } catch {}
}

// Export function
export function detectNews(text) {
  const doc = preprocess(text);
  const category = classifier.classify(doc);
  const scores = classifier.getClassifications(doc);
  const sentiment = vader.SentimentIntensityAnalyzer.polarity_scores(text);

  return {
    text,
    tokens: doc,
    predictedCategory: category,
    scores,
    sentiment,
    training: trainingSummary.metrics
  };
}

// Simple rule-based alternative (no training required)
export function detectNewsRules(text) {
  const reasons = [];
  const lower = text.toLowerCase();

  const urgency = ["urgent", "immediately", "asap", "important", "help", "deadline"];
  if (urgency.some(k => lower.includes(k))) reasons.push("urgency words");

  if (/(\$|usd|million|billion|wire\s*transfer|gift\s*card|bitcoin|crypto)/i.test(text)) {
    reasons.push("money/transfer keywords");
  }
  const exclam = (text.match(/!/g) || []).length;
  if (exclam >= 2) reasons.push("many exclamation marks");
  if (/(dear\s+(friend|customer|user)|greetings\s+my\s+dear\s+friend)/i.test(text)) {
    reasons.push("generic greeting");
  }
  const urls = text.match(/https?:\/\/\S+|www\.[^\s)]+/ig) || [];
  if (urls.length > 0) reasons.push("contains link(s)");

  // Clickbait / sensational language
  const sensational = [
    "shocking", "embarrassing", "disturbing", "you won't believe", "won't believe",
    "exposed", "destroyed", "goes viral", "must see", "epic fail", "insane",
    "unbelievable", "crazy", "jaw-dropping", "mind-blowing"
  ];
  if (sensational.some(k => lower.includes(k))) reasons.push("sensational/clickbait language");

  // Excessive ALL-CAPS words (e.g., names with yelling)
  const words = text.split(/\s+/).filter(Boolean);
  const allCapsWords = words.filter(w => /[A-Z]{3,}/.test(w) && !/^[A-Z]{1}[a-z]+$/.test(w));
  if (allCapsWords.length >= 3) reasons.push("many ALL-CAPS words");

  const score = Math.min(1, reasons.length * 0.2); // 0..1
  const predictedCategory = score >= 0.5 ? "fake" : "real";
  const sentiment = vader.SentimentIntensityAnalyzer.polarity_scores(text);

  return {
    text,
    predictedCategory,
    rulesConfidence: score,
    redFlags: reasons,
    sentiment
  };
}
