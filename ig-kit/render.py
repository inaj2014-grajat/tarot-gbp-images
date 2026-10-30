#!/usr/bin/env python3
"""Render a Tarot by Charu Instagram carousel (1080x1350 JPEGs) from a JSON spec.

Usage:
  python3 render.py spec.json OUTDIR

Spec (all text fields: plain text, "\n" = line break; Devanagari is detected and set in Tiro Devanagari):
{
  "slug": "2026-11-09-the-moon",
  "format": "carousel",                     # or "reel": hides slide counters and SWIPE, then run reel.py
  "card": "the-moon",                       # key in cards.json; image must be in cards/<key>.jpg
  "slides": [
    {"type": "hook",    "photo": "bedroom-night", "head": "...", "sub": "...", "head_px": 86, "shift": 0.0},
    {"type": "card",    "title": "The Moon", "sub": "The card of ..."},
    {"type": "detail",  "box": [x0, y0, x1, y1], "fade": 88,   # box in card pixels (cards are ~1147x1919);
                        "label": "LOOK CLOSER", "head": "...", "sub": "...", "head_px": 58},
    {"type": "message", "photo": "balcony", "layout": "bottom",      # or "top" when the subject sits low
                        "quote": "...", "trans": "...", "line": "...", "cta": "DM “CLARITY”"}
  ]
}
Writes OUTDIR/01-hook.jpg ... and OUTDIR/contact.jpg (all slides side by side, for review).
"""
import html, json, pathlib, re, sys, urllib.request
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

KIT = pathlib.Path(__file__).resolve().parent
W, H = 1080, 1350
FONT_DIR = pathlib.Path.home() / ".cache" / "tbc-fonts"
G = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONTS = {
    "Cinzel.ttf": G + "cinzel/Cinzel%5Bwght%5D.ttf",
    "Lora.ttf": G + "lora/Lora%5Bwght%5D.ttf",
    "Lora-Italic.ttf": G + "lora/Lora-Italic%5Bwght%5D.ttf",
    "Tiro.ttf": G + "tirodevanagarihindi/TiroDevanagariHindi-Regular.ttf",
    "Tiro-Italic.ttf": G + "tirodevanagarihindi/TiroDevanagariHindi-Italic.ttf",
}
DEVA = re.compile("[ऀ-ॿ]")


def ensure_fonts():
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in FONTS.items():
        p = FONT_DIR / name
        if not p.exists() or p.stat().st_size < 10_000:
            urllib.request.urlretrieve(url, p)
        if p.stat().st_size < 10_000:
            sys.exit(f"font download failed: {name}")


def t(s, size=None):
    """Escape text; newline -> <br>; wrap Devanagari text in the Hindi font."""
    if not s:
        return ""
    out = html.escape(s).replace("\n", "<br>")
    if DEVA.search(s):
        st = f' style="font-size:{size}px"' if size else ""
        out = f'<span class="hi"{st}>{out}</span>'
    return out


# ---------- image layers ----------
def cover_top(src, shift=0.0):
    im = Image.open(src).convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    if im.height < H:  # landscape photo: scale by height instead, centre crop
        im = Image.open(src).convert("RGB")
        im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
        x = (im.width - W) // 2
        return im.crop((x, 0, x + W, H))
    y = int((im.height - H) * shift)
    return im.crop((0, y, W, y + H))


