#!/usr/bin/env node
// Render a built MacBook mockup to MP4, frame by frame, or save stills.
//
//   node render-video.mjs mockup.html out.mp4 [--fps 60] [--width 1920] [--height 1080] [--duration 30]
//   node render-video.mjs mockup.html --stills 0.5,4,20 [--out-dir stills]
//
// The page is opened with ?capture, which disables the wall-clock loop. Each
// frame is drawn with window.showcase.renderAt(t) and captured, so the result
// is smooth and identical on every run regardless of machine speed. By
// default the video ends exactly when the screenshot reaches the bottom of
// the page (window.showcase.duration). Requires ffmpeg for MP4 output.

import { spawn } from "node:child_process";
import { mkdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { launchBrowser, parseArgs } from "./browser.mjs";

const args = parseArgs(process.argv.slice(2), {
  fps: 60,
  width: 1920,
  height: 1080,
  "out-dir": "stills",
});
const [input, out = "mockup.mp4"] = args._;
if (!input) {
  console.error("Usage: node render-video.mjs <mockup.html> [out.mp4] [--fps 60] [--duration s] [--stills t1,t2]");
  process.exit(1);
}

const width = Number(args.width);
const height = Number(args.height);
const url = `${pathToFileURL(resolve(input)).href}?capture`;

const browser = await launchBrowser();
try {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.error("page error:", e.message));
  await page.goto(url, { waitUntil: "load" });
  await page.waitForFunction(() => window.showcase?.ready === true, null, { timeout: 120000 });
  const canvas = page.locator("#stage");

  const frameAt = async (t) => {
    await page.evaluate((time) => window.showcase.renderAt(time), t);
    // The canvas fills the viewport; a high-quality JPEG of the viewport is
    // several times faster to grab than a PNG of the element.
    return page.screenshot({ type: "jpeg", quality: 95 });
  };

  if (args.stills) {
    mkdirSync(args["out-dir"], { recursive: true });
    for (const t of String(args.stills).split(",").map(Number)) {
      const path = join(args["out-dir"], `at-${t}s.png`);
      await page.evaluate((time) => window.showcase.renderAt(time), t);
      await canvas.screenshot({ path });
      console.log(`Wrote ${path}`);
    }
  } else {
    const fps = Number(args.fps);
    const duration = Number(args.duration ?? (await page.evaluate(() => window.showcase.duration)));
    const frames = Math.round(duration * fps);
    console.log(`Rendering ${frames} frames (${duration.toFixed(2)} s at ${fps} fps) to ${out}`);

    const ffmpeg = spawn(
      "ffmpeg",
      [
        "-v", "error", "-y",
        "-f", "image2pipe", "-framerate", String(fps), "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "slow",
        "-movflags", "+faststart", out,
      ],
      { stdio: ["pipe", "inherit", "inherit"] },
    );
    const done = new Promise((ok, fail) =>
      ffmpeg.on("close", (code) => (code === 0 ? ok() : fail(new Error(`ffmpeg exited ${code}`)))),
    );

    const started = Date.now();
    for (let i = 0; i < frames; i++) {
      // The last frame lands exactly on `duration`: the bottom of the page.
      const t = frames > 1 ? (i / (frames - 1)) * duration : 0;
      const png = await frameAt(t);
      if (!ffmpeg.stdin.write(png)) await new Promise((ok) => ffmpeg.stdin.once("drain", ok));
      if (i % fps === 0) {
        const pct = ((i / frames) * 100).toFixed(0);
        process.stdout.write(`\r  ${pct}%  (${((Date.now() - started) / 1000).toFixed(0)} s)`);
      }
    }
    ffmpeg.stdin.end();
    await done;
    console.log(`\rWrote ${out}                    `);
  }
} finally {
  await browser.close();
}
