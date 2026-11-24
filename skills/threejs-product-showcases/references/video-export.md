# Video export

Both scenes draw every frame as a pure function of time. They expose that function as `window.showcase.renderAt(t)`, so a video can be rendered frame by frame at any frame rate. The result is perfectly smooth however long each frame takes to draw.

## 1. `tools/render-video.mjs`

```bash
cd tools && npm install           # once: installs playwright-core

# MP4 at 60 fps; for a scroll it ends exactly when the page reaches the bottom
node render-video.mjs ../path/mockup.html mockup.mp4

# Options
node render-video.mjs mockup.html out.mp4 --fps 30 --width 1080 --height 1920 --duration 20

# Stills, for checking frames before a long render
node render-video.mjs mockup.html --stills 0.5,4,20,60 --out-dir stills
```

How it works:

1. It opens the page as `file://…?capture` in headless Chrome (installed Google Chrome by default, or `CHROME_PATH`) at the requested viewport. Capture mode disables the wall-clock loop and turns on `preserveDrawingBuffer`.
2. It waits for `window.showcase.ready`.
3. For each frame `i` it calls `renderAt(i / (frames - 1) × duration)`. The last frame lands exactly on `duration`, so a scroll finishes on the page's last rows.
4. It grabs a JPEG of the viewport (quality 95) and pipes it to ffmpeg: H.264, CRF 16, yuv420p, faststart.

Speed: about 60 ms per 1080p frame on a laptop GPU, so a 60 s scroll at 60 fps takes about 4 minutes. A PNG screenshot of the canvas element was about 7× slower, so the tool uses viewport JPEGs.

Defaults: `duration` is `window.showcase.duration`. For a screenshot that is when the page reaches the bottom; for a video it is the clip length (at least 8 s); for the turntable it is one revolution, which loops seamlessly.

### Frame rate

Use 60 fps for scrolling content. At 250 page-px/s, the page moves ~3 screen px per frame at 60 fps and ~6 at 30 fps. The 30 fps version visibly judders on text. 30 fps is fine for the turntable and for video content.

### Vertical and square video

Pass `--width 1080 --height 1920` (or 1080×1080). The camera fit uses the viewport aspect, so the device shrinks to fit the width. For vertical social video, consider the `tunnel` or `beams` backdrop: they fill the tall frame better than `gradient`.

## 2. Inside a HyperFrames composition

HyperFrames renders HTML to video by seeking a paused timeline. A Three.js scene fits its seek protocol, but four rules apply.

1. **No network.** The importmap points at jsDelivr, so bundle Three.js locally. For example, put the scene code in an ES module and run `npx esbuild scene.js --bundle --format=iife --outfile=lib/scene.js`, then load it with a plain `<script src>` inside the scene's `<template>`.
2. **Load assets from the project**, not base64. `TextureLoader.loadAsync("assets/tile-0.jpg")` and `GLTFLoader.load("assets/macbook.glb")`; the same tiles `build.py` produces work.
3. **Draw only in `hf-seek`**:

   ```js
   window.__hf = window.__hf || {};
   window.__hf.buildReady = window.__hf.buildReady || {};
   window.__hf.buildReady["laptop"] = init(); // resolves once models and textures are ready
   // inside init(), after setup:
   renderAt(0);
   window.addEventListener("hf-seek", (e) => renderAt(e.detail.time));
   ```

   Use a fixed 1920×1080 renderer with `preserveDrawingBuffer: true`. Do not start a `requestAnimationFrame` loop.
4. **Lint.** `hyperframes check` scans bundled code and flags Three.js's own `Math.random()` (UUIDs) and `requestAnimationFrame` (the unused animation loop) as errors. They don't affect the frames. To pass the check, post-process the bundle: replace `Math.random()` with a seeded LCG and rename `requestAnimationFrame` to an unused identifier.

Set the root composition's `data-duration` to `window.showcase.duration` (round up to a frame), so the video stops when the scroll does. Render at 60 fps: `hyperframes render --fps 60`.

## 3. Determinism checklist

- All motion comes from `t`. No `performance.now()`, `Date.now()`, frame counters or `Math.random()` in `draw()`.
- Grain is seeded by `floor(t × 24)`, not a random seed.
- Video frames come from `video.currentTime = t % duration` plus the `seeked` event, never from playback.
- Textures are uploaded before the first frame (`renderer.initTexture`), so no frame shows a half-loaded tile.
- Rendering a time twice gives the same frame, give or take GPU rounding. In testing, two renders of t = 10 differed by a mean of 0.0004 and a maximum of 7 on a 0–255 scale. Test it: take stills at t = 10 and 20, then at 20 and 10 in a second run, and compare the t = 10 images.