def place_card(card_path, card_h=880, angle=-3.5, cx=W // 2, cy=560):
    bg = Image.open(KIT / "assets" / "velvet.jpg").convert("RGB").resize((W, H))
    card = Image.open(card_path).convert("RGB")
    cw, ch = card.size
    c = card.crop((10, 10, cw - 10, ch - 10))
    c = c.resize((round(c.width * card_h / c.height), card_h), Image.LANCZOS)
    hh, ww = c.height, c.width
    yy, xx = np.mgrid[0:hh, 0:ww]
    shade = 1.0 - 0.38 * (xx / ww * 0.55 + yy / hh * 0.45)
    arr = np.asarray(c).astype(np.float32)
    arr[..., 0] *= shade; arr[..., 1] *= shade * 0.98; arr[..., 2] *= shade * 0.92
    c = Image.fromarray(np.clip(arr * 0.95, 0, 255).astype(np.uint8))
    mask = Image.new("L", c.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, c.width - 1, c.height - 1), radius=int(c.width * 0.07), fill=255)
    rgba = c.convert("RGBA"); rgba.putalpha(mask)
    rgba = rgba.rotate(angle, resample=Image.BICUBIC, expand=True)
    a = rgba.getchannel("A"); P = 120

    def shadow(sc, blur):
        s = Image.new("L", (a.width + 2 * P, a.height + 2 * P), 0)
        s.paste(a.point(lambda v: int(v * sc)), (P, P))
        o = Image.new("RGBA", s.size, (0, 0, 0, 0)); o.putalpha(s.filter(ImageFilter.GaussianBlur(blur)))
        return o
    base = bg.convert("RGBA")
    x, y = cx - rgba.width // 2, cy - rgba.height // 2
    base.alpha_composite(shadow(0.85, 38), (x - P + 34, y - P + 48))
    base.alpha_composite(shadow(0.9, 7), (x - P + 5, y - P + 8))
    base.alpha_composite(rgba, (x, y))
    return base.convert("RGB")


def detail_box(card_path, box, max_h=1000):
    """Keep the crop's own aspect (no squashing), stay off the name banner, cap height.
    Returns (box, out_h)."""
    cw, ch = Image.open(card_path).size
    x0, y0, x1, y1 = box
    banner = int(ch * 0.87)                       # RWS title banner starts ~87% down
    if y1 > banner:
        print(f"warning: detail box bottom {y1} reaches the name banner; clamped to {banner}")
        y1 = banner
    out_h = round(W * (y1 - y0) / (x1 - x0))
    if out_h > max_h:                             # too tall: trim from the top
        y0 = y1 - round((x1 - x0) * max_h / W); out_h = max_h
    return (x0, y0, x1, y1), out_h


def detail(card_path, box, out_h):
    return Image.open(card_path).convert("RGB").crop(tuple(box)).resize((W, out_h), Image.LANCZOS)


