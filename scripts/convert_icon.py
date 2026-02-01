"""Convert an SVG into PNG + ICO with optional background."""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert SVG to PNG + ICO.")
    parser.add_argument("svg_path", type=Path, help="Path to the SVG file.")
    parser.add_argument(
        "background",
        type=str,
        help='Background hex color (e.g. "#0F172A") or "transparent".',
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (defaults to SVG directory).",
    )
    parser.add_argument(
        "--base-name",
        type=str,
        default=None,
        help="Base filename for outputs (defaults to SVG name).",
    )
    return parser.parse_args()


def render_svg(svg_path: Path) -> Image.Image:
    png_bytes = cairosvg.svg2png(url=str(svg_path), output_width=512, output_height=512)
    return Image.open(BytesIO(png_bytes)).convert("RGBA")


def with_background(image: Image.Image, background: str) -> Image.Image:
    if background.lower() == "transparent":
        return image
    bg = Image.new("RGBA", image.size, background)
    return Image.alpha_composite(bg, image)


def save_outputs(image: Image.Image, output_dir: Path, base_name: str, transparent: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{base_name}.png"
    ico_path = output_dir / f"{base_name}.ico"
    icns_path = output_dir / f"{base_name}.icns"

    ico_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    icns_sizes = [(512, 512), (256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]

    if transparent:
        image.save(png_path)
        image.save(ico_path, sizes=ico_sizes)
        image.save(icns_path, sizes=icns_sizes)
    else:
        rgb = image.convert("RGB")
        rgb.save(png_path)
        rgb.save(ico_path, sizes=ico_sizes)
        rgb.save(icns_path, sizes=icns_sizes)

    print(f"Wrote: {png_path}")
    print(f"Wrote: {ico_path}")
    print(f"Wrote: {icns_path}")


def main() -> None:
    args = parse_args()
    if not args.svg_path.exists():
        raise FileNotFoundError(f"SVG not found: {args.svg_path}")

    output_dir = args.output_dir or args.svg_path.parent
    base_name = args.base_name or args.svg_path.stem

    image = render_svg(args.svg_path)
    image = with_background(image, args.background)
    transparent = args.background.lower() == "transparent"
    save_outputs(image, output_dir, base_name, transparent)


if __name__ == "__main__":
    main()
