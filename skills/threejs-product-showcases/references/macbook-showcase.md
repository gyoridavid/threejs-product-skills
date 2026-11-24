# MacBook mockup: technical notes

Template: `macbook-showcase/macbook.template.html`. Build: `macbook-showcase/build.py`.

The build fills five placeholders:

- `__TITLE__` and `__ARIA_LABEL__`;
- `__CONFIG_JSON__` (backdrop, colour overrides, scroll speed, grain);
- `__MACBOOK_GLB_BASE64__`;
- `<!-- __SCREEN_DATA__ -->`: a `screen-manifest` JSON tag plus one `screen-tile` tag per screenshot tile, or one `screen-video` tag.

## 1. The MacBook model

`assets/macbook.glb` was exported from Blender. It has 105 nodes, 34 meshes, 13 materials and no animations, and the lid is open at ~89°.

| Node | Role |
| --- | --- |
| `deck` | the base |
| `lid`, `lid-glass` | lid shell and glass |
| `display` | the screen panel. Match it exactly: `/^display(?:\.\d+)?$/` |
| `display-notch` | the black notch, which sits in front of the panel |
| `apple-logo`, `apple-logo-leaf`, `camera` | lid details |
| `key-*`, `keyboard-*`, `trackpad`, `speaker-grille-*`, … | the deck |

The main materials are `macbook-space-black`, `macbook-display-panel`, `macbook-bezel`, `macbook-keycap`, `macbook-keyboard-well` and `macbook-trackpad`. The template sets `macbook-space-black` to metalness 0.88 and roughness 0.5, and every material's `envMapIntensity` to 1.45.

### Hinge

```js
const hinge = new THREE.Group();
hinge.position.set(0, 0.01485, -0.1054); // model units, at the back edge of the deck
root.add(hinge);
root.updateMatrixWorld(true);
for (const part of lidParts) hinge.attach(part); // attach keeps the world transform
hinge.rotation.x = THREE.MathUtils.degToRad(-11); // negative tilts the lid back
```

`add()` instead of `attach()` snaps every lid part to the hinge origin: the lid flies off.

### Normalisation and framing

- Scale by `1 / size.x`, so the device is 1 unit wide. Centre X/Z and move it so `bounds.min.y = 0`. The result is about 1 × 0.72 × 0.72.
- The camera target is `(0, size.y * 0.4, 0)`, below the bbox centre. The base is much nearer the camera than the screen, so it projects larger and lower.
- fov 30°, elevation 8°. `fitDistance(fillH, fillW, aspect)` returns the farther of the height-fit and width-fit distances. The start uses (0.34, 0.30); the settled shot uses (0.64, 0.70). Above ~0.7 the base gets cropped at 16:9.

### Using another laptop model

Print the scene graph and `Box3` sizes. Find the panel mesh and the lid meshes by name, and find the hinge where the lid meets the deck. Then check the tilted lid neither intersects the deck nor floats above it. None of the constants above carry over.

## 2. Content on the display

The panel is a flat mesh. Its glTF UVs belong to a tiling material, so the template rebuilds planar UVs from its bounds, with `u` across and `v` up. The panel aspect is about 1.54.

The screen material is `MeshBasicMaterial({ toneMapped: false, side: DoubleSide })`: content is shown exactly as authored.

### Screenshot

Fit the page **width** to the panel and show a vertical window of it:

```
windowPx    = pageWidth / screenAspect          // page rows visible at once (~845 at 1300 wide)
scrollRange = pageHeight - windowPx
top         = progress * scrollRange            // page row at the top of the screen
```

With the default `flipY`, texture `v = 1` is the top of the image. For a tile that starts at page row `tile.top`:

```js
tex.repeat.set(1, windowPx / tile.height);
tex.offset.set(0, 1 - (top - tile.top + windowPx) / tile.height);
```

At `progress = 0` the window shows the page's first rows. At `progress = 1` the offset of the last tile is 0, which is the page's last rows.

**Tiling.** GPUs commonly cap textures at 8192 px, and a full page is often 10,000–20,000 px tall. Squashing it into 8000 px makes a 1300 px-wide page roughly 650 px wide, and the text turns to mush. `build.py` instead scales the page to 1300 px wide and cuts tiles of 8000 px with a 1200 px overlap. The overlap must exceed `windowPx`, so that some tile always contains the whole window. The template switches `material.map` to the containing tile, and pre-uploads every tile with `renderer.initTexture` so the switch never stalls. Tiles get mipmaps and maximum anisotropy so text stays readable while the laptop is small.