# ---------- HTML ----------
def head_css():
    F = FONT_DIR
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Cinzel;src:url('file://{F}/Cinzel.ttf');font-weight:400 900}}
@font-face{{font-family:Lora;src:url('file://{F}/Lora.ttf');font-style:normal;font-weight:400 700}}
@font-face{{font-family:Lora;src:url('file://{F}/Lora-Italic.ttf');font-style:italic;font-weight:400 700}}
@font-face{{font-family:TiroHi;src:url('file://{F}/Tiro.ttf');font-style:normal}}
@font-face{{font-family:TiroHi;src:url('file://{F}/Tiro-Italic.ttf');font-style:italic}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;overflow:hidden;background:#0b0d0b;position:relative;color:#F3EAD8;font-family:Lora,TiroHi,serif}}
.bg{{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover}}
.ov{{position:absolute;inset:0}}
.brand{{position:absolute;top:58px;left:64px;font-family:Cinzel;font-weight:500;font-size:19px;letter-spacing:.34em;color:#D4AF5A}}
.num{{position:absolute;top:58px;right:64px;font-family:Cinzel;font-size:19px;letter-spacing:.2em;color:rgba(243,234,216,.75)}}
.label{{font-family:Cinzel;font-weight:500;font-size:22px;letter-spacing:.36em;color:#D4AF5A}}
.h{{font-family:Cinzel,TiroHi;font-weight:600;color:#F3EAD8;text-wrap:balance;text-shadow:0 2px 24px rgba(0,0,0,.6)}}
.hi{{font-family:TiroHi,serif;font-weight:400;letter-spacing:0;line-height:1.35}}
.it{{font-style:italic;color:#E6D7BA;text-wrap:balance;text-shadow:0 2px 18px rgba(0,0,0,.65)}}
.rule{{width:84px;height:1px;background:#D4AF5A}}
.pill{{font-family:Cinzel;font-weight:600;font-size:30px;letter-spacing:.16em;color:#0b0d0b;background:#D4AF5A;padding:20px 48px;border-radius:999px}}
.grain{{position:absolute;inset:0;opacity:.07;mix-blend-mode:overlay;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}}
.band{{position:absolute;top:0;left:0;right:0;height:190px;background:linear-gradient(180deg,rgba(11,13,11,.95) 0%,rgba(11,13,11,.75) 45%,rgba(11,13,11,0) 100%)}}
</style></head><body>"""


TOPDARK = '<div class="ov" style="background:linear-gradient(180deg,rgba(4,6,5,.88) 0%,rgba(4,6,5,.62) 26%,rgba(4,6,5,0) 50%,rgba(4,6,5,0) 78%,rgba(4,6,5,.55) 100%)"></div>'
BRAND = '<div class="brand">TAROT BY CHARU</div>'


def num(i, n):
    return f'<div class="num">{i} / {n}</div>'


def hook_html(img, s, i, n):
    return f"""<img class="bg" src="{img}">{TOPDARK}{BRAND}
<div style="position:absolute;top:150px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:28px;padding:0 80px;text-align:center">
  <div class="h" style="font-size:{s.get('head_px', 86)}px;line-height:1.08">{t(s['head'])}</div>
  <div class="rule"></div>
  <div class="it" style="font-size:42px;line-height:1.3">{t(s.get('sub', ''))}</div>
</div>
<div style="position:absolute;bottom:58px;left:0;right:0;text-align:center" class="label swipe">SWIPE &nbsp;&rarr;</div>
<div class="grain"></div>"""


def card_html(img, s, i, n):
    return f"""<img class="bg" src="{img}">
<div class="ov" style="background:linear-gradient(180deg,rgba(0,0,0,0) 72%,rgba(3,6,5,.75) 100%)"></div>
{BRAND}{num(i, n)}
<div style="position:absolute;top:1080px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:14px;padding:0 90px;text-align:center">
  <div class="h" style="font-size:68px;color:#D4AF5A;letter-spacing:.02em">{t(s['title'])}</div>
  <div class="it" style="font-size:34px;line-height:1.35">{t(s.get('sub', ''))}</div>
</div><div class="grain"></div>"""


def detail_html(img, s, i, n):
    fade = s.get("fade", 85)
    m = f"linear-gradient(180deg,#000 0%,#000 {fade}%,transparent 100%)"
    return f"""<img src="{img}" style="position:absolute;top:0;left:0;width:1080px;height:{s.get('img_h', 900)}px;-webkit-mask-image:{m};mask-image:{m}">
<div class="band"></div>{BRAND}{num(i, n)}
<div style="position:absolute;top:{s.get('top', 960)}px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:20px;padding:0 96px;text-align:center">
  <div class="label">{t(s.get('label', 'LOOK CLOSER'))}</div>
  <div class="h" style="font-size:{s.get('head_px', 58)}px;line-height:1.14">{t(s['head'])}</div>
  <div class="it" style="font-size:33px;line-height:1.4">{t(s.get('sub', ''))}</div>
</div><div class="grain"></div>"""


def message_html(img, s, i, n):
    q, tr, line, cta = t(s["quote"]), t(s.get("trans", "")), t(s.get("line", ""), 40), t(s.get("cta", ""))
    if s.get("layout") == "top":
        return f"""<img class="bg" src="{img}">{TOPDARK}{BRAND}{num(i, n)}
<div style="position:absolute;top:130px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:18px;padding:0 90px;text-align:center">
  <div class="label">THE CARD'S MESSAGE</div>
  <div class="it" style="font-size:50px;line-height:1.26;color:#F3EAD8">&ldquo;{q}&rdquo;</div>
  <div style="font-size:26px;line-height:1.45;color:rgba(230,215,186,.9);text-shadow:0 2px 14px rgba(0,0,0,.7)">{tr}</div>
  <div class="rule" style="margin-top:8px"></div>
  <div class="h" style="font-size:34px;line-height:1.25">{line}</div>
  {f'<div class="pill" style="font-size:26px;padding:16px 40px">{cta}</div>' if cta else ''}
</div><div class="grain"></div>"""
    return f"""<img class="bg" src="{img}">{TOPDARK}
<div class="ov" style="background:linear-gradient(180deg,rgba(0,0,0,0) 62%,rgba(4,8,6,.82) 80%,rgba(4,8,6,.94) 100%)"></div>
{BRAND}{num(i, n)}
<div style="position:absolute;top:140px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:20px;padding:0 90px;text-align:center">
  <div class="label">THE CARD'S MESSAGE</div>
  <div class="it" style="font-size:52px;line-height:1.28;color:#F3EAD8">&ldquo;{q}&rdquo;</div>
  <div style="font-size:27px;line-height:1.45;color:rgba(230,215,186,.9);text-shadow:0 2px 14px rgba(0,0,0,.7)">{tr}</div>
</div>
<div style="position:absolute;bottom:72px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:24px;text-align:center;padding:0 80px">
  <div class="h" style="font-size:38px;line-height:1.25">{line}</div>
  {f'<div class="pill">{cta}</div>' if cta else ''}
</div><div class="grain"></div>"""


BUILDERS = {"hook": hook_html, "card": card_html, "detail": detail_html, "message": message_html}


def main():
    spec_path, outdir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    outdir.mkdir(parents=True, exist_ok=True)
    work = outdir / "_work"; work.mkdir(exist_ok=True)
    ensure_fonts()
    card_path = KIT / "cards" / f"{spec['card']}.jpg"
    if not card_path.exists():
        sys.exit(f"card image missing: {card_path} (fetch it with hf_fs attach, see cards.json)")
    slides = spec["slides"]
    n = len(slides)
    names = []
    for i, s in enumerate(slides, 1):
        typ = s["type"]
        layer = work / f"{i:02d}.jpg"
        if typ in ("hook", "message"):
            p = KIT / "photos" / f"{s['photo']}.jpg"
            if not p.exists():
                sys.exit(f"photo missing: {p}")
            cover_top(p, s.get("shift", 0.0)).save(layer, quality=94)
        elif typ == "card":
            place_card(card_path).save(layer, quality=94)
        elif typ == "detail":
            box, h = detail_box(card_path, s["box"])
            s["img_h"] = h
            s.setdefault("top", min(h + 60, 1080))
            detail(card_path, box, h).save(layer, quality=94)
        else:
            sys.exit(f"unknown slide type {typ}")
        css = head_css() + ("<style>.num,.swipe{display:none}</style>" if spec.get("format") == "reel" else "")
        (work / f"{i:02d}.html").write_text(css + BUILDERS[typ](f"file://{layer}", s, i, n) + "</body></html>", encoding="utf-8")
        names.append(f"{i:02d}-{s.get('name', typ)}")
    from playwright.sync_api import sync_playwright
    outs = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        for i, nm in enumerate(names, 1):
            pg.goto(f"file://{work / f'{i:02d}.html'}"); pg.wait_for_timeout(900)
            png = work / f"{nm}.png"
            pg.screenshot(path=str(png))
            out = outdir / f"{nm}.jpg"
            Image.open(png).convert("RGB").save(out, quality=92)
            outs.append(out); print(out)
        b.close()
    # contact sheet for review
    th = [Image.open(o).resize((432, 540), Image.LANCZOS) for o in outs]
    sheet = Image.new("RGB", (432 * len(th) + 12 * (len(th) - 1), 540), (40, 40, 40))
    for k, im in enumerate(th):
        sheet.paste(im, (k * 444, 0))
    sheet.save(outdir / "contact.jpg", quality=88)
    print(outdir / "contact.jpg")


if __name__ == "__main__":
    main()
