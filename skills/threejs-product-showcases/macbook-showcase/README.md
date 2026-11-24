# MacBook mockup

An open MacBook pushes in from a distance and settles into a gentle float. Its screen either **scrolls a full-page website screenshot** from top to bottom or **loops a video**. The backdrop is sampled from that content, so the set always matches the page.

```
macbook-showcase/
├── build.py                 # builds one self-contained HTML
├── macbook.template.html    # the scene; build.py fills in the placeholders
└── assets/macbook.glb       # the MacBook model (lid open ~89°)
```

## Build

```bash
# 1. A full-page screenshot (or bring your own tall PNG/JPEG)
node ../tools/capture-page.mjs https://your-site.example page.png

# 2. The page
python3 build.py --screenshot page.png --out mockup.html

# Video on the screen instead
python3 build.py --video demo.mp4 --out mockup.html
```

Open `mockup.html` in Chrome. Everything except Three.js is inlined; Three.js loads from jsDelivr, so the first open needs internet.

### Options

| Flag | Default | What it does |
| --- | --- | --- |
| `--backdrop` | `beams` | `beams`: accent-coloured light shafts from above. `tunnel`: ribbed portal. `gradient`: quiet glow. |
| `--accent '#hex'` | sampled | Force the accent colour, e.g. a brand colour |
| `--base '#hex'` | sampled | Force the background colour |
| `--theme dark\|light` | detected | Force the light/dark treatment |
| `--scroll-speed` | `250` | Cruise speed in page px/s, measured at 1300 px width |
| `--no-grain` | off | Disable the fine film grain |
| `--model` | `assets/macbook.glb` | Another MacBook GLB (see the model notes below) |

## What happens at runtime

1. **Palette.** The screen content is downsampled. Its average colour sets the background (near-black for dark pages, a soft tone for light ones). Its strongest saturated hue becomes the accent. The accent tints the backdrop, the rim light and an edge of the studio environment that reflects in the aluminium. `window.showcase.palette` shows the result.
2. **Screen.** The page is fitted to the panel width and a window of it is shown. Pages taller than 8000 px arrive as overlapping tiles; the screen uses whichever tile contains the current window. Videos are cover-cropped into the 16:10 panel.
3. **Motion.**
   - The camera pushes in over 4 s, then dollies about 6% closer for the rest of the shot, with a slow sideways sway.
   - The scroll starts at 3.6 s. It eases in, cruises at a constant speed, and eases to a stop at the bottom.
   - The laptop floats with small, slow sines.
4. **End.** For a screenshot, `window.showcase.duration` is the moment the page reaches the bottom. Interactive pages then hold there while the laptop keeps floating; videos keep looping.

## Stills and video

```bash
cd ../tools && npm install
node render-video.mjs ../macbook-showcase/mockup.html --stills 0.5,4,20   # PNGs
node render-video.mjs ../macbook-showcase/mockup.html mockup.mp4          # 60 fps MP4, ends at the page bottom
```

See `../references/video-export.md` for options and for using the scene inside HyperFrames.

## Tuning in the template

Named constants near the top of the module script:

- `INTRO_DURATION` (4.0 s), `DOLLY_CLOSER` (0.94): camera push and late drift.
- `SCROLL_DELAY` (3.6 s), `SCROLL_EASE` (2.5 s): when the scroll starts, and how long it takes to reach full speed and to stop.
- `fitDistance(0.34, 0.3)` and `fitDistance(0.64, 0.7)` in `resize()`: start and end framing, as the fraction of frame height and width the device fills.
- The `beams()`, `tunnel()` and `gradient()` functions in the backdrop shader. Add a new look as another branch; see `../references/backdrops-and-color.md`.

## Model notes

`assets/macbook.glb` is open at ~89°. The template:

- reparents the lid parts to a hinge at `(0, 0.01485, -0.1054)` with `attach()`, then tilts the lid back 11°;
- normalises the device to 1 unit wide, with its feet on y = 0;
- rebuilds planar UVs on the mesh named exactly `display` (not `display-notch`).

Another model needs its own hinge position and display mesh. `../references/macbook-showcase.md` explains how to find them.

## Check before delivering

- The screen starts at the top of the page, reaches the true bottom, and the text is legible in the settled shot.
- The backdrop colour belongs to the page. If the sampled accent is wrong (e.g. a photo dominates), pass `--accent`.
- The final frame has air below the laptop: nothing is cropped at 16:9, 16:10 or portrait.
- No console errors.
