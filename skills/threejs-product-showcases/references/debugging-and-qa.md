# Debugging and QA

A page can build, load and run without errors and still be wrong in ways only a real frame shows. These are the checks that catch real problems.

## 1. Look at frames, not just the build

```bash
cd tools && npm install
node render-video.mjs ../out/mockup.html --stills 0.5,4,20 --out-dir stills
node render-video.mjs ../out/mockup.html --stills 4 --width 390 --height 844 --out-dir stills-portrait
```

Check, for the MacBook:

- the start: the set and laptop are visible, with no loader text;
- the settle (~4 s): the page is legible and the laptop is whole, with air below;
- the end (`window.showcase.duration`): the page shows its true last rows;
- a portrait viewport.

For the turntable, check t = 0 and a quarter-turn later.

`render-video.mjs` runs headless Chrome and prints page errors. For an interactive check, open the HTML in Chrome with DevTools open. The page sets `window.showcase` once it is ready, so `window.showcase.palette` and `window.showcase.duration` are available in the console.

Test viewports: 1920×1080, 1440×900, 1280×800, 390×844.

## 2. Symptom → cause → fix

### Screen

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Black screen | `display` mesh not found, video not decoded, autoplay blocked | match `display` exactly; muted + `playsinline`; in capture mode the video is seeked, not played |
| Image upside down | V direction vs `flipY` | top of the screen = texture `v = 1` |
| Stretched or squashed page | fitted both axes | fit width; window vertically |
| Blank screen on long pages | texture over the GPU limit | build with `build.py`: it tiles at ≤ 8000 px |
| Blurry text | page shrunk to fit one texture, or captured too narrow | tiles at 1300 px; capture at 1280–1440 px wide |
| Content jumps mid-scroll | tile overlap smaller than the visible window | keep `TILE_OVERLAP` > page width / 1.54 |
| Scroll ends early or late | offset maths off | at progress 1 the last tile's offset must be 0 |
| Scroll uneven | eased over its whole length | trapezoid profile (constant cruise) |
| Scroll judders in video | 30 fps export | export at 60 fps |

### Model and camera

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Lid floats or detaches | `add()` instead of `attach()` | `attach()` keeps world transforms |
| Lid intersects the deck | wrong hinge or over-rotation | hinge `(0, 0.01485, -0.1054)`, −11° |
| Base cropped | settled fill too high | keep it ≤ (0.64, 0.70) |
| Device tiny in portrait | width fit takes over (correct) | accept it, or use a vertical-specific framing |
| Product orbits instead of spinning | bbox-centre pivot | `--pivot base` or `top` |
| Product sinks or floats | lowest point not at y = 0 | `findSpinAxis` handles it; check for stray vertices below the base |

### Backdrop and colour

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Wrong accent | a photo outweighs the brand colour | `--accent '#hex'` |
| Grey, lifeless set | page has no saturated colour, so the fallback accent was used | `--accent` |
| Light page got a dark set | average luminance just under 0.45 | `--theme light` |
| Colours don't match the hex | treated as linear somewhere | backdrop values are display-referred sRGB; don't convert |
| Banding in gradients | 8-bit output | keep the grain on (it dithers) |

### Turntable

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Floor grey with a horizon | tone mapping in the reflector shader | remove `tonemapping_fragment` |
| Reflection shows the inside | mirrored clone | `Reflector` |
| Reflection too strong or too long | `uStrength` / `uFadeEnd` | lower them |
| Scratch-like highlights | thin lights or a sharp reflector | broad softboxes; a 512–1024 px target |
| Product looks chalky | uniform environment, too much fill | more environment contrast, less fill |

## 3. Isolating an artifact

Remove one layer at a time:

1. **Matte:** roughness 1, clearcoat 0, `scene.environmentIntensity = 0`. If the lines vanish, they were reflections; if they stay, they are texture or UV seams.
2. **No map:** `material.map = null` and a mid-grey colour. If the problem disappears, it lives in the texture.
3. **No backdrop:** skip the backdrop render, so the model is drawn on black.
4. **Helpers:** add a temporary `Box3Helper` and `AxesHelper` to confirm the pivot and orientation.
5. **Whole page:** set the screenshot's `repeat.y` to 1 for a squashed full-page view. That confirms the UV direction.

## 4. Files and loading

- **`file://` fetches fail:** the builds inline everything as base64. Don't switch the final page back to `loader.load("model.glb")`.
- **Offline:** Three.js comes from jsDelivr, and the page shows an error after 12 s if it can't load. For offline delivery, vendor Three.js and rewrite the importmap.
- **Size:** about 3–5 MB for a screenshot mockup (the model is 2.5 MB of that); a video mockup adds the video; a turntable is the GLB plus ~25 KB.
- **Memory:** each 1300×8000 tile is ~55 MB of GPU memory with mipmaps. Two or three tiles are fine on any recent machine.

## 5. Definition of done

- It opens by double-click, with no server and no console errors.
- The content is upright, correctly cropped and legible in the settled shot.
- The scroll reaches the true bottom; a video export ends there.
- The backdrop colour belongs to the content.
- Nothing is clipped at 16:9, 16:10 or portrait.
- Any reflection is physically plausible.
