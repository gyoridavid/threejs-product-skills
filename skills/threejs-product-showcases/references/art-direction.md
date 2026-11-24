# Art direction

The reasoning behind the two scenes. Read it when adapting them to a new brand, product or page, or when a render is technically right but feels wrong.

## 1. Decide what the viewer looks at

Both scenes are single-hero compositions.

- **MacBook:** the screen is the brightest, highest-contrast area and the story. The laptop is the silhouette; the backdrop is the frame. Everything else stays quiet.
- **Turntable:** the product's silhouette and surface are the hero. The white space is the frame, and the reflection grounds the product; it is not a second product.

What follows from that:

- No UI chrome, captions, prices or logos unless the request asks for them. A full-bleed scene with nothing competing reads as premium.
- One dominant motion. The MacBook has a camera push followed by the scroll; the turntable has one slow spin. Don't add competing loops.
- Leave negative space. A device that touches every edge reads as a crop, not a hero.

## 2. The MacBook

### Screenshot or video

- **Screenshot scroll:** use it when the page is the message: a landing page, a product site, a portfolio. The scroll is the story, so start at the top, move down only, and stop at the bottom. Never bounce or loop a scroll; a page that jumps back to its header breaks the illusion. For video delivery, end the video on the frame where the page reaches the bottom.
- **Video:** use it for app flows, motion-led products and anything with interaction. Cover-crop into the 16:10 panel and keep the subject centred.

The screen must be legible in the settled shot. At 1300 px of page width and the default framing, body text is readable at 1080p. Text below ~14 px on the source page will not be.

### Backdrop

The backdrop exists to make the page feel at home, not to be looked at. That is why it is sampled from the content (see `backdrops-and-color.md`):

- **beams** for most pages. It reads as stage light in the brand colour and draws the eye down to the laptop.
- **gradient** for long scrolls and minimal brands, where the content should carry the whole video.
- **tunnel** for energy: short social clips and neutral pages that need a graphic frame. The portal is capped so the ribs stay visible around the settled laptop; at full size it would become a plain white void.

Keep the device darker than a light backdrop and lighter-edged than a dark one. The accent-tinted rim light does the second part automatically.

### Camera

- Start with the laptop small enough that the set reads, but large enough that the page is recognisable: about 34% of the frame height.
- Push in with an ease-in-out over ~4 s. A slow dolly continues for the rest of the shot (6% closer), so a long scroll never feels static.
- The sideways sway is ±0.05 rad, slow. Enough to show the model is 3D; not enough to tilt the page out of readability. Product UI should face the viewer.
- Aim at 40% of the device height, below the screen centre: the base is nearer the camera and needs the room.
- End with air below the laptop. The float only reads as levitation if there is space under it.

### Float

Small and slow: ±0.009 units of bob plus a secondary sine, and fractions of a degree of yaw, pitch and roll. Larger amounts read as a bounce. The float ramps in as the camera settles, so the push-in stays clean.

## 3. The turntable

The white turntable speaks a different language from the dark mockup: a seamless white sweep, a real reflection, one key light, one fill and one slow spin. It is the vocabulary of e-commerce product photography. It feels shoppable and clean, and it suits dark or saturated products best: they get a crisp silhouette.

### Reflection

- A real planar reflection, never a scaled clone (`product-turntable.md` explains why).
- Fade it with distance. A full mirror across the floor looks like glass, not a studio surface.
- Keep the floor pure white: no tone mapping in the reflector shader.
- Keep it slightly soft (a 1024 px target). Razor-sharp reflections reveal scan seams and facets.
- Keep the contact shadow low-contrast. It grounds the product; it should not look like a sticker.

### Light and surface

- A dark studio surround in the environment gives glossy surfaces meaningful reflections. A uniformly bright environment makes ceramics look chalky.
- Use broad softboxes. Thin strip lights make hairline highlights that look like scratches, especially on low-poly scans.
- The key light should leave a readable shadow side, with the fill soft and low.

### Camera

- Elevation 13.5°, enough to see a rim or top surface without looking down on the product.
- Sit the product slightly high in the frame, so the reflection has room below.
- Centre the body axis, not the bbox. Asymmetric parts are allowed to swing.

## 4. Failure modes

| Looks like | Probably | Direction |
| --- | --- | --- |
| Backdrop colour feels random | a photo on the page won the accent vote | `--accent` with the brand colour |
| Set competes with the page | tunnel on a colourful page | `beams` or `gradient` |
| Light set looks muddy | low-contrast base vs accent | `--base` lighter, or a more saturated `--accent` |
| Page text illegible | page captured too wide, or tiny source text | capture at 1280–1440 px wide; check the settled frame |
| Scroll feels rushed | speed too high for the page density | `--scroll-speed 180` |
| Laptop base cropped | settled framing too tight | lower the settled fills |
| Floor grey with a horizon | tone mapping in the reflector | remove `tonemapping_fragment` |
| Reflection shows the product's inside | mirrored clone | use `Reflector` |
| Scratch-like lines on a glossy product | thin strip lights | broad softboxes |
| Product looks pasted in | no contact shadow or reflection | add both, subtly |

## 5. A short process

1. Decide the hero and the single dominant motion.
2. Pick the content (screenshot or video) and let it pick the palette. Override only with a reason.
3. Frame from the silhouette, not the bbox. Check the whole device.
4. Light for form; let the screen or product be the brightest thing.
5. Decide how it ends: a scroll ends at the bottom; a turntable loops after one revolution.
6. Look at real frames at the start, the settle and the end, at 16:9 and in portrait.
