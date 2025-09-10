import natural from "natural";
import vader from "vader-sentiment";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

export class NlpService {
  constructor(options = {}) {
    this.tokenizer = new natural.WordTokenizer();
    this.classifier = new natural.BayesClassifier();
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    this.modelPath = options.modelPath || path.join(__dirname, "../model.json");
    this.skipTraining = options.skipTraining || process.env.NO_TRAIN === "1";
    this.trainingSummary = { trained: false, metrics: {} };
  }

  preprocess(text) {
    const lower = text.toLowerCase();
    const tokens = this.tokenizer.tokenize(lower);
    const filtered = tokens.filter(t => !natural.stopwords.includes(t));
    const stemmed = filtered.map(t => natural.PorterStemmer.stem(t));
    return stemmed.join(" ");
  }

  async initialize(datasetLoaderFn) {
    if (this.skipTraining) {
      this.trainingSummary = { trained: false, metrics: { noTrain: true } };
      return;
    }
    if (fs.existsSync(this.modelPath)) {
      try {
        const json = JSON.parse(fs.readFileSync(this.modelPath, "utf-8"));
        this.classifier = natural.BayesClassifier.restore(json);
        this.trainingSummary = { trained: true, metrics: { loadedFromCache: true } };
        return;
      } catch {}
    }
    const dataset = typeof datasetLoaderFn === 'function' ? await datasetLoaderFn() : [];
    if (dataset.length === 0) {
      this.trainingSummary = { trained: false, metrics: { emptyDataset: true } };
      return;
    }
    let shuffled = [...dataset].sort(() => Math.random() - 0.5);
    const sampleEnv = process.env.SAMPLE_SIZE;
    const sampleSize = sampleEnv ? parseInt(sampleEnv, 10) : NaN;
    if (!Number.isNaN(sampleSize) && sampleSize > 0 && sampleSize < shuffled.length) {
      shuffled = shuffled.slice(0, sampleSize);
    }
    const splitIndex = Math.max(1, Math.floor(shuffled.length * 0.8));
    const trainSet = shuffled.slice(0, splitIndex);
    const testSet = shuffled.slice(splitIndex);

    trainSet.forEach(item => {
      const doc = this.preprocess(item.text);
      this.classifier.addDocument(doc, item.label);
    });
    this.classifier.train();

    let correct = 0;
    const confusion = { fake: { fake: 0, real: 0 }, real: { fake: 0, real: 0 } };
    testSet.forEach(item => {
      const doc = this.preprocess(item.text);
      const pred = this.classifier.classify(doc);
      if (pred === item.label) correct += 1;
      confusion[item.label][pred] += 1;
    });
    const accuracy = testSet.length > 0 ? correct / testSet.length : 1;

    const tp = confusion.fake.fake;
    const fp = confusion.real.fake;
    const fn = confusion.fake.real;
    const precision = tp + fp === 0 ? 1 : tp / (tp + fp);
    const recall = tp + fn === 0 ? 1 : tp / (tp + fn);

    this.trainingSummary = {
      trained: true,
      metrics: {
        size: dataset.length,
        trainSize: trainSet.length,
        testSize: testSet.length,
        accuracy,
        precisionFake: precision,
        recallFake: recall,
        confusion
      }
    };
    try { fs.writeFileSync(this.modelPath, JSON.stringify(this.classifier.toJSON())); } catch {}
  }

  analyzeWithModel(text) {
    const doc = this.preprocess(text);
    const category = this.classifier.classify(doc);
    const scores = this.classifier.getClassifications(doc);
    const sentiment = vader.SentimentIntensityAnalyzer.polarity_scores(text);
    return { text, tokens: doc, predictedCategory: category, scores, sentiment, training: this.trainingSummary.metrics };
  }

  analyzeWithRules(text) {
    const reasons = [];
    const lower = text.toLowerCase();
    const urgency = ["urgent", "immediately", "asap", "important", "help", "deadline"];
    if (urgency.some(k => lower.includes(k))) reasons.push("urgency words");
    if (/(\$|usd|million|billion|wire\s*transfer|gift\s*card|bitcoin|crypto)/i.test(text)) reasons.push("money/transfer keywords");
    const exclam = (text.match(/!/g) || []).length;
    if (exclam >= 2) reasons.push("many exclamation marks");
    if (/(dear\s+(friend|customer|user)|greetings\s+my\s+dear\s+friend)/i.test(text)) reasons.push("generic greeting");
    const urls = text.match(/https?:\/\/\S+|www\.[^\s)]+/ig) || [];
    if (urls.length > 0) reasons.push("contains link(s)");
    const sensational = [
      "shocking","embarrassing","disturbing","you won't believe","won't believe",
      "exposed","destroyed","goes viral","must see","epic fail","insane",
      "unbelievable","crazy","jaw-dropping","mind-blowing"
    ];
    if (sensational.some(k => lower.includes(k))) reasons.push("sensational/clickbait language");
    const words = text.split(/\s+/).filter(Boolean);
    const allCapsWords = words.filter(w => /[A-Z]{3,}/.test(w) && !/^[A-Z]{1}[a-z]+$/.test(w));
    if (allCapsWords.length >= 3) reasons.push("many ALL-CAPS words");
    const score = Math.min(1, reasons.length * 0.2);
    const predictedCategory = score >= 0.5 ? "fake" : "real";
    const sentiment = vader.SentimentIntensityAnalyzer.polarity_scores(text);
    return { text, predictedCategory, rulesConfidence: score, redFlags: reasons, sentiment };
  }
}


