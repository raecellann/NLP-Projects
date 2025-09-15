# 🔍 Fake News Detector

A web application that detects fake news using Natural Language Processing (NLP) and Machine Learning techniques. The system can analyze text from multiple sources including direct text input, URLs, and images using OCR technology.

## ✨ Features

- **📝 Text Analysis**: Direct text input analysis
- **🔗 URL Analysis**: Extract and analyze content from news article URLs
- **📷 Image Analysis**: Upload images with text and extract content using OCR
- **🤖 Dual Detection Methods**:
  - **Rules-based**: Fast analysis using predefined patterns and heuristics
  - **Model-based**: Machine learning model trained on news datasets
- **📊 Detailed Results**: Confidence scores, red flags, sentiment analysis, and more
- **🎨 Modern UI**: Beautiful, responsive interface with dark theme

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fake-news-detector
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the application**
   ```bash
   npm start or npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 📖 How to Use

### 1. Analyze Text
- Paste article text directly into the text area
- Choose between Rules or Model analysis method
- Click "Analyze Text"

### 2. Analyze URL
- Enter a news article URL
- Select analysis method
- Click "Analyze URL" to fetch and analyze content

### 3. Analyze Image
- Click the upload area or drag & drop an image
- Select analysis method
- Click "Analyze Image" to extract text and analyze

## 🔧 Analysis Methods

### Rules-Based Detection
- **Speed**: ⚡ Very fast
- **Training**: ❌ No training required
- **Accuracy**: Good for obvious fake news patterns
- **Features**:
  - Urgency word detection
  - Money/transfer keyword analysis
  - Exclamation mark counting
  - Generic greeting detection
  - Link presence analysis
  - Sensational language detection
  - ALL-CAPS word analysis

### Model-Based Detection
- **Speed**: 🐌 Slower (requires processing)
- **Training**: ✅ Uses trained ML model
- **Accuracy**: Higher accuracy for complex cases
- **Features**:
  - Natural language processing
  - Sentiment analysis
  - Text preprocessing and tokenization
  - Bayesian classification

## 📊 Understanding Results

### Prediction Categories
- **🟢 Real**: News appears to be legitimate
- **🔴 Fake**: News shows signs of being fabricated

### Result Components
- **Confidence Score**: How certain the system is (Rules method)
- **Red Flags**: Specific indicators of fake news
- **Sentiment Analysis**: Emotional tone of the content
- **Extracted Text**: For images, shows the OCR-extracted text
- **Raw Data**: Complete analysis details

## 🛠️ Technical Stack

- **Backend**: Node.js, Express.js
- **NLP**: Natural.js, VADER Sentiment
- **OCR**: Tesseract.js
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **File Upload**: Multer
- **Web Scraping**: Axios, Cheerio

## 📁 Project Structure

```
fake-news-detector/
├── public/
│   ├── index.html          # Main UI
│   └── styles.css          # Styling
├── src/
│   ├── controllers/
│   │   └── AnalyzeController.js    # API endpoints
│   ├── repositories/
│   │   └── DatasetRepository.js    # Data loading
│   ├── routes/
│   │   └── analyzeRoutes.js        # Route definitions
│   ├── services/
│   │   ├── NlpService.js           # NLP processing
│   │   └── ScraperService.js       # Web scraping
│   └── server.js                   # Main server
├── package.json
└── README.md
```


## 🚨 Limitations

- **Language**: Currently optimized for English text
- **Image Quality**: OCR accuracy depends on image clarity and text readability
- **Context**: May not understand complex contextual nuances
- **Training Data**: Model accuracy depends on training dataset quality

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📝 References

- Natural.js for NLP capabilities
- Tesseract.js for OCR functionality
- VADER Sentiment for sentiment analysis
- All contributors and the open-source community

## Websites That supports this Application
- New York Times
- PhilStar
- Manila Times
- The Onion (Fake)
- Rappler 
- CNN 
- Inquirer 
- Manila Bulletin
---
