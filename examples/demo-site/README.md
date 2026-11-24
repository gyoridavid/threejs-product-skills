# Demo site

`index.html` is a landing page for **Fernway**, a fictional trip-planning app. It exists so the previews in this repo show a realistic page without using anyone's real site or brand. Open `index.html#dark` for the night theme, which has a different accent and shows the backdrop's colour matching.

Recreate the previews:

```bash
cd ../../skills/threejs-product-showcases/tools && npm install
node capture-page.mjs "file://$PWD/../../../examples/demo-site/index.html#dark" /tmp/fernway-dark.png
cd ../macbook-showcase
python3 build.py --screenshot /tmp/fernway-dark.png --out /tmp/fernway-dark.html
node ../tools/render-video.mjs /tmp/fernway-dark.html --stills 4.4 --width 1600 --height 900
```
