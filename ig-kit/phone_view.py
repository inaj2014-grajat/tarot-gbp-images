#!/usr/bin/env python3
"""Show a carousel the way it looks on a phone, as a check before publishing.

Usage: python3 -I ig-kit/phone_view.py <post dir> <out.jpg> [slide.jpg ...]

Input:  caption.txt in <post dir>; the slides given, or else the newest -rN of each 01-*.jpg, 02-*.jpg ... in <post dir>.
Output: <out.jpg>, a sheet of the profile grid followed by each slide in the feed.

This is a mock in Chrome's Pixel 7 phone mode, not the real Instagram app:
- The 3:4 grid crop was measured on the live profile on 2 Nov 2026 (275x367 tiles, 1080x1350 source).
- The feed layout and the top-right counter pill follow the app from memory. They are unverified.
"""
import html
import pathlib
import re
import sys
import tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

CAPTION_FOLD = 125  # characters shown before "more"
BASE_CSS = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><style>
*{margin:0;box-sizing:border-box;font-family:Inter,Roboto,Arial,sans-serif}
body{background:#fff;color:#111;width:412px}
.head{display:flex;align-items:center;gap:10px;padding:10px 12px;font-weight:600;font-size:14px}
.av{width:32px;height:32px;border-radius:50%;background:#c9c9c9}
.frame{position:relative;width:412px;height:515px;overflow:hidden}
.frame img{width:100%;height:100%;display:block}
.pill{position:absolute;top:12px;right:12px;background:rgba(20,20,20,.72);color:#fff;font-size:12px;font-weight:600;padding:5px 11px;border-radius:13px}
.dots{display:flex;justify-content:center;gap:4px;padding:10px 0 6px}.dots i{width:6px;height:6px;border-radius:50%;background:#cfcfcf}.dots i.on{background:#0095f6}
.cap{padding:2px 12px 12px;font-size:14px;line-height:1.35}.cap b{font-weight:600}.more{color:#777}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px}
.tile{aspect-ratio:3/4;background:#e9e9e9;overflow:hidden}.tile img{width:100%;height:100%;object-fit:cover;object-position:center;display:block}
.note{padding:8px 12px;font-size:11px;color:#777}
</style>"""


def newest_slides(slides_dir):
    """Return the newest revision of each numbered slide, in order."""
    best = {}
    for path in pathlib.Path(slides_dir).glob("[0-9][0-9]-*.jpg"):
        match = re.search(r"-r(\d+)$", path.stem)
        rev = int(match.group(1)) if match else 0
        key = path.stem[:2]
        if key not in best or rev > best[key][0]:
            best[key] = (rev, path)
    return [best[k][1] for k in sorted(best)]


def fold_caption(text):
    """Cut the caption where Instagram folds it."""
    flat = " ".join(text.split())
    return flat if len(flat) <= CAPTION_FOLD else flat[:CAPTION_FOLD].rstrip()


def grid_page(cover):
    tiles = f'<div class="tile"><img src="file://{cover}"></div>' + '<div class="tile"></div>' * 5
    return f'{BASE_CSS}<div class="head"><div class="av"></div>tarotcharutarot</div><div class="grid">{tiles}</div><div class="note">Profile grid. Mock in phone mode.</div>'


def feed_page(path, index, total, caption):
    dots = "".join(f'<i class="{"on" if k == index else ""}"></i>' for k in range(total))
    return (f'{BASE_CSS}<div class="head"><div class="av"></div>tarotcharutarot</div>'
            f'<div class="frame"><img src="file://{path}"><div class="pill">{index + 1}/{total}</div></div>'
            f'<div class="dots">{dots}</div><div class="cap"><b>tarotcharutarot</b> {html.escape(caption)}<span class="more">... more</span></div>')


def build(post_dir, out, given):
    """Render the grid and every slide at Pixel 7 size, and join them into one sheet."""
    slides = [pathlib.Path(g) for g in given] or newest_slides(post_dir)
    if not slides:
        sys.exit(f"no slides found in {post_dir}")
    caption_file = pathlib.Path(post_dir) / "caption.txt"
    caption = fold_caption(caption_file.read_text(encoding="utf-8")) if caption_file.exists() else ""
    pages = [grid_page(slides[0].resolve())]
    pages += [feed_page(s.resolve(), k, len(slides), caption) for k, s in enumerate(slides)]
    shots = []
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch()
        context = browser.new_context(**p.devices["Pixel 7"])
        page = context.new_page()
        for k, markup in enumerate(pages):
            source = pathlib.Path(tmp) / f"{k}.html"
            source.write_text(markup, encoding="utf-8")
            page.goto(f"file://{source}")
            page.wait_for_timeout(300)
            shot = pathlib.Path(tmp) / f"{k}.png"
            page.screenshot(path=str(shot))
            shots.append(Image.open(shot).convert("RGB").copy())
        browser.close()
    width = 412
    scaled = [s.resize((width, round(s.height * width / s.width)), Image.LANCZOS) for s in shots]
    sheet = Image.new("RGB", ((width + 12) * len(scaled) - 12, max(s.height for s in scaled)), (40, 40, 40))
    for k, shot in enumerate(scaled):
        sheet.paste(shot, (k * (width + 12), 0))
    sheet.save(out, quality=90)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2], sys.argv[3:])