Pages shorter than the panel aspect have nothing to scroll; they are shown stretched to the panel. Capture at a narrower width or crop to the panel aspect instead.

### Video

- `VideoTexture` from a muted, looping, `playsinline` `<video>` fed by a Blob URL. Linear filtering, no mipmaps.
- Cover crop: if the video is wider than the panel, map `u` from `u0` to `1 - u0`, where `u0 = (1 - screenAspect / videoAspect) / 2`. If it is taller, do the same on `v`. Keep the subject centred in the source.
- Interactive pages autoplay muted, with a first-gesture fallback. Capture mode seeks to `t % duration` and waits for `seeked` before drawing, so every exported frame shows the right video frame.

## 3. Timeline

Everything visible comes from `draw(t)`, where `t` is seconds since start.

| Element | Formula |
| --- | --- |
| Push-in | `intro = smoothstep((t - 0.1) / 4.0)`; distance from `startDistance` to `endDistance` |
| Late dolly | over the content's remaining time, distance eases a further `× 0.94` |
| Sway | camera x offset `sin(sin(0.22 t) · 0.05) · distance · 0.5`, ramped in after 1 s |
| Float | position ±0.004 x, ±0.009 + ±0.0022 y; rotation ±0.0035 pitch, ±0.012 yaw, ±0.005 roll; ramped in over 1–5 s |
| Backdrop | `uProgress = smoothstep((t - 0.2) / 4.0)`; `uTime = t` |
| Scroll | trapezoid velocity (below), starting at 3.6 s |

### Scroll profile

A long page needs a constant cruise speed; a smoothstep across the whole scroll is slow at both ends and fast in the middle, which reads as uneven. The template accelerates over `a = 2.5` s, cruises, and decelerates over `a`:

```js
const T = scrollTime, v = 1 / (T - a), u = clamp(t - SCROLL_DELAY, 0, T);
progress = u < a     ? v * u * u / (2 * a)
         : u < T - a ? v * a / 2 + v * (u - a)
         :             1 - v * (T - u) * (T - u) / (2 * a);
```

`scrollTime = scrollRange / (speed × pageWidth / 1300) + a`, with `speed` = 250 page-px/s by default. In practice:

- 250 px/s scrolls a 14,000 px page in about 55 s and reads comfortably.
- 600 px/s feels rushed.
- Below 150 px/s it starts to drag.

At 60 fps, 250 px/s moves the on-screen page about 3 px per frame. That is smooth. At 30 fps the same speed judders noticeably, so export scrolls at 60 fps.

`window.showcase.duration = SCROLL_DELAY + scrollTime`. A video export stops on the frame where the page reaches the bottom.

## 4. Render order

```js
renderer.autoClear = false;
renderer.clear();
renderer.render(backdrop.scene, backdrop.camera); // full-screen quad, ignores the camera
renderer.clearDepth();
renderer.render(scene, camera);
```

The backdrop and its palette are covered in `backdrops-and-color.md`.

## 5. Modes

| URL | Behaviour |
| --- | --- |
| `mockup.html` | Interactive wall-clock loop with `requestAnimationFrame`; the page holds at the bottom while the laptop floats |
| `mockup.html?t=12` | Renders the single frame at 12 s, then stops |
| `mockup.html?capture` | Renders t = 0 and waits for `window.showcase.renderAt(t)` calls; `preserveDrawingBuffer` is on |
| `&dpr=2` | Pixel ratio in the two capture modes (default 1) |

`window.showcase` = `{ ready, duration, palette, renderAt(t) }`.

## 6. Pitfalls

| Symptom | Cause | Fix |
| --- | --- | --- |
| Lid floats away from the deck | `add()` instead of `attach()` | reparent with `attach()` |
| Screen material does nothing | matched `display-notch` | match `display` exactly |
| Page upside down | V direction vs `flipY` | top of the screen samples `v = 1`; start at offset `1 - visible` |
| Page stretched | fitted both axes | fit width only, window vertically |
| Blank screen on a long page | texture taller than the GPU limit | build with `build.py`, which tiles the page |
| Blurry text on a long page | page shrunk to fit one texture | use tiles at 1300 px wide |
| Jump when the tile changes | overlap smaller than the window | keep `TILE_OVERLAP` > `windowPx` |
| Scroll feels uneven | eased over its whole length | trapezoid profile |
| Scroll too fast or too slow | duration fixed regardless of page length | set `--scroll-speed`, not a duration |
| Base cropped in the settled shot | height fill too high | keep the settled fills at or below (0.64, 0.70) |
