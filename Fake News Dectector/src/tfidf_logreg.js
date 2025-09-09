import * as MatrixNS from "ml-matrix";
const Matrix = MatrixNS.Matrix || MatrixNS.default || MatrixNS;
import { loadDataset } from "./dataset.js";

function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]+/g, " ")
    .split(/\s+/)
    .filter(Boolean);
}

function buildTfidf(docs) {
  const df = new Map();
  const tokensPerDoc = docs.map(t => tokenize(t));
  for (const tokens of tokensPerDoc) {
    const unique = new Set(tokens);
    for (const tok of unique) df.set(tok, (df.get(tok) || 0) + 1);
  }
  const vocab = Array.from(df.keys());
  const idf = new Map();
  const N = docs.length;
  for (const term of vocab) {
    const n = df.get(term) || 1;
    idf.set(term, Math.log((N + 1) / (n + 1)) + 1);
  }
  const termIndex = new Map(vocab.map((t, i) => [t, i]));
  const X = Matrix.zeros(N, vocab.length);
  tokensPerDoc.forEach((tokens, i) => {
    const tf = new Map();
    for (const tok of tokens) tf.set(tok, (tf.get(tok) || 0) + 1);
    const maxTf = Math.max(1, ...tf.values());
    for (const [tok, count] of tf.entries()) {
      const j = termIndex.get(tok);
      if (j === undefined) continue;
      const tfNorm = count / maxTf;
      const v = tfNorm * (idf.get(tok) || 0);
      X.set(i, j, v);
    }
  });
  return { X, vocab, idf };
}

function buildTfidfFromVocab(docs, vocab, idf) {
  const termIndex = new Map(vocab.map((t, i) => [t, i]));
  const N = docs.length;
  const X = Matrix.zeros(N, vocab.length);
  docs.forEach((text, i) => {
    const tokens = tokenize(text);
    const tf = new Map();
    for (const tok of tokens) if (termIndex.has(tok)) tf.set(tok, (tf.get(tok) || 0) + 1);
    const maxTf = Math.max(1, ...tf.values());
    for (const [tok, count] of tf.entries()) {
      const j = termIndex.get(tok);
      const tfNorm = count / maxTf;
      const v = tfNorm * (idf.get(tok) || 0);
      X.set(i, j, v);
    }
  });
  return X;
}

function sigmoid(x) {
  return 1 / (1 + Math.exp(-x));
}

function addBias(X) {
  const [rows, cols] = [X.rows, X.columns];
  const Xb = Matrix.zeros(rows, cols + 1);
  for (let i = 0; i < rows; i++) {
    Xb.set(i, 0, 1);
    for (let j = 0; j < cols; j++) Xb.set(i, j + 1, X.get(i, j));
  }
  return Xb;
}

function trainBinaryLogReg(X, y, options = {}) {
  const steps = options.numSteps || 1200;
  const lr = options.learningRate || 5e-3;
  const Xb = addBias(X);
  const [rows, cols] = [Xb.rows, Xb.columns];
  const w = new Array(cols).fill(0);
  for (let step = 0; step < steps; step++) {
    const grad = new Array(cols).fill(0);
    for (let i = 0; i < rows; i++) {
      let z = 0;
      for (let j = 0; j < cols; j++) z += Xb.get(i, j) * w[j];
      const p = sigmoid(z);
      const error = p - y[i];
      for (let j = 0; j < cols; j++) grad[j] += error * Xb.get(i, j);
    }
    for (let j = 0; j < cols; j++) w[j] -= (lr / rows) * grad[j];
  }
  return { weights: w };
}

function predictProbaBinary(model, X) {
  const Xb = addBias(X);
  const [rows, cols] = [Xb.rows, Xb.columns];
  const w = model.weights;
  const probs = new Array(rows);
  for (let i = 0; i < rows; i++) {
    let z = 0;
    for (let j = 0; j < cols; j++) z += Xb.get(i, j) * w[j];
    probs[i] = sigmoid(z);
  }
  return probs;
}

export async function trainTfidfLogReg() {
  const dataset = await loadDataset();
  if (!dataset.length) throw new Error("No dataset");
  const shuffled = [...dataset].sort(() => Math.random() - 0.5);
  const split = Math.max(1, Math.floor(shuffled.length * 0.8));
  const train = shuffled.slice(0, split);
  const test = shuffled.slice(split);

  const labels = Array.from(new Set(shuffled.map(s => s.label))).sort();
  const labelIndex = new Map(labels.map((l, i) => [l, i]));

  const { X: Xtrain, vocab, idf } = buildTfidf(train.map(s => s.text));
  const ytrain = train.map(s => labelIndex.get(s.label));
  const logreg = trainBinaryLogReg(Xtrain, ytrain, { numSteps: 1500, learningRate: 5e-3 });

  const Xtest = buildTfidfFromVocab(test.map(s => s.text), vocab, idf);
  const ytest = test.map(s => s.label);
  const probs = predictProbaBinary(logreg, Xtest);
  const preds = probs.map(p => (p > 0.5 ? labels[1] : labels[0]));

  let correct = 0;
  const confusion = { [labels[0]]: { [labels[0]]: 0, [labels[1]]: 0 }, [labels[1]]: { [labels[0]]: 0, [labels[1]]: 0 } };
  for (let i = 0; i < preds.length; i++) {
    if (preds[i] === ytest[i]) correct++;
    confusion[ytest[i]][preds[i]] += 1;
  }
  const accuracy = preds.length ? correct / preds.length : 1;

  return { model: logreg, vocab, idf, labels, metrics: { accuracy, confusion, size: dataset.length } };
}

export function predictWithTrained(trained, text) {
  const { model, vocab, idf, labels } = trained;
  const X = buildTfidfFromVocab([text], vocab, idf);
  const prob = predictProbaBinary(model, X)[0];
  const pred = prob > 0.5 ? labels[1] : labels[0];
  return { predictedCategory: pred, probabilityFake: prob };
}


