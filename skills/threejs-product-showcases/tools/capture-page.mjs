#!/usr/bin/env node
// Capture a full-page screenshot of a website for the MacBook mockup.
//
//   node capture-page.mjs https://example.com page.png [--width 1440] [--height 900] [--wait 1500]
//
// Before the screenshot the page is scrolled from top to bottom in steps, so
// lazy-loaded images and scroll-triggered sections are rendered, then it
// returns to the top. Only capture sites you have the right to show.

import { launchBrowser, parseArgs } from "./browser.mjs";

const args = parseArgs(process.argv.slice(2), { width: 1440, height: 900, wait: 1500 });
const [url, out = "page.png"] = args._;
if (!url) {
  console.error("Usage: node capture-page.mjs <url> [out.png] [--width 1440] [--height 900] [--wait 1500]");
  process.exit(1);
}

const browser = await launchBrowser();
try {
  const page = await browser.newPage({
    viewport: { width: Number(args.width), height: Number(args.height) },
    deviceScaleFactor: 1,
  });
  await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
  await page.waitForTimeout(Number(args.wait));

  // Walk down the page so lazy content loads, then return to the top.
  const step = Math.round(Number(args.height) * 0.6);
  let height = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < height; y += step) {
    await page.evaluate((top) => window.scrollTo(0, top), y);
    await page.waitForTimeout(200);
    height = await page.evaluate(() => document.documentElement.scrollHeight);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(Number(args.wait));

  await page.screenshot({ path: out, fullPage: true });
  const finalHeight = await page.evaluate(() => document.documentElement.scrollHeight);
  console.log(`Wrote ${out} (${args.width}x${finalHeight})`);
} finally {
  await browser.close();
}
