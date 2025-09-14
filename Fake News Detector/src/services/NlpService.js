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
        await new Promise((resolve, reject) => {
          natural.BayesClassifier.load(this.modelPath, null, (err, classifier) => {
            if (err) return reject(err);
            this.classifier = classifier;
            return resolve();
          });
        });
        this.trainingSummary = { trained: true, metrics: { loadedFromCache: true } };
        return;
      } catch {}
    }
    const dataset = typeof datasetLoaderFn === 'function' ? await datasetLoaderFn() : [];
    if (dataset.length === 0) {
      this.trainingSummary = { trained: false, metrics: { emptyDataset: true } };
      return;
    }
    // Deterministic RNG for reproducible shuffles (helps avoid label skew variance)
    const seedString = process.env.MODEL_SEED || "fake-news-detector";
    let seed = 1779033703;
    for (let i = 0; i < seedString.length; i++) {
      seed = Math.imul(seed ^ seedString.charCodeAt(i), 3432918353);
      seed = (seed << 13) | (seed >>> 19);
    }
    const rng = () => {
      seed = Math.imul(seed ^ (seed >>> 16), 2246822507);
      seed = Math.imul(seed ^ (seed >>> 13), 3266489909);
      const t = (seed ^= seed >>> 16) >>> 0;
      return (t & 0x7fffffff) / 0x80000000;
    };
    const shuffleInPlace = (arr) => {
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(rng() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }
      return arr;
    };

    // Optional balancing: keep classes at equal count if BALANCE=1
    let working = [...dataset];
    if (process.env.BALANCE === "1") {
      const byLabel = working.reduce((acc, item) => {
        (acc[item.label] = acc[item.label] || []).push(item);
        return acc;
      }, {});
      const labels = Object.keys(byLabel);
      if (labels.length >= 2) {
        const minCount = Math.min(...labels.map(l => byLabel[l].length));
        working = labels.flatMap(l => byLabel[l].slice(0, minCount));
      }
    }

    const sampleEnv = process.env.SAMPLE_SIZE;
    const sampleSize = sampleEnv ? parseInt(sampleEnv, 10) : NaN;
    if (!Number.isNaN(sampleSize) && sampleSize > 0 && sampleSize < working.length) {
      const byLabel = working.reduce((acc, item) => {
        (acc[item.label] = acc[item.label] || []).push(item);
        return acc;
      }, {});
      const labels = Object.keys(byLabel);
      const perLabel = Math.max(1, Math.floor(sampleSize / Math.max(1, labels.length)));
      working = labels.flatMap(l => byLabel[l].slice(0, perLabel));
    }

    const byLabelForSplit = working.reduce((acc, item) => {
      (acc[item.label] = acc[item.label] || []).push(item);
      return acc;
    }, {});
    const trainSet = [];
    const testSet = [];
    Object.values(byLabelForSplit).forEach((arr) => {
      shuffleInPlace(arr);
      const splitIndex = Math.max(1, Math.floor(arr.length * 0.8));
      trainSet.push(...arr.slice(0, splitIndex));
      testSet.push(...arr.slice(splitIndex));
    });
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
    try {
      await new Promise((resolve, reject) => {
        this.classifier.save(this.modelPath, (err) => {
          if (err) return reject(err);
          return resolve();
        });
      });
      this.trainingSummary.metrics.savedTo = this.modelPath;
    } catch (e) {
      try {
        const fallback = path.resolve(process.cwd(), "src/model.json");
        try { fs.mkdirSync(path.dirname(fallback), { recursive: true }); } catch {}
        await new Promise((resolve, reject) => {
          this.classifier.save(fallback, (err) => {
            if (err) return reject(err);
            return resolve();
          });
        });
        this.trainingSummary.metrics.savedTo = fallback;
      } catch (e2) {
        this.trainingSummary.metrics.saveError = (e2 && e2.message) ? e2.message : String(e2);
      }
    }
  }

  analyzeWithModel(text) {
    const doc = this.preprocess(text);
    const category = this.classifier.classify(doc);
    const scores = this.classifier.getClassifications(doc);
    const sentiment = vader.SentimentIntensityAnalyzer.polarity_scores(text);
    return { text, tokens: doc, predictedCategory: category, scores, sentiment, training: this.trainingSummary.metrics };
  }

  analyzeWithRules(text, metadata = {}) {
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

    // Author/Publisher credibility checks
    if (metadata.author) {
      const authorLower = metadata.author.toLowerCase();
      const suspiciousAuthors = ["anonymous", "unknown", "staff", "editor", "admin"];
      if (suspiciousAuthors.some(s => authorLower.includes(s))) {
        reasons.push("suspicious author name");
      }
    }

    if (metadata.publisher) {
      const publisherLower = metadata.publisher.toLowerCase();
      const suspiciousPublishers = ["blog", "wordpress", "tumblr", "medium", "unknown"];
      if (suspiciousPublishers.some(s => publisherLower.includes(s))) {
        reasons.push("unverified publisher");
      }
      
      // Check for known credible sources
      const credibleSources = ["bbc", "cnn", "reuters", "ap", "associated press", "new york times", "washington post", "wall street journal"];
      if (credibleSources.some(s => publisherLower.includes(s))) {
        // Reduce fake score for credible sources
        reasons.push("credible source");
      }
    }

    // No author/publisher is suspicious
    if (!metadata.author && !metadata.publisher) {
      reasons.push("no author/publisher information");
    }

    let score = Math.min(1, reasons.length * 0.2);
    
    // Adjust score based on credibility
    if (reasons.includes("credible source")) {
      score = Math.max(0, score - 0.3); // Reduce fake probability for credible sources
    }
    if (reasons.includes("no author/publisher information")) {
      score = Math.min(1, score + 0.2); // Increase fake probability for missing info
    }

    const predictedCategory = score >= 0.5 ? "fake" : "real";
    const sentiment = vader.SentimentIntensityAnalyzer.polarity_scores(text);
    return { text, predictedCategory, rulesConfidence: score, redFlags: reasons, sentiment };
  }
}


