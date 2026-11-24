---
name: threejs-product-showcases
description: Build self-contained Three.js 3D showcase pages and videos — a floating MacBook mockup that scrolls a website screenshot or plays a video on its screen, with a backdrop colour-matched to that content, or a white-studio product turntable with a real floor reflection. Use whenever the user asks for a 3D device or laptop mockup, a website shown on a MacBook, a scrolling page on a laptop screen, a product turntable or 360° spin, a reflective product hero, or a video of any of these — even if they don't mention Three.js.
---

# Three.js Product Showcases

Two scenes, each a template plus a build script that inlines everything into one HTML file that opens by double-click:

- **MacBook mockup** (`macbook-showcase/`): an open MacBook pushes in and floats. Its screen scrolls a full-page website screenshot from top to bottom, or loops a video. The backdrop takes its colours from that content, so a red site gets red light and a green site gets green.
- **Product turntable** (`product-turntable/`): any GLB product turning slowly on a glossy white floor with a real planar reflection, a contact shadow, and soft studio light.

Both pages expose a frame-exact render hook, so `tools/render-video.mjs` can turn them into smooth MP4s.

## Pick the starting point

| Request | Read |
| --- | --- |
| Website or app on a laptop, scrolling page, screen demo | `macbook-showcase/README.md`, then `references/macbook-showcase.md` |
| Background look, colours, matching a brand | `references/backdrops-and-color.md` |
| Product spin, 360° view, reflective product hero | `product-turntable/README.md`, then `references/product-turntable.md` |
| An MP4 instead of (or as well as) a web page | `references/video-export.md` |
| Composition, mood, when to use which look | `references/art-direction.md` |
| Something renders wrong | `references/debugging-and-qa.md` |

## Workflow

1. **Get the content.** A tall full-page screenshot (`tools/capture-page.mjs <url>` makes one), a video, or a product GLB. The skill ships no sample content; only the MacBook model is bundled. Only capture sites the user owns or may show.
2. **Build.** Run the folder's `build.py` with the content. Each folder's README covers the options: backdrop, accent colour, scroll speed, pivot and finish.
3. **Look at real frames.** `node tools/render-video.mjs page.html --stills 0.5,4,20` saves stills at given seconds. Check the start, the settled hero, and the end (for a scroll: the page bottom). Also check one portrait viewport.
4. **Deliver** the HTML. Or render a video: `node tools/render-video.mjs page.html out.mp4`. For a scroll it ends exactly when the page reaches the bottom.

The tools need Node 18+, `npm install` in `tools/`, and Google Chrome (or `CHROME_PATH`). The build scripts need Python 3.10+, plus ffmpeg for screenshots.

## Rules that save hours

1. **Use the templates and build scripts; don't rewrite the scene from scratch.** They hold fixes that are easy to lose: the MacBook hinge, screen UVs, texture tiling, the reflector shader and the spin-axis search.
2. **Inline assets.** Browsers block `fetch()` of local files from `file://`. The builds embed base64 and decode it to `ArrayBuffer`s or Blob URLs.
3. **Tall pages are tiled, not shrunk.** WebGL textures top out around 8192 px. The build cuts a long page into overlapping 8000 px tiles at 1300 px wide, so the text stays sharp; it does not squash the page into one texture.
4. **Scroll at a constant speed with eased ends.** Use a trapezoid velocity profile at ~250 page-px/s. Easing the whole scroll makes it feel uneven, and a fixed duration makes long pages race by.
5. **Every frame is a function of time.** `draw(t)` uses no frame counters and no video `currentTime` as a clock. Video export calls `window.showcase.renderAt(t)` per frame, so output is smooth no matter how slowly the machine renders.
6. **Never fake a floor reflection with a mirrored clone.** It shows the inside of the model. Use the `Reflector` setup in the turntable.
7. **The bounding-box centre is rarely the spin axis.** Handles and spouts push it sideways. The turntable defaults to the centroid of the product's base.
8. **Frame the whole device.** The MacBook base is nearer the camera than the screen, so a height-only fit crops it. Keep the height fill around 0.65 or below, and check the last frame.
9. **The screen is unlit content.** Use `MeshBasicMaterial` with `toneMapped: false`, so the page or video keeps its own colours.

## File map

```
threejs-product-showcases/
├── SKILL.md
├── macbook-showcase/
│   ├── README.md
│   ├── build.py                    # --screenshot | --video, --backdrop, --accent …
│   ├── macbook.template.html
│   └── assets/macbook.glb          # the only bundled model
├── product-turntable/
│   ├── README.md
│   ├── build.py                    # --model, --pivot, --finish …
│   └── product-turntable.template.html
├── tools/
│   ├── capture-page.mjs            # full-page screenshot of a URL
│   ├── render-video.mjs            # stills or MP4 via window.showcase.renderAt(t)
│   └── package.json
└── references/
    ├── macbook-showcase.md         # model anatomy, screen maths, tiling, timeline
    ├── backdrops-and-color.md      # palette sampling, the three backdrops, custom looks
    ├── product-turntable.md        # spin axis, reflector, materials, light
    ├── video-export.md             # render-video, HyperFrames, determinism
    ├── art-direction.md
    └── debugging-and-qa.md
```

Keep the pages full-bleed, with no UI chrome or copy unless the user asks for it. The device or product is the hero.
