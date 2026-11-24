# Product turntable

A product turning slowly on a pure-white glossy floor, with a real planar reflection that fades with distance, a soft contact shadow, a warm key light, and a broad cool fill. The studio environment rotates more slowly than the product, so highlights glide across it.

```
product-turntable/
├── build.py                          # builds one self-contained HTML
└── product-turntable.template.html
```

No model is bundled. Bring a binary glTF (`.glb`).

## Build

```bash
python3 build.py --model product.glb --out turntable.html
```

| Flag | Default | What it does |
| --- | --- | --- |
| `--pivot base\|top\|bbox` | `base` | How to find the spin axis (below) |
| `--finish original\|glossy` | `original` | Keep the model's materials, or add a clear-coat gloss (ceramics, plastics, lacquer) |
| `--revolution` | `32` | Seconds per full turn |
| `--title`, `--label` | generic | Page title and accessible description |

The output is the GLB size plus ~25 KB. Open it in Chrome; Three.js loads from jsDelivr.

## The spin axis

The bounding-box centre is often not where a product should spin: a handle, spout, strap or cable pushes it sideways, and the product orbits instead of turning in place.

- `base` (default): the centroid of the lowest 2% of vertices. That is the footprint, which sits under the body for most products, mugs included.
- `top`: the centroid of the highest 2%. Use it when the base is uneven or wider than the body, e.g. a bottle on a stand or a cup on a saucer.
- `bbox`: the bounding-box centre. Fine for symmetric products.

Check by rendering two stills a quarter-turn apart: the body should stay put while handles orbit.

```bash
node ../tools/render-video.mjs turntable.html --stills 0,8
```

## Scene defaults

- White background; a 60×60 `Reflector` floor with a custom shader. The reflection is 1024² at strength 0.78 and fades radially from 0.04 to 2.2 units.
- Contact shadow: a 1.75-unit radial plane just above the floor.
- Camera: fov 30°, elevation 13.5°. It fits the product's widest silhouette over a full turn at 54% of the frame height and 80% of the width.
- Light: hemisphere 0.65, directional key 3.4 with soft VSM shadows, rect-area fill 1.7. ACES tone mapping, exposure 1.02.
- The product is scaled so its height is 1 unit.

## Tuning

| Want | Change |
| --- | --- |
| More mirror | raise `uStrength`; raise the Reflector `textureWidth/Height` |
| Shorter reflection | lower `uFadeEnd` |
| Softer reflection | lower the Reflector target to 512 |
| Closer crop / more air | raise / lower the 0.54 height fill in `fitDistance` |
| Faster highlight sweep | raise `ENVIRONMENT_SPEED` |

Keep the custom reflector shader free of `tonemapping_fragment`. With it, the reflected white turns grey and draws a horizon line.

## Video

One revolution loops seamlessly, and `window.showcase.duration` is one revolution:

```bash
node ../tools/render-video.mjs turntable.html turntable.mp4
```

## Check before delivering

- The reflection is a real mirror image, not the model's inside.
- The floor is pure white with no grey horizon.
- The body stays centred while it turns.
- The contact shadow sits under the base, faint.
- The whole product stays in frame at 16:9 and in portrait.
