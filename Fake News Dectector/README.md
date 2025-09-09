
## Usage

Install dependencies:
```bash
npm install
```

Rule-based on raw text:
```bash
node index.js --text "Your article text here..."
```

Train/use JS model on raw text:
```bash
node index.js --text-model "Your article text here..."
```

TF-IDF + Logistic Regression (JS-only, improved baseline):
```bash
node index.js --text-tfidf "Your article text here..."
```

Scrape URL(s) then rule-based classify:
```bash
node index.js https://example.com/news/article-123
```
- You can point to a remote API by setting `PY_MODEL_URL` (defaults to `http://127.0.0.1:8000`):
```bash
set PY_MODEL_URL=http://127.0.0.1:8000 && node index.js --py-text "..."
```

### Existing modes
- Rule-based, raw text:
```bash
node index.js --text "..."
```
- JS model, raw text:
```bash
node index.js --text-model "..."
```
- Scrape URL(s) then rule-based:
```bash
node index.js https://example.com/article
```
