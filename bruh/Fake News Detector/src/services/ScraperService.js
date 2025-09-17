import axios from "axios";
import { load } from "cheerio";
import { chromium } from "playwright";

export class ScraperService {
  constructor(options = {}) {
    this.timeoutMs = options.timeoutMs || 15000;
    this.maxRedirects = options.maxRedirects || 5;
    this.userAgent =
      options.userAgent ||
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";
    // Simple in-memory cache to speed up repeated demos
    this.cache = new Map(); // url -> { at: number, result }
    this.cacheTtlMs = options.cacheTtlMs || 5 * 60 * 1000; // 5 minutes
  }

  async #tryFetch(url) {
    return axios.get(url, {
      headers: {
        "User-Agent": this.userAgent,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept":
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
      },
      maxRedirects: this.maxRedirects,
      timeout: this.timeoutMs,
      validateStatus: (s) => s >= 200 && s < 400,
    });
  }

  #cleanText(text) {
    return text
      .replace(/\s+/g, " ")
      .replace(/[\u200B-\u200D\uFEFF]/g, "")
      .trim();
  }

  #extractMetadata(html) {
    const $ = load(html);
    const metadata = { author: null, publisher: null, title: null, description: null, image: null, datePublished: null };

    const metaImageSelectors = [
      'meta[property="og:image"]',
      'meta[name="twitter:image"]',
      'meta[itemprop="image"]',
      'meta[name="image"]'
    ];
    for (const selector of metaImageSelectors) {
      const element = $(selector);
      if (element.length) {
        const img = element.attr("content");
        if (img && img.trim()) {
          metadata.image = img.trim();
          break;
        }
      }
    }
    if (!metadata.image) {
      let imgEl = $("article img[src]").first();
      if (!imgEl.length) imgEl = $("main img[src]").first();
      if (!imgEl.length) imgEl = $("img[src]").first();
      if (imgEl.length) {
        let imgSrc = imgEl.attr("src");
        if (imgSrc && imgSrc.trim()) {
          if (/^\/[^\/]/.test(imgSrc)) {
            const base = $("base").attr("href") || "";
            imgSrc = base ? base + imgSrc : imgSrc;
          }
          metadata.image = imgSrc.trim();
        }
      }
    }

    const dateSelectors = [
      'meta[property="article:published_time"]',
      'meta[name="date"]',
      'meta[itemprop="datePublished"]',
      'meta[name="pubdate"]',
      'meta[name="publish-date"]',
      'meta[name="DC.date.issued"]',
      'time[datetime]'
    ];
    for (const selector of dateSelectors) {
      const element = $(selector);
      if (element.length) {
        const date = element.attr("content") || element.attr("datetime") || element.text();
        if (date && date.trim()) {
          metadata.datePublished = date.trim();
          break;
        }
      }
    }

    const authorSelectors = [
      'meta[name="author"]',
      'meta[property="article:author"]',
      'meta[property="og:article:author"]',
      '[rel="author"]',
      ".author",
      ".byline",
      ".article-author",
      "[data-author]",
      ".author-name",
      ".writer",
    ];

    for (const selector of authorSelectors) {
      const element = $(selector);
      if (element.length) {
        const author = element.attr("content") || element.text();
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
      ".site-name",
      ".publisher",
      ".brand"
    ];

    for (const selector of publisherSelectors) {
      const element = $(selector);
      if (element.length) {
        let publisher = element.attr("content") || element.text();
        if (publisher && publisher.trim()) {
          metadata.publisher = this.#cleanText(publisher);
          break;
        }
      }
    }

    if (!metadata.publisher) {
      const ogSiteName = $('meta[property="og:site_name"]').attr('content');
      if (ogSiteName && ogSiteName.trim()) {
        metadata.publisher = this.#cleanText(ogSiteName);
      }
    }

    const titleSelectors = [
      'meta[property="og:title"]',
      'meta[name="title"]',
      "title",
    ];

    for (const selector of titleSelectors) {
      const element = $(selector);
      if (element.length) {
        const title = element.attr("content") || element.text();
        if (title && title.trim()) {
          metadata.title = this.#cleanText(title);
          break;
        }
      }
    }

    const descSelectors = [
      'meta[property="og:description"]',
      'meta[name="description"]',
      'meta[property="article:description"]',
    ];

    for (const selector of descSelectors) {
      const element = $(selector);
      if (element.length) {
        const description = element.attr("content");
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
          if (node && node["@type"] === "NewsArticle") {
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
            if (node.image && !metadata.image) {
              metadata.image = typeof node.image === 'string' ? node.image : (Array.isArray(node.image) ? node.image[0] : null);
            }
            if (node.datePublished && !metadata.datePublished) {
              metadata.datePublished = node.datePublished;
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
      $(".article-content p, .entry-content p, .post-content p, .td-post-content p").each((_, el) =>
        chunks.push($(el).text())
      );
    }

    if (chunks.length === 0) {
      $("p").each((_, el) => chunks.push($(el).text()));
    }

    const filtered = chunks
      .map((t) => this.#cleanText(t))
      .filter(
        (t) =>
          t.length >= 40 &&
          !/subscribe|cookie|advert|newsletter|accept\s*cookies|follow\s*us|share\s*this|read\s*more|continue\s*reading/i.test(
            t
          )
      );

    return this.#cleanText(filtered.join(" "));
  }

  async scrapeArticleText(url) {
    console.log(`\n[DEBUG] Starting scrape for: ${url}`);

    let lastError = null;

    // Cache check
    try {
      const cached = this.cache.get(url);
      if (cached && (Date.now() - cached.at) < this.cacheTtlMs) {
        console.log("[DEBUG] Returning cached result for", url);
        return cached.result;
      }
    } catch {}

    try {
      console.log("[DEBUG] Trying direct HTTP fetch...");
      const { data } = await this.#tryFetch(url);
      const text = this.#extractTextFromHtml(data);
      const metadata = this.#extractMetadata(data);

      if (text.length > 0) {
        console.log(`[DEBUG] Direct fetch succeeded for ${url}. Text length: ${text.length}`);
        return { text, metadata };
      } else {
        console.log(`[DEBUG] Direct fetch found no text for ${url}.`);
        lastError = new Error("No text found in main page");
      }
    } catch (error) {
      console.log(`[DEBUG] Direct fetch failed for ${url}: ${error.message}`);
      lastError = error;
    }

    try {
      console.log("[DEBUG] Trying Playwright as fallback...");
      const result = await this.scrapeArticleTextPlaywright(url);
      console.log(`[DEBUG] Playwright succeeded for ${url}. Text length: ${result.text.length}`);
      try { this.cache.set(url, { at: Date.now(), result }); } catch {}
      return result;
    } catch (error) {
      console.log(`[DEBUG] Playwright failed for ${url}: ${error.message}`);
      lastError = error;
    }

    throw new Error(`[DEBUG] No readable article text found for ${url}. Last error: ${lastError ? lastError.message : "Unknown"}`);
  }

  async scrapeArticleTextPlaywright(url) {
    let browser;
    try {
      console.log(`[DEBUG] Launching Playwright for ${url}...`);
      browser = await chromium.launch({ headless: true });
      const context = await browser.newContext({
        userAgent: this.userAgent,
        viewport: { width: 1280, height: 800 },
        locale: "en-US",
        timezoneId: "Asia/Manila",
        extraHTTPHeaders: {
          "Accept-Language": "en-US,en;q=0.9",
        },
      });

      const page = await context.newPage();
      page.setDefaultTimeout(10000);
      page.setDefaultNavigationTimeout(30000);
      // Block heavy resource types to speed up scraping
      await page.route('**/*', (route) => {
        const type = route.request().resourceType();
        if (type === 'image' || type === 'media' || type === 'font' || type === 'stylesheet') {
          return route.abort();
        }
        return route.continue();
      });
      await page.goto(url, { timeout: 60000, waitUntil: "domcontentloaded" }); 

      const selectors = [
        "article",
        ".td-post-content",
        ".article-content",
        "main",
        ".content",
        ".story",
        ".entry-content",
        ".post-content"
      ];
      let found = false;
      for (const selector of selectors) {
        try {
          await page.waitForSelector(selector, { timeout: 5000 });
          found = true;
          console.log(`[DEBUG] Found selector: ${selector}`);
          break;
        } catch {}
      }
      if (!found) {
        console.log("[DEBUG] No main content selector found, dumping HTML for inspection...");
        const html = await page.content();
        console.log(html.slice(0, 1000)); 
        throw new Error("No main content selector found");
      }

      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(200); 

      const html = await page.content();
      const text = this.#extractTextFromHtml(html);
      const metadata = this.#extractMetadata(html);

      if (text.length > 0) {
        console.log(`[DEBUG] Playwright extracted text for ${url}. Length: ${text.length}`);
        return { text, metadata };
      } else {
        console.log(`[DEBUG] Playwright found no text for ${url}. Dumping HTML for debugging:`);
        console.log(html.slice(0, 1000));
        throw new Error("No text found with Playwright");
      }
    } catch (error) {
      console.log(`[DEBUG] Playwright error for ${url}: ${error.message}`);
      throw error;
    } finally {
      if (browser) await browser.close();
    }
  }
}