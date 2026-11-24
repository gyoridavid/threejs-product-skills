#!/usr/bin/env python3
"""Build a self-contained white-studio product turntable with a real reflection.

The model is inlined, so the output opens by double-click from file://.

Examples:
    python3 build.py --model product.glb --out turntable.html
    python3 build.py --model mug.glb --pivot top --finish glossy
"""

from __future__ import annotations

import argparse
import base64
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "product-turntable.template.html"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--model", required=True, help="product GLB (binary glTF)")
    parser.add_argument("--out", default="product-turntable.html", help="output HTML path")
    parser.add_argument(
        "--pivot", choices=["base", "top", "bbox"], default="base",
        help="spin axis: centre of the base (default), of the top, or the bounding box",
    )
    parser.add_argument(
        "--finish", choices=["original", "glossy"], default="original",
        help="keep the model's materials, or add a clear-coat gloss",
    )
    parser.add_argument("--revolution", type=float, default=32, help="seconds per turn")
    parser.add_argument("--title", default="Product turntable", help="page <title>")
    parser.add_argument("--label", default="A product turning slowly on a white studio floor",
                        help="accessible description of the scene")
    args = parser.parse_args()

    model = Path(args.model).expanduser().resolve()
    output = Path(args.out).expanduser().resolve()
    for label, path in (("model", model), ("template", TEMPLATE)):
        if not path.exists():
            raise SystemExit(f"Missing {label}: {path}")
    if model.read_bytes()[:4] != b"glTF":
        raise SystemExit("The model must be a binary glTF (.glb) file")

    config = {"pivot": args.pivot, "finish": args.finish, "revolutionSeconds": args.revolution}
    page = TEMPLATE.read_text()
    replacements = {
        "__TITLE__": html.escape(args.title),
        "__ARIA_LABEL__": html.escape(args.label, quote=True),
        "__CONFIG_JSON__": json.dumps(config),
        "__MODEL_GLB_BASE64__": base64.b64encode(model.read_bytes()).decode("ascii"),
    }
    for token, value in replacements.items():
        if token not in page:
            raise SystemExit(f"Template is missing the placeholder {token}")
        page = page.replace(token, value)

    output.write_text(page)
    size_mb = output.stat().st_size / (1024 * 1024)
    print(f"Wrote {output} ({size_mb:.1f} MB, pivot: {args.pivot}, finish: {args.finish})")


if __name__ == "__main__":
    main()
