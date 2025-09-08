import axios from "axios";
import { load } from "cheerio";

function cleanText(text) {
  return text
    .replace(/\s+/g, " ")
    .replace(/[\u200B-\u200D\uFEFF]/g, "")
    .trim();
}

async function tryFetch(url) {
  return axios.get(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    },
    maxRedirects: 5,
    timeout: 15000,
    validateStatus: (s) => s >= 200 && s < 400,
  });
}

function extractTextFromHtml(html) {
  const $ = load(html);
  let chunks = [];

  // Generic
  $("article p, main p, [role='main'] p").each((_, el) => chunks.push($(el).text()));

  // BBC specific blocks
  if (chunks.length === 0) {
    $("[data-component='text-block'] p").each((_, el) => chunks.push($(el).text()));
    $(".ssrcss-uf6wea-RichTextComponentWrapper p").each((_, el) => chunks.push($(el).text()));
  }

  // Fallback: all paragraphs
  if (chunks.length === 0) {
    $("p").each((_, el) => chunks.push($(el).text()));
  }

  // JSON-LD articleBody
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

  const filtered = chunks
    .map(t => cleanText(t))
    .filter(t => t.length >= 40 && !/subscribe|cookie|advert|newsletter|accept\s*cookies/i.test(t));

  return cleanText(filtered.join(" "));
}

export async function scrapeArticleText(url) {
  // 1) Try original URL
  try {
    const { data } = await tryFetch(url);
    const text = extractTextFromHtml(data);
    if (text.length > 0) return text;
  } catch {}

  // 2) Try AMP variants if not already AMP
  const ampCandidates = [];
  if (!/\.amp(\b|$)/i.test(url)) ampCandidates.push(url.replace(/(#.*)?$/, ".amp"));
  if (!/[?&]outputType=amp(\b|$)/i.test(url)) ampCandidates.push(url + (url.includes("?") ? "&" : "?") + "outputType=amp");

  for (const ampUrl of ampCandidates) {
    try {
      const { data } = await tryFetch(ampUrl);
      const text = extractTextFromHtml(data);
      if (text.length > 0) return text;
    } catch {}
  }

  throw new Error("No readable article text found (tried normal and AMP)");
}


