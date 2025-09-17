import Tesseract from 'tesseract.js';

export class AnalyzeController {
  constructor(services) {
    this.nlp = services.nlp;
    this.scraper = services.scraper;
  }

  analyzeText = async (req, res) => {
    try {
      const { text, method } = req.body || {};
      if (!text || typeof text !== "string" || text.trim().length === 0) {
        return res.status(400).json({ error: "text is required" });
      }
      const result = this.nlp.analyzeBlended(text);
      res.json(result);
    } catch (e) {
      res.status(500).json({ error: e && e.message ? e.message : String(e) });
    }
  }

  analyzeUrl = async (req, res) => {
    try {
      const { url, method } = req.body || {};
      if (!url || typeof url !== "string") {
        return res.status(400).json({ error: "url is required" });
      }
      const scrapedData = await this.scraper.scrapeArticleText(url);
      const { text, metadata } = scrapedData;
      const result = this.nlp.analyzeBlended(text);
      res.json({ 
        url, 
        textPreview: text.slice(0, 400), 
        author: metadata.author,
        publisher: metadata.publisher,
        title: metadata.title,
        description: metadata.description,
        image: metadata.image,
        datePublished: metadata.datePublished,
        ...result 
      });
    } catch (e) {
      res.status(500).json({ error: e && e.message ? e.message : String(e) });
    }
  }

  analyzeImage = async (req, res) => {
    try {
      const { method } = req.body || {};
      const file = req.file;
      
      if (!file) {
        return res.status(400).json({ error: "image file is required" });
      }

      const { data: { text } } = await Tesseract.recognize(
        file.buffer,
        'eng',
        {
          logger: m => console.log(m) 
        }
      );

      if (!text || text.trim().length === 0) {
        return res.status(400).json({ error: "No text could be extracted from the image" });
      }
      const result = this.nlp.analyzeBlended(text);
      
      res.json({ 
        imageName: file.originalname,
        extractedText: text,
        textPreview: text.slice(0, 400),
        ...result 
      });
    } catch (e) {
      res.status(500).json({ error: e && e.message ? e.message : String(e) });
    }
  }
}


