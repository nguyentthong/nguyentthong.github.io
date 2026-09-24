#!/usr/bin/env python3
"""Build the web copies of the photos listed in _travels/*.md.

Each trip file names a raw folder under images/ (gitignored, the originals
carry GPS), a cover photo and the photos to show. For a trip file
_travels/<slug>.md this writes:

  assets/img/travels/<slug>/NN-1024.webp   page image
  assets/img/travels/<slug>/NN-2048.webp   high-density page image and full screen view
  assets/img/travels/<slug>/cover.webp     3:2 crop for the /travels/ index

Copies are rebuilt from pixels only, so no EXIF, GPS or XMP metadata survives.
Image sizes and the page layout rows (portrait photos next to each other are
paired side by side) go to _data/travel_photos.json, which is generated and
must not be edited by hand.

Requires Pillow and PyYAML:  pip install pillow pyyaml
Usage:  python3 bin/travel_photos.py
"""

import json
import shutil
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
TRIPS_DIR = ROOT / "_travels"
RAW_DIR = ROOT / "images"
OUT_DIR = ROOT / "assets" / "img" / "travels"
META_OUT = ROOT / "_data" / "travel_photos.json"

SIZES = ((1024, 80), (2048, 78))  # longest edge in px, WebP quality
COVER_SIZE, COVER_QUALITY = (1200, 800), 80


def front_matter(path):
    text = path.read_text()
    if not text.startswith("---"):
        sys.exit(f"error: {path} has no front matter")
    return yaml.safe_load(text.split("---", 2)[1])


def load(path):
    with Image.open(path) as original:
        return ImageOps.exif_transpose(original).convert("RGB")


def save(img, path, quality):
    img.save(path, "WEBP", quality=quality, method=6)  # no exif argument, so metadata is dropped
    with Image.open(path) as check:
        if len(check.getexif()) or "exif" in check.info or "xmp" in check.info:
            sys.exit(f"error: metadata survived in {path}")


def layout_rows(photos):
    """One photo per row, except two consecutive portrait photos share a row."""
    rows, i = [], 0
    while i < len(photos):
        pair = i + 1 < len(photos) and all(p["height"] > p["width"] for p in photos[i:i + 2])
        rows.append([i, i + 1] if pair else [i])
        i += 2 if pair else 1
    return rows


def build_trip(path):
    trip = front_matter(path)
    slug = path.stem
    src_dir = RAW_DIR / trip["folder"]
    sources = [p["source"] for p in trip["photos"]] + [trip["cover"]]
    missing = sorted({s for s in sources if not (src_dir / s).is_file()})
    if missing:
        sys.exit(f"error: {path.name}: not found in {src_dir}: {', '.join(missing)}")

    out_dir = OUT_DIR / slug
    out_dir.mkdir(parents=True)

    photos = []
    for n, entry in enumerate(trip["photos"], 1):
        pixels = load(src_dir / entry["source"])
        for edge, quality in SIZES:
            copy = pixels.copy()
            copy.thumbnail((edge, edge), Image.LANCZOS)
            save(copy, out_dir / f"{n:02d}-{edge}.webp", quality)
        photos.append({"file": f"{n:02d}", "width": copy.width, "height": copy.height})

    cover = ImageOps.fit(load(src_dir / trip["cover"]), COVER_SIZE, Image.LANCZOS)
    save(cover, out_dir / "cover.webp", COVER_QUALITY)

    return slug, {"photos": photos, "rows": layout_rows(photos)}


def main():
    trip_files = sorted(TRIPS_DIR.glob("*.md"))
    if not trip_files:
        sys.exit(f"error: no trip files in {TRIPS_DIR}")
    shutil.rmtree(OUT_DIR, ignore_errors=True)  # drop copies of photos or trips no longer listed
    meta = {"_generated": "by bin/travel_photos.py from _travels/*.md, do not edit"}
    for path in trip_files:
        slug, trip_meta = build_trip(path)
        meta[slug] = trip_meta
        print(f"{slug}: {len(trip_meta['photos'])} photos in {len(trip_meta['rows'])} rows")
    META_OUT.write_text(json.dumps(meta, indent=2) + "\n")
    total = sum(f.stat().st_size for f in OUT_DIR.rglob("*.webp"))
    print(f"wrote {META_OUT.relative_to(ROOT)}, {total / 1e6:.1f} MB of images in {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
