# Backdrops and colour

The MacBook mockup's background is not a fixed design. It is generated from the screen content, so the set looks art-directed for each page without anyone picking colours. This file explains how the palette is derived, what the three built-in looks do, and how to add a new one.

## 1. Sampling the palette

`samplePalette()` draws each content source at 48 px wide (a tall page becomes a 48 × ~500 strip) and reads the pixels:

- **Average colour**: the mean of every pixel. It decides light vs dark (luminance < 0.45 is dark) and tints the base.
- **Accent**: pixels with saturation ≥ 0.3 and value ≥ 0.3 vote into 24 hue bins, weighted by `saturation × value²`. Each bin is scored together with half of each neighbour, so a hue that straddles a bin edge isn't split. The winning bin's weighted mean colour is the accent. If saturated pixels make up less than 0.2% of the page, there is no accent and a neutral blue-grey is used.

Sampling the **whole page**, not only the hero, finds the colour the brand repeats: buttons, links, highlights. A single large photo can still win. When it does, pass `--accent`.

`derivePalette()` turns the sample into the shader inputs:

| | Dark page | Light page |
| --- | --- | --- |
| `base` | the page's hue at value 0.045 and saturation ≤ 0.35: a tinted near-black | the page's hue at saturation ≤ 0.12, value × 0.96 (≤ 0.93): a soft version of the page background |
| `accent` | sampled hue, saturation ≥ 0.55, value ≥ 0.9 | sampled hue, saturation ≥ 0.55, value ≥ 0.75 |
| light model | additive: `col + accent × amount` | tint: `mix(col, accent, amount × 0.9)` |

`--accent`, `--base` and `--theme` override each part independently. The result is exposed as `window.showcase.palette` (sRGB 0–1 triplets), which helps when tuning.

The accent also reaches the model:

- the **rim light** is `0.55 + 0.45 × accent`, a pale tint of the accent;
- one **studio-environment softbox** uses the same tint;

so the aluminium picks up the set's colour instead of looking pasted in.

### Colour space

The backdrop `ShaderMaterial` writes values straight to the framebuffer. It has no `colorspace_fragment` and no tone mapping, so sRGB values sampled from the page go in unchanged and come out matching. Don't convert them to linear. The model is tone-mapped (ACES) as usual, and the screen is not tone-mapped.

## 2. The built-in looks

All three share the same uniforms (`uBase`, `uAccent`, `uDark`, `uProgress`, `uTime`, `uAspect`), the same vignette, and a time-seeded grain of ±0.018. Every value is a function of `uTime`, so frames are repeatable.

### `beams` (default)

Five soft shafts of accent light fan down from above the frame centre (`q = p - (0, 0.75)`, angle-space Gaussians). Each drifts by ±0.035 rad and pulses slowly. A soft accent glow sits behind the laptop. Both ramp in with `uProgress` as the camera arrives.

It works for almost anything. It reads as stage lighting on dark pages and as a coloured wash on light ones. Its look descends from launch-video lighting: one light source, one colour.

### `tunnel`

Concentric rounded-rectangle ribs (`sin(d × 195)` on a rounded-box SDF) in the accent colour over an `accent × 0.22` recess, around a white portal. The portal opens with `uProgress` and stops at a half-size of (0.55, 0.34), so ribs stay visible around the settled laptop. A tiny sine warp keeps the ribs from looking machined.

It is loud and editorial. Use it when the page is fairly neutral and the shot needs energy, or for social clips. On a busy, colourful page it competes with the screen.

### `gradient`

A radial lift of the base colour with a faint accent glow behind the laptop. The quietest option. Use it for long scrolls where the content must carry the video, or for light, minimal brands.

## 3. Adding a look

1. Add a branch to the fragment shader: a `vec3 mylook(vec2 p)` function, picked by `uMode`.
2. Register its name in `BACKDROPS` in the template and in `--backdrop` choices in `build.py`.
3. Build it from `uBase` and `uAccent` only, so it stays colour-matched. Use `addLight(col, light, amount)` to brighten on dark sets and tint on light ones.
4. Animate only with `uTime` and `uProgress`. No `Math.random`, no frame counters.
5. Check it on one dark and one light page, and on a page with no strong colour.

Ideas that fit the scene:

- **Horizon:** a soft floor plane gradient with a bright line at the laptop's base height.
- **Aurora:** two slow, low-frequency noise bands in the accent and its complementary hue.
- **Grid:** a perspective grid floor that fades into the base colour.
- **Spotlight:** one cone from above, plus a floor ellipse.

Keep one dominant motion. The camera and the scroll are already moving, so a backdrop that also moves fast fights them.

## 4. Choosing colours by hand

- Use `--accent` with the brand colour when the sample picks a photo colour, or when a design system dictates the colour.
- Use `--base` when the page background is a brand colour (e.g. a cream site that should sit on cream).
- `--theme light` on a dark page gives a light set with a dark device. That high contrast suits product announcements.

Keep the accent saturated and fairly bright. A dull accent makes the beams read as smoke.
