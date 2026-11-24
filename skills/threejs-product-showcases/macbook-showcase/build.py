#!/usr/bin/env python3
"""Build a self-contained MacBook mockup page.

The screen shows either a tall website screenshot that scrolls to the bottom
(--screenshot) or a looping video (--video). Everything (model, screen content,
settings) is inlined, so the output opens by double-click from file://.

Examples:
    python3 build.py --screenshot page.png --out mockup.html
    python3 build.py --screenshot page.png --backdrop tunnel --accent "#7337cd"
    python3 build.py --video demo.mp4 --backdrop gradient --out demo.html
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "macbook.template.html"
DEFAULT_MODEL = HERE / "assets" / "macbook.glb"

PAGE_WIDTH = 1300  # plenty for the ~950 px the screen covers in a close-up
TILE_HEIGHT = 8000  # below the common 8192 px WebGL texture limit
TILE_OVERLAP = 1200  # must exceed the visible window (~845 px at 1300 wide)


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def require(tool: str) -> None:
    if shutil.which(tool) is None:
        raise SystemExit(f"{tool} is required for screenshots (install ffmpeg)")


def dimensions(path: Path) -> tuple[int, int]:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path),
        ],
        text=True,
    ).strip()
    width, height = out.split(",")[:2]
    return int(width), int(height)


def prepare_tiles(screenshot: Path, workdir: Path) -> tuple[dict, list[Path]]:
    """Scale the page to PAGE_WIDTH and cut it into overlapping JPEG tiles.

    One texture per tile keeps every texture under the GPU size limit without
    shrinking a long page until its text is unreadable.
    """
    require("ffmpeg")
    require("ffprobe")
    width, height = dimensions(screenshot)
    out_w = min(PAGE_WIDTH, width)
    out_h = round(height * out_w / width / 2) * 2

    tiles, paths = [], []
    top = 0
    while True:
        tile_h = min(TILE_HEIGHT, out_h - top)
        path = workdir / f"tile-{len(paths)}.jpg"
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-y", "-i", str(screenshot),
                "-vf", f"scale={out_w}:{out_h}:flags=lanczos,crop={out_w}:{tile_h}:0:{top}",
                "-q:v", "2", str(path),
            ],
            check=True,
        )
        tiles.append({"top": top, "height": tile_h})
        paths.append(path)
        if top + tile_h >= out_h:
            break
        top += TILE_HEIGHT - TILE_OVERLAP

    manifest = {"kind": "screenshot", "width": out_w, "height": out_h, "tiles": tiles}
    return manifest, paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    content = parser.add_mutually_exclusive_group(required=True)
    content.add_argument("--screenshot", help="tall full-page PNG/JPEG to scroll on the screen")
    content.add_argument("--video", help="MP4 (H.264) to loop on the screen")
    parser.add_argument("--out", default="macbook-mockup.html", help="output HTML path")
    parser.add_argument("--model", default=str(DEFAULT_MODEL), help="MacBook GLB")
    parser.add_argument(
        "--backdrop", choices=["beams", "tunnel", "gradient"], default="beams",
        help="background look; all three take their colours from the screen content",
    )
    parser.add_argument("--accent", help="override the sampled accent colour, e.g. '#ff6363'")
    parser.add_argument("--base", help="override the sampled background colour, e.g. '#0b0b0e'")
    parser.add_argument("--theme", choices=["dark", "light"], help="override light/dark detection")
    parser.add_argument(
        "--scroll-speed", type=float, default=250,
        help="cruise speed in page px/s at 1300 px width (default 250)",
    )
    parser.add_argument("--no-grain", action="store_true", help="disable the backdrop grain")
    parser.add_argument("--title", default="MacBook mockup", help="page <title>")
    args = parser.parse_args()

    model = Path(args.model).expanduser().resolve()
    output = Path(args.out).expanduser().resolve()
    source = Path(args.screenshot or args.video).expanduser().resolve()
    for label, path in (("model", model), ("template", TEMPLATE), ("content", source)):
        if not path.exists():
            raise SystemExit(f"Missing {label}: {path}")

    config = {
        "backdrop": args.backdrop,
        "accent": args.accent,
        "base": args.base,
        "theme": args.theme,
        "scrollSpeed": args.scroll_speed,
        "grain": not args.no_grain,
    }

    with tempfile.TemporaryDirectory() as tmp:
        if args.screenshot:
            manifest, tile_paths = prepare_tiles(source, Path(tmp))
            data_tags = [
                f'<script class="screen-tile" type="text/plain">{b64(p)}</script>'
                for p in tile_paths
            ]
            label = "A floating MacBook scrolling a website from top to bottom"
        else:
            manifest = {"kind": "video"}
            data_tags = [f'<script class="screen-video" type="text/plain">{b64(source)}</script>']
            label = "A floating MacBook playing a video on its screen"

        screen_data = "\n    ".join(
            [f'<script id="screen-manifest" type="application/json">{json.dumps(manifest)}</script>']
            + data_tags
        )

        page = TEMPLATE.read_text()
        replacements = {
            "__TITLE__": html.escape(args.title),
            "__ARIA_LABEL__": label,
            "__CONFIG_JSON__": json.dumps(config),
            "__MACBOOK_GLB_BASE64__": b64(model),
            "<!-- __SCREEN_DATA__ -->": screen_data,
        }
        for token, value in replacements.items():
            if token not in page:
                raise SystemExit(f"Template is missing the placeholder {token}")
            page = page.replace(token, value)

    output.write_text(page)
    size_mb = output.stat().st_size / (1024 * 1024)
    detail = (
        f"{manifest['width']}x{manifest['height']} page in {len(manifest['tiles'])} tile(s)"
        if args.screenshot
        else "video"
    )
    print(f"Wrote {output} ({size_mb:.1f} MB, {detail}, backdrop: {args.backdrop})")


if __name__ == "__main__":
    main()
