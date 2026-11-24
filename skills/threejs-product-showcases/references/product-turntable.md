# Product turntable: technical notes

Template: `product-turntable/product-turntable.template.html`. Build: `product-turntable/build.py`.

A pure-white, e-commerce-style hero: any GLB product turning on a glossy white floor, with a real reflection, a soft contact shadow, one key light, one broad fill and a slowly rotating studio environment.

## 1. Preparing the model

The template accepts any binary glTF with any number of meshes. In order, it:

1. keeps the model's materials (or applies the glossy finish; see section 2) and sets textures to sRGB with maximum anisotropy;
2. finds the spin axis and the lowest point in **world space** across all meshes (`findSpinAxis`);
3. wraps the model in a group offset by that axis, then scales it so the product is **1 unit tall**;
4. fits the camera to the product's widest silhouette over a full turn: the larger of the bbox width and 85% of the swept diameter.

### The spin axis

A turntable must turn around the product's body axis. The bounding-box centre is pulled sideways by anything asymmetric: a handle, spout, strap, cable or lens. Spinning around it makes the body orbit and wobble.

| `--pivot` | Axis from | Good for |
| --- | --- | --- |
| `base` (default) | centroid of vertices in the lowest 2% of the height | most products: the footprint sits under the body. Handles rarely reach the floor. |
| `top` | centroid of vertices in the highest 2% | products with an uneven or offset base: a cup on a saucer, a bottle on a stand |
| `bbox` | bounding-box centre | symmetric products |

The 2% band is wide enough to average out an uneven scan and narrow enough to exclude handles. A 0.2% band was skewed by single vertices on a scanned rim.

Verify with two stills a quarter-turn apart (`--stills 0,8` at the default 32 s revolution). The body should not move.

If the product's up axis isn't +Y (some CAD exports are Z-up), rotate the glTF scene before `findSpinAxis`.

## 2. Materials

The default keeps the model's own PBR materials. That suits most products, and it is the only correct choice for metal, fabric and wood.

`--finish glossy` replaces each material with a `MeshPhysicalMaterial` that keeps `map`, `normalMap`, `color` and `side`, and sets roughness 0.24, clearcoat 1.0, clearcoatRoughness 0.12 and envMapIntensity 1.7. Use it for ceramics, glazed and lacquered surfaces and glossy plastic, especially photogrammetry scans whose materials came out flat.

Scans often carry baked lighting in their base colour. Don't add strong extra contrast; let the key light give shape. A baked texture can also show a UV seam under a mirror-sharp highlight. Broad softboxes (as in the environment here) hide it; thin strip lights reveal it.

Use `side: DoubleSide` on scans that aren't closed solids, or the inside of a rim disappears.

## 3. White studio and a real reflection

- `scene.background` is pure white, with no floor mesh other than the reflector and no fog.
- A 60×60 `Reflector` lies at y = 0, with a 1024² render target and `clipBias: 0.003`.
- A radial contact-shadow plane sits at y = 0.002, rendered after the reflector.

### Why `Reflector`, not a mirrored clone

Cloning the product with `scale.y = -1` looks plausible for a second. Then it shows the inside of the product: the interior of a cup, the back faces of a shell. A real floor reflection is the scene rendered from a camera mirrored below the floor, which is what `Reflector` does.

### The fade shader

A full mirror reads as glass. The custom shader, passed as the Reflector's `shader` option, fades the reflection into the floor colour with distance from the turntable axis:

```glsl
vec4 base = texture2DProj(tDiffuse, vUv);
float fade = 1.0 - smoothstep(uFadeStart, uFadeEnd, length(vWorldPosition.xz));
vec3 reflected = mix(color, base.rgb, uStrength * fade);
gl_FragColor = vec4(reflected, 1.0);
#include <colorspace_fragment>
```

- Defaults: `uStrength` 0.78, `uFadeStart` 0.04, `uFadeEnd` 2.2.
- **No `tonemapping_fragment`.** Under ACES the reflected white background turns grey, and a horizon line appears where the floor meets the background. Keep only the colour-space conversion.
- The contact plane is single-sided. Seen from the reflector's mirrored camera its back face is culled, so it doesn't appear twice.

If the floor turns grey after a Three.js upgrade, check in this order: a tone-mapping include in the shader; the background in the reflection pass; the colour space of the reflection target. Only then touch colours.

## 4. Camera

- fov 30°, elevation 13.5°, target at half the product height.
- Fit: the larger of `height / (0.54 × 2 tan(fov/2))` and `widest / (0.80 × 2 tan(fov/2) × aspect)`.
- This framing leaves white space and room for the reflection below. 0.65 gives a closer hero; 0.45 gives more air.
- In portrait the width fit takes over: the product gets smaller but stays whole.

## 5. Light

- Hemisphere light at 0.65.
- Key: directional at 3.4, warm white, from (-2.2, 4.2, 3.0), with 1024² VSM shadows (radius 16).
- Fill: a `RectAreaLight` at 1.7, cool white, 2.4 × 1.8, from front right.
- Environment: a canvas-drawn studio (a dark surround, large warm and cool softboxes, a warm floor bounce), PMREM-filtered. The dark surround matters: without it, clear-coat highlights become a flat white sheen.
- The environment turns at 0.055 rad/s, independently of the product, so highlights glide across the surface.

## 6. Timing and capture

- `REVOLUTION_SECONDS` (default 32, `--revolution`): one continuous turn with no easing. It is a turntable.
- `draw(t)` sets the turntable angle and the environment rotation from `t` alone. `window.showcase.duration` is one revolution, which loops seamlessly.
- `?t=` and `?capture` work as in the MacBook template; see `video-export.md`.

## 7. Checklist for a new product

- The body stays centred while it turns (spin axis).
- The base sits exactly on the floor: no gap in the reflection, no intersection.
- The materials suit the product (`original` vs `glossy`).
- The contact shadow is in proportion: it is sized for a product 1 unit tall, so scale it for very wide products.
- The whole product fits at 16:9 and in portrait.
