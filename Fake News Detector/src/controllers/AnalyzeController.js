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
      const useModel = method === "model";
      const result = useModel ? this.nlp.analyzeWithModel(text) : this.nlp.analyzeWithRules(text);
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
      const text = await this.scraper.scrapeArticleText(url);
      const useModel = method === "model";
      const result = useModel ? this.nlp.analyzeWithModel(text) : this.nlp.analyzeWithRules(text);
      res.json({ url, textPreview: text.slice(0, 400), ...result });
    } catch (e) {
      res.status(500).json({ error: e && e.message ? e.message : String(e) });
    }
  }
}


