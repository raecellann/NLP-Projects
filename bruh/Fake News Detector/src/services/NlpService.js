import natural from "natural";
import vader from "vader-sentiment";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

export class NlpService {
  constructor(options = {}) {
    this.tokenizer = new natural.WordTokenizer();
    this.useTfidf = options.useTfidf || process.env.USE_TFIDF === "1";
    this.classifier = this.useTfidf
      ? new natural.LogisticRegressionClassifier()
      : new natural.BayesClassifier();
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    this.modelPath = options.modelPath || path.join(__dirname, "../model.json");
    this.tfidfPath = this.modelPath.replace(/\.json$/, ".tfidf.json");
    this.tfidf = this.useTfidf ? new natural.TfIdf() : null;
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
        if (this.useTfidf) {
          await new Promise((resolve, reject) => {
            natural.LogisticRegressionClassifier.load(this.modelPath, null, (err, classifier) => {
              if (err) return reject(err);
              this.classifier = classifier;
              return resolve();
            });
          });
          // Load TF-IDF corpus for inference
          if (fs.existsSync(this.tfidfPath)) {
            try {
              const docs = JSON.parse(fs.readFileSync(this.tfidfPath, "utf8"));
              if (Array.isArray(docs) && this.tfidf) {
                docs.forEach(d => this.tfidf.addDocument(d));
              }
            } catch {}
          }
        } else {
          await new Promise((resolve, reject) => {
            natural.BayesClassifier.load(this.modelPath, null, (err, classifier) => {
              if (err) return reject(err);
              this.classifier = classifier;
              return resolve();
            });
          });
        }
        this.trainingSummary = { trained: true, metrics: { loadedFromCache: true } };
        return;
      } catch {}
    }
    const dataset = typeof datasetLoaderFn === 'function' ? await datasetLoaderFn() : [];
    if (dataset.length === 0) {
      this.trainingSummary = { trained: false, metrics: { emptyDataset: true } };
      return;
    }
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
    if (this.useTfidf) {
      // Build TF-IDF over training documents
      const preprocessedDocs = trainSet.map(item => this.preprocess(item.text));
      preprocessedDocs.forEach(doc => this.tfidf.addDocument(doc));
      // Convert each training document into a weighted feature object
      preprocessedDocs.forEach((doc, i) => {
        const features = {};
        this.tfidf.listTerms(i).forEach(({ term, tfidf }) => {
          features[term] = tfidf;
        });
        this.classifier.addDocument(features, trainSet[i].label);
      });
      this.classifier.train();
      // Persist TF-IDF corpus for inference on new texts
      try {
        fs.writeFileSync(this.tfidfPath, JSON.stringify(preprocessedDocs), "utf8");
      } catch {}
    } else {
      trainSet.forEach(item => {
        const doc = this.preprocess(item.text);
        this.classifier.addDocument(doc, item.label);
      });
      this.classifier.train();
    }

    let correct = 0;
    const confusion = { fake: { fake: 0, real: 0 }, real: { fake: 0, real: 0 } };
    testSet.forEach(item => {
      let pred;
      if (this.useTfidf) {
        const features = this.#buildTfidfFeatures(this.preprocess(item.text));
        pred = this.classifier.classify(features);
      } else {
        const doc = this.preprocess(item.text);
        pred = this.classifier.classify(doc);
      }
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
    let category;
    let scores;
    if (this.useTfidf) {
      const features = this.#buildTfidfFeatures(doc);
      category = this.classifier.classify(features);
      scores = this.classifier.getClassifications(features);
    } else {
      category = this.classifier.classify(doc);
      scores = this.classifier.getClassifications(doc);
    }
    const sentiment = vader.SentimentIntensityAnalyzer.polarity_scores(text);
    return { text, tokens: doc, predictedCategory: category, scores, sentiment, training: this.trainingSummary.metrics };
  }

  #buildTfidfFeatures(doc) {
    if (!this.tfidf) return {};
    const terms = this.tokenizer.tokenize(doc).filter(t => t && !natural.stopwords.includes(t));
    const stemmed = terms.map(t => natural.PorterStemmer.stem(t));
    const termCounts = stemmed.reduce((acc, t) => {
      acc[t] = (acc[t] || 0) + 1;
      return acc;
    }, {});
    const features = {};
    Object.keys(termCounts).forEach(term => {
      try {
        const idf = typeof this.tfidf.idf === "function" ? this.tfidf.idf(term) : 1;
        features[term] = termCounts[term] * (idf || 0);
      } catch {
        features[term] = termCounts[term];
      }
    });
    return features;
  }

}


