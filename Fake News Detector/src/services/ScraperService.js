import axios from "axios";
import { load } from "cheerio";

export class ScraperService {
  constructor(options = {}) {
    this.timeoutMs = options.timeoutMs || 15000;
    this.maxRedirects = options.maxRedirects || 5;
    this.userAgent = options.userAgent || "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";
  }

  async #tryFetch(url) {
    return axios.get(url, {
      headers: {
        "User-Agent": this.userAgent,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
      },
      maxRedirects: this.maxRedirects,
      timeout: this.timeoutMs,
      validateStatus: (s) => s >= 200 && s < 400,
    });
  }

  #cleanText(text) {
    return text.replace(/\s+/g, " ").replace(/[\u200B-\u200D\uFEFF]/g, "").trim();
  }

  #extractMetadata(html) {
    const $ = load(html);
    const metadata = { author: null, publisher: null, title: null, description: null };

    const authorSelectors = [
      'meta[name="author"]',
      'meta[property="article:author"]',
      'meta[property="og:article:author"]',
      '[rel="author"]',
      '.author',
      '.byline',
      '.article-author',
      '[data-author]',
      '.author-name',
      '.writer'
    ];

    for (const selector of authorSelectors) {
      const element = $(selector);
      if (element.length) {
        const author = element.attr('content') || element.text();
        if (author && author.trim()) {
          metadata.author = this.#cleanText(author);
          break;
        }
      }
    }

    const publisherSelectors = [
      'meta[property="og:site_name"]',
      'meta[name="application-name"]',
      'meta[property="article:publisher"]',
      '.site-name',
      '.publisher',
      '.brand',
      'title'
    ];

    for (const selector of publisherSelectors) {
      const element = $(selector);
      if (element.length) {
        let publisher = element.attr('content') || element.text();
        if (publisher && publisher.trim()) {
          if (selector === 'title') {
            publisher = publisher.split(' - ')[0].split(' | ')[0].trim();
          }
          metadata.publisher = this.#cleanText(publisher);
          break;
        }
      }
    }

    const titleSelectors = [
      'meta[property="og:title"]',
      'meta[name="title"]',
      'title'
    ];

    for (const selector of titleSelectors) {
      const element = $(selector);
      if (element.length) {
        const title = element.attr('content') || element.text();
        if (title && title.trim()) {
          metadata.title = this.#cleanText(title);
          break;
        }
      }
    }

    const descSelectors = [
      'meta[property="og:description"]',
      'meta[name="description"]',
      'meta[property="article:description"]'
    ];

    for (const selector of descSelectors) {
      const element = $(selector);
      if (element.length) {
        const description = element.attr('content');
        if (description && description.trim()) {
          metadata.description = this.#cleanText(description);
          break;
        }
      }
    }

    $("script[type='application/ld+json']").each((_, el) => {
      try {
        const json = JSON.parse($(el).contents().text());
        const nodes = Array.isArray(json) ? json : [json];
        for (const node of nodes) {
          if (node && node['@type'] === 'NewsArticle') {
            if (node.author && !metadata.author) {
              metadata.author = this.#cleanText(node.author.name || node.author);
            }
            if (node.publisher && !metadata.publisher) {
              metadata.publisher = this.#cleanText(node.publisher.name || node.publisher);
            }
            if (node.headline && !metadata.title) {
              metadata.title = this.#cleanText(node.headline);
            }
            if (node.description && !metadata.description) {
              metadata.description = this.#cleanText(node.description);
            }
          }
        }
      } catch {}
    });

    return metadata;
  }

  #extractTextFromHtml(html) {
    const $ = load(html);
    let chunks = [];
    
    $("article p, main p, [role='main'] p").each((_, el) => chunks.push($(el).text()));
    
    if (chunks.length === 0) {
      $("[data-component='text-block'] p").each((_, el) => chunks.push($(el).text()));
      $(".ssrcss-uf6wea-RichTextComponentWrapper p").each((_, el) => chunks.push($(el).text()));
    }
    
    if (chunks.length === 0) {
      $(".article-content p, .entry-content p, .post-content p").each((_, el) => chunks.push($(el).text()));
      $(".article-body p, .story-content p, .content p").each((_, el) => chunks.push($(el).text()));
      
      $(".article-content p, .news-content p").each((_, el) => chunks.push($(el).text()));
      
      $(".article-content p, .news-content p, .story-content p").each((_, el) => chunks.push($(el).text()));
      
      $(".article-content p, .entry-content p").each((_, el) => chunks.push($(el).text()));
      
      $(".article-content p, .post-content p").each((_, el) => chunks.push($(el).text()));
      
      $(".article-content p, .story-content p").each((_, el) => chunks.push($(el).text()));
    }
    
    if (chunks.length === 0) {
      $(".content p, .post p, .entry p, .article p").each((_, el) => chunks.push($(el).text()));
    }
    
    if (chunks.length === 0) {
      $("p").each((_, el) => chunks.push($(el).text()));
    }
    
    if (chunks.length === 0) {
      $("script[type='application/ld+json']").each((_, el) => {
        try {
          const json = JSON.parse($(el).contents().text());
          const nodes = Array.isArray(json) ? json : [json];
          for (const node of nodes) {
            if (node && (node.articleBody || node.description)) {
              chunks.push(node.articleBody || node.description);
            }
          }
        } catch {}
      });
    }
    
    const filtered = chunks.map(t => this.#cleanText(t)).filter(t => 
      t.length >= 40 && 
      !/subscribe|cookie|advert|newsletter|accept\s*cookies|follow\s*us|share\s*this|read\s*more|continue\s*reading/i.test(t)
    );
    
    return this.#cleanText(filtered.join(" "));
  }

  async scrapeArticleText(url) {
    let lastError = null;
    
    try {
      const { data } = await this.#tryFetch(url);
      const text = this.#extractTextFromHtml(data);
      const metadata = this.#extractMetadata(data);
      
      if (text.length > 0) {
        console.log(`✅ Successfully scraped ${url} - ${text.length} characters`);
        return { text, metadata };
      } else {
        console.log(`⚠️ No text found in main page for ${url}`);
        lastError = new Error("No text found in main page");
      }
    } catch (error) {
      console.log(`❌ Failed to fetch main page for ${url}:`, error.message);
      lastError = error;
    }
    
    const ampCandidates = [];
    if (!/\.amp(\b|$)/i.test(url)) ampCandidates.push(url.replace(/(#.*)?$/, ".amp"));
    if (!/[?&]outputType=amp(\b|$)/i.test(url)) ampCandidates.push(url + (url.includes("?") ? "&" : "?") + "outputType=amp");
    
    for (const ampUrl of ampCandidates) {
      try {
        console.log(`🔄 Trying AMP version: ${ampUrl}`);
        const { data } = await this.#tryFetch(ampUrl);
        const text = this.#extractTextFromHtml(data);
        const metadata = this.#extractMetadata(data);
        
        if (text.length > 0) {
          console.log(`✅ Successfully scraped AMP version - ${text.length} characters`);
          return { text, metadata };
        }
      } catch (error) {
        console.log(`❌ AMP version failed:`, error.message);
        lastError = error;
      }
    }
    
    const errorMsg = `No readable article text found for ${url}. Last error: ${lastError ? lastError.message : 'Unknown'}`;
    console.log(`❌ ${errorMsg}`);
    throw new Error(errorMsg);
  }
}