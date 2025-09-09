import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { scrapeArticleText } from "./scrape.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function csvEscape(s) {
  const t = (s || "").replace(/"/g, '""');
  return `"${t}"`;
}

function ensureTrailingNewline(filePath) {
  try {
    const buf = fs.readFileSync(filePath);
    if (buf.length && buf[buf.length - 1] !== 0x0a) fs.appendFileSync(filePath, "\n");
  } catch {}
}

function appendRow(target, title, text) {
  ensureTrailingNewline(target);
  const row = `${csvEscape(title)},${csvEscape(text)}\n`;
  fs.appendFileSync(target, row);
}

async function main() {
  const args = process.argv.slice(2);
  const labelIdx = args.findIndex(a => a === "--label");
  const titleIdx = args.findIndex(a => a === "--title");
  const textIdx = args.findIndex(a => a === "--text");
  const urlIdx = args.findIndex(a => a === "--url");
  const label = labelIdx !== -1 ? (args[labelIdx + 1] || "").toLowerCase() : "";
  let title = titleIdx !== -1 ? (args[titleIdx + 1] || "") : "";
  let text = textIdx !== -1 ? (args[textIdx + 1] || "") : "";
  const url = urlIdx !== -1 ? (args[urlIdx + 1] || "") : "";
  if (!label || !["real", "fake"].includes(label)) {
    console.error("Usage: node src/append_to_dataset.js --label real|fake [--title \"...\"] (--text \"...\" | --url https://...)");
    process.exit(1);
  }
  if (!text && url) {
    try {
      console.log(`Scraping: ${url}`);
      text = await scrapeArticleText(url);
      if (!title) title = (text || "").slice(0, 80);
    } catch (e) {
      console.error("Failed to scrape URL:", e && e.message ? e.message : e);
      process.exit(1);
    }
  }
  if (!text) {
    console.error("Error: provide --text or a valid --url to scrape.");
    process.exit(1);
  }
  const target = path.join(__dirname, "data", label === "real" ? "True.csv" : "Fake.csv");
  appendRow(target, title, text);
  if (url) {
    const logPath = path.join(__dirname, "data", "sources.log");
    fs.appendFileSync(logPath, `${label.toUpperCase()}\t${url}\n`);
  }
  console.log(`Appended to ${label === "real" ? "True.csv" : "Fake.csv"}`);
}

main().catch(e => { console.error(e); process.exit(1); });


