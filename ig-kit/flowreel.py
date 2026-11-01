#!/usr/bin/env python3
"""Build a Tarot by Charu Reel from a scene spec (AI clip + text overlays + card scenes + music).

Usage:  python3 -I ig-kit/flowreel.py <dir>/spec.json <dir>
Writes: <dir>/reel.mp4, <dir>/contact.jpg (key frames), <dir>/safezone.jpg (Instagram UI overlay),
        <dir>/build.json (timings + checks). Exit 0 = pass, 1 = a check failed (do not publish).

spec.json (format "reel", engine "flowreel"):
{
  "slug": "...", "format": "reel", "engine": "flowreel", "card": "<main card key>",
  "flow": {"prompt": "...", "model": "Veo 3.1 - Fast"},      # how clip.mp4 was made (for the record)
  "scenes": [
    {"type": "clip", "src": "clip.mp4", "hold": 2.0, "brighten": true,
     "texts": [{"t": 0, "text": "ये सब कब तक चलेगा?", "style": "hi"},
               {"t": 3.0, "text": "Nothing stays<br>the same forever.", "style": "cz"}]},
    {"type": "chat", "dur": 6, "steps": [
        {"t": 0,   "from": "them", "text": "यार, ये सब कब बदलेगा?", "time": "11:47 PM"},
        {"t": 1.6, "typing": true},
        {"t": 2.4, "from": "me", "text": "..."}]},
    {"type": "card", "card": "temperance", "dur": 3.8, "label": "THE CARD'S MESSAGE",
     "sub": "...", "cta": "DM “CLARITY”", "line": "Charu can help you ...", "zoom": false},
    {"type": "text", "dur": 3, "head": "...", "sub": "..."}           # dark brand slide, text only
  ]
}
Text styles: "hi" = gold Devanagari-first (Tiro), "cz" = cream Cinzel small caps, "lora" = cream Lora italic.
Hindi lines may mix English words; fonts are picked per character. Use <br> for a line break.

Brand/IG rules enforced here:
- every overlay's text sits inside the Instagram Reels safe area (y 270-1250, x 65-1015, and left of
  x 850 below y 1150), checked on the rendered PNGs, not on intent;
- text appears on frame 1 and within 0.5 s of every cut (fade-through-black is 0.8 s; text is back by mid-fade);
- total length must be under 15 s;
- the clip's own visible watermark (e.g. Flow/Veo) is never cropped or covered: clips are scaled, not cropped.
"""
import json, pathlib, subprocess, sys, shutil, math
import numpy as np
from PIL import Image

KIT = pathlib.Path(__file__).resolve().parent
FONTS = KIT / "fonts"
W, H, FPS = 1080, 1920, 24
FADE = 0.8
SAFE = dict(x0=65, x1=1015, y0=270, y1=1250, rail_y=1150, rail_x=850)
GOLD, CREAM, BG = "#D4AF5A", "#F3EBDD", "#0d0a08"


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"command failed: {' '.join(map(str, cmd))[:300]}\n{r.stderr[-1500:]}")
    return r.stdout


def probe_dur(p):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).strip())


def has_audio(p):
    return bool(sh(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(p)]).strip())


def u(name):
    return (FONTS / name).as_uri()


CSS = f"""
@font-face{{font-family:Cinzel;font-weight:600;src:url({u('cinzel-latin-600-normal.woff2')})}}
@font-face{{font-family:Lora;font-style:italic;font-weight:400;src:url({u('lora-latin-400-italic.woff2')})}}
@font-face{{font-family:Lora;font-style:normal;font-weight:500;src:url({u('lora-latin-500-normal.woff2')})}}
@font-face{{font-family:Tiro;src:url({u('tiro-devanagari-hindi-devanagari-400-normal.woff2')});unicode-range:U+0900-097F,U+1CD0-1CF9,U+200C-200D,U+20A8,U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FF}}
@font-face{{font-family:Tiro;src:url({u('tiro-devanagari-hindi-latin-400-normal.woff2')});unicode-range:U+0000-00FF,U+2000-206F}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:transparent}}
.shadow{{text-shadow:0 2px 18px rgba(0,0,0,.85),0 0 4px rgba(0,0,0,.6)}}
.grad{{position:absolute;left:0;right:0;top:720px;height:1032px;
  background:linear-gradient(to bottom,rgba(8,6,5,0) 0%,rgba(8,6,5,.62) 30%,rgba(8,6,5,.78) 55%,rgba(8,6,5,.85) 100%)}}
.block{{position:absolute;left:90px;right:90px;bottom:790px;text-align:center}}
.hi{{font-family:Tiro,serif;font-size:92px;line-height:1.32;color:{GOLD}}}
.cz{{font-family:Cinzel,serif;font-weight:600;font-size:72px;line-height:1.2;color:{CREAM};font-variant:small-caps}}
.lora{{font-family:Lora,serif;font-style:italic;font-size:64px;line-height:1.3;color:{CREAM}}}
.rule{{width:120px;height:2px;background:{GOLD};opacity:.8;margin:32px auto 0}}
.wm{{position:absolute;left:56px;bottom:62px;font-family:Cinzel,serif;font-weight:600;font-size:26px;letter-spacing:.32em;color:{GOLD};opacity:.7}}
.dark{{background:radial-gradient(ellipse at 50% 34%,#16241c 0%,{BG} 62%,#0a0807 100%)}}
.stack{{position:absolute;top:296px;bottom:684px;left:110px;right:110px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px}}
.lab{{font-family:Cinzel,serif;font-weight:600;font-size:26px;letter-spacing:.32em;color:{GOLD};opacity:.85;flex:none}}
.card{{flex:0 1 auto;min-height:0;max-height:500px;width:auto;object-fit:contain;border-radius:14px;box-shadow:0 18px 50px rgba(0,0,0,.65),0 0 0 2px rgba(212,175,90,.55)}}
.sub{{flex:none;text-align:center;font-family:Tiro,Lora,serif;font-size:48px;line-height:1.28;color:{CREAM}}}
.sub.it{{font-family:Lora,Tiro,serif;font-style:italic}}
.btn{{flex:none;background:{GOLD};color:{BG};font-family:Cinzel,serif;font-weight:600;font-size:40px;letter-spacing:.08em;padding:18px 56px;border-radius:60px;white-space:nowrap}}
.cta{{flex:none;max-width:620px;text-align:center;font-family:Lora,serif;font-weight:500;font-size:34px;line-height:1.38;color:#E8DFCF;opacity:.92}}
.foot{{flex:none;font-family:Cinzel,serif;font-weight:600;font-size:24px;letter-spacing:.32em;color:{GOLD};opacity:.8}}
.footabs{{position:absolute;top:1214px;left:0;right:0;text-align:center}}
.thead{{position:absolute;top:520px;left:110px;right:110px;text-align:center;font-family:Tiro,serif;font-size:92px;line-height:1.3;color:{GOLD}}}
.tsub{{position:absolute;top:900px;left:120px;right:120px;text-align:center;font-family:Lora,Tiro,serif;font-style:italic;font-size:52px;line-height:1.35;color:{CREAM}}}
.chat{{position:absolute;left:80px;right:80px;top:400px}}
.chathead{{font-family:Lora,serif;font-weight:500;font-size:30px;color:#9fb3a8;text-align:center;margin-bottom:34px}}
.msg{{max-width:760px;padding:26px 34px 18px;border-radius:34px;margin-bottom:26px;font-family:Tiro,serif;font-size:58px;line-height:1.3;position:relative}}
.them{{background:#24302a;color:{CREAM};border-bottom-left-radius:8px}}
.me{{background:{GOLD};color:{BG};margin-left:auto;border-bottom-right-radius:8px}}
.time{{display:block;font-family:Lora,serif;font-weight:500;font-size:24px;opacity:.6;text-align:right;margin-top:6px}}
.typing{{width:auto;display:inline-block;white-space:nowrap;padding:30px 30px 26px}}
.typing i{{display:inline-block;width:18px;height:18px;border-radius:50%;background:{CREAM};opacity:.6;margin-right:12px}}
"""
WM = "<div class='wm'>TAROT BY CHARU</div>"


def html_page(body, extra_body_class=""):
    # Tiro sets the danda (।) with a wide left gap that reads like a typo; pull it in everywhere.
    body = body.replace("।", "<span style='margin-left:-0.22em'>।</span>")
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body class='{extra_body_class}'>{body}</body></html>")


class Renderer:
    def __init__(self, work):
        from playwright.sync_api import sync_playwright
        self.work = work
        self.pw = sync_playwright().start()
        self.b = self.pw.chromium.launch()
        self.pg = self.b.new_page(viewport={"width": W, "height": H})

    def png(self, html, out, transparent):
        tmp = self.work / "_page.html"
        tmp.write_text(html, encoding="utf-8")
        self.pg.goto(tmp.as_uri(), wait_until="load")
        self.pg.evaluate("document.fonts.ready")
        self.pg.wait_for_timeout(400)
        self.pg.screenshot(path=str(out), omit_background=transparent)
        return out

    def close(self):
        self.b.close(); self.pw.stop()


def card_img(key):
    p = KIT / "cards" / f"{key}.jpg"
    if not p.exists():
        raise SystemExit(f"card scan missing: {p} (fetch it with hf_fs attach, see SKILL.md)")
    return p.as_uri()


def text_bbox(png, below=None):
    """Bounding box of bright text pixels (ignores the gradient and the bottom brand mark band)."""
    a = np.asarray(Image.open(png).convert("RGBA")).astype(int)
    lum = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
    m = (lum > 120) & (a[..., 3] > 200)
    m[1752:, :] = False  # brand mark in the bottom letterbox band (intentionally under the IG UI)
    ys, xs = np.where(m)
    if not len(xs):
        return None, False
    bb = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    rail = bool(m[SAFE["rail_y"]:, SAFE["rail_x"] + 1:].any())
    return bb, rail


def check_safe(png, name, problems):
    bb, rail = text_bbox(png)
    if bb is None:
        return None
    x0, y0, x1, y1 = bb
    if x0 < SAFE["x0"] or x1 > SAFE["x1"] or y0 < SAFE["y0"] or y1 > SAFE["y1"] or rail:
        problems.append(f"{name}: text outside Instagram safe area {bb} (rail hit: {rail})")
    return bb


def still_to_mp4(png, dur, out, zoom=False):
    vf = f"scale={W}:{H},setsar=1,fps={FPS},format=yuv420p"
    if zoom:
        n = int(dur * FPS)
        vf = (f"scale={W*2}:{H*2},zoompan=z='1+0.03*on/{n}':x='iw/2-(iw/zoom/2)':y='{2*760}*(1-1/zoom)'"
              f":d={n}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p")
    sh(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", f"{dur:.3f}", "-framerate", str(FPS), "-i", str(png),
        "-vf", vf, "-t", f"{dur:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)])


def build_clip(sc, d, work, R, i, problems, cuts, t_offset, not_last):
    src = d / sc["src"]
    if not src.exists():
        raise SystemExit(f"clip missing: {src}")
    cdur = probe_dur(src)
    # 'hold' = seconds the last frame stays fully visible; the fade to the next scene comes after it
    hold = float(sc.get("hold", 0)) + (FADE if not_last else 0)
    total = cdur + hold
    texts = sc.get("texts", [])
    if not texts or texts[0]["t"] > 0.5:
        problems.append(f"scene {i}: first text must appear within 0.5 s")
    ins, filt, chain = ["-i", str(src)], [], "[0:v]"
    g = "eq=gamma='if(lt(t,2),1.28,if(lt(t,4),1.28-0.14*(t-2),1))':saturation=1.04:eval=frame," if sc.get("brighten") else ""
    filt.append(f"[0:v]{g}scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS}"
                f"{f',tpad=stop_mode=clone:stop_duration={hold}' if hold else ''},format=yuva420p[v0]")
    last = "v0"
    for k, tx in enumerate(texts):
        t0 = float(tx["t"]); t1 = float(texts[k + 1]["t"]) if k + 1 < len(texts) else total
        style = tx.get("style", "hi")
        png = R.png(html_page(f"<div class='grad'></div><div class='block'><div class='{style} shadow'>{tx['text']}</div>"
                              f"<div class='rule'></div></div>{WM}"), work / f"s{i}_t{k}.png", True)
        check_safe(png, f"scene {i} text {k}", problems)
        ins += ["-loop", "1", "-t", f"{t1 - t0 + 0.05:.3f}", "-i", str(png)]
        fade = "" if t0 == 0 else ",fade=in:st=0:d=0.2:alpha=1"
        filt.append(f"[{k+1}:v]format=rgba{fade},setpts=PTS-STARTPTS+{t0}/TB[o{k}]")
        en = f"between(t,{t0},{t1})" if k + 1 < len(texts) else f"gte(t,{t0})"
        filt.append(f"[{last}][o{k}]overlay=0:0:enable='{en}':eof_action=pass[v{k+1}]")
        last = f"v{k+1}"
        if t0 > 0:
            cuts.append(t_offset + t0)
    filt.append(f"[{last}]format=yuv420p,trim=0:{total:.3f},setpts=PTS-STARTPTS[out]")
    out = work / f"scene{i}.mp4"
    sh(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", "[out]", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)])
    return out, total, (src if has_audio(src) else None), cdur


def build_card(sc, i, work, R, problems):
    parts = ["<div class='stack'>", f"<div class='lab'>{sc.get('label', 'THE CARD’S MESSAGE')}</div>",
             f"<img class='card' src='{card_img(sc['card'])}'>"]
    if sc.get("sub"):
        it = " it" if not any('ऀ' <= ch <= 'ॿ' for ch in sc["sub"]) else ""
        parts.append(f"<div class='sub{it}'>{sc['sub']}</div>")
    if sc.get("cta"):
        parts.append(f"<div class='btn'>{sc['cta']}</div>")
    if sc.get("line"):
        parts.append(f"<div class='cta'>{sc['line']}</div>")
    parts.append("<div class='foot'>TAROT BY CHARU</div></div>")
    png = R.png(html_page("".join(parts), "dark"), work / f"s{i}.png", False)
    check_safe(png, f"scene {i} card", problems)
    out = work / f"scene{i}.mp4"
    still_to_mp4(png, float(sc.get("dur", 3.5)), out, sc.get("zoom", False))
    if sc.get("zoom"):
        last = work / f"s{i}_last.png"
        sh(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", str(out), "-frames:v", "1", str(last)])
        check_safe(last, f"scene {i} card (end of zoom)", problems)
    return out


def build_text(sc, i, work, R, problems):
    body = f"<div class='thead'>{sc['head']}</div>" + (f"<div class='tsub'>{sc['sub']}</div>" if sc.get("sub") else "") \
        + "<div class='footabs'><span class='foot'>TAROT BY CHARU</span></div>"
    png = R.png(html_page(body, "dark"), work / f"s{i}.png", False)
    check_safe(png, f"scene {i} text", problems)
    out = work / f"scene{i}.mp4"
    still_to_mp4(png, float(sc.get("dur", 3)), out, sc.get("zoom", False))
    return out


def build_chat(sc, i, work, R, problems, cuts, t_offset):
    steps, dur = sc["steps"], float(sc.get("dur", 6))
    if steps[0]["t"] > 0.5:
        problems.append(f"scene {i}: first chat bubble must appear within 0.5 s")
    segs, shown = [], []
    for k, st in enumerate(steps):
        t1 = float(steps[k + 1]["t"]) if k + 1 < len(steps) else dur
        if not st.get("typing"):
            shown.append(st)
        bubbles = "".join(
            f"<div class='msg {m['from']}'>{m['text']}" + (f"<span class='time'>{m['time']}</span>" if m.get("time") else "") + "</div>"
            for m in shown)
        if st.get("typing"):
            bubbles += "<div class='msg them typing'><i></i><i></i><i></i></div>"
        head = f"<div class='chathead'>{sc.get('header', '')}</div>" if sc.get("header") else ""
        png = R.png(html_page(f"<div class='chat'>{head}{bubbles}</div><div class='footabs'><span class='foot'>TAROT BY CHARU</span></div>", "dark"),
                    work / f"s{i}_{k}.png", False)
        check_safe(png, f"scene {i} chat step {k}", problems)
        seg = work / f"s{i}_{k}.mp4"
        still_to_mp4(png, t1 - float(st["t"]), seg)
        segs.append(seg)
        if st["t"] > 0:
            cuts.append(t_offset + float(st["t"]))
    lst = work / f"s{i}_list.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segs))
    out = work / f"scene{i}.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out


def main():
    spec_p, d = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    spec = json.loads(spec_p.read_text(encoding="utf-8"))
    work = d / "_work"; shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    problems, cuts, clip_audio = [], [], []
    R = Renderer(work)
    scene_files, durs, t = [], [], 0.0
    try:
        for i, sc in enumerate(spec["scenes"]):
            if sc["type"] == "clip":
                f, dur, aud, cdur = build_clip(sc, d, work, R, i, problems, cuts, t, i + 1 < len(spec["scenes"]))
                if aud:
                    clip_audio.append((aud, t, cdur))
            elif sc["type"] == "card":
                f = build_card(sc, i, work, R, problems); dur = float(sc.get("dur", 3.5))
            elif sc["type"] == "text":
                f = build_text(sc, i, work, R, problems); dur = float(sc.get("dur", 3))
            elif sc["type"] == "chat":
                f = build_chat(sc, i, work, R, problems, cuts, t); dur = float(sc.get("dur", 6))
            else:
                raise SystemExit(f"unknown scene type {sc['type']}")
            scene_files.append(f); durs.append(dur)
            t += dur - (FADE if i + 1 < len(spec["scenes"]) else 0)
            if i + 1 < len(spec["scenes"]):
                cuts.append(t + FADE / 2)
    finally:
        R.close()

    total = sum(durs) - FADE * (len(durs) - 1)
    if total >= 15:
        problems.append(f"reel is {total:.1f}s; must be under 15s")

    # video: chain fade-through-black between scenes
    ins, filt, last, off = [], [], "0:v", 0.0
    for f in scene_files:
        ins += ["-i", str(f)]
    for k in range(1, len(scene_files)):
        off += durs[k - 1] - FADE
        filt.append(f"[{last}][{k}:v]xfade=transition=fadeblack:duration={FADE}:offset={off:.3f}[x{k}]")
        last = f"x{k}"
    video = work / "video.mp4"
    if filt:
        sh(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", f"[{last}]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(video)])
    else:
        shutil.copy(scene_files[0], video)

    # audio: brand music (bells on each cut) + the clip's own ambience underneath
    wav = work / "music.wav"
    sh([sys.executable, "-I", str(KIT / "music.py"), f"{total:.2f}", ",".join(f"{c:.2f}" for c in sorted(set(cuts))) or "0", str(wav),
        str(spec.get("music_seed", 7))])
    ains, af, mix = ["-i", str(wav)], [f"[1:a]atrim=0:{total:.3f},afade=out:st={max(total-0.8,0):.2f}:d=0.8[m]"], ["[m]"]
    for k, (aud, start, cdur) in enumerate(clip_audio):
        ains += ["-i", str(aud)]
        af.append(f"[{k+2}:a]loudnorm=I=-30:TP=-6,atrim=0:{cdur:.3f},afade=out:st={max(cdur-0.5,0):.2f}:d=0.5,"
                  f"adelay={int(start*1000)}:all=1,apad=whole_dur={total:.3f}[c{k}]")
        mix.append(f"[c{k}]")
    af.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    out = d / spec.get("output", "reel.mp4")
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(video), *ains, "-filter_complex", ";".join(af),
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}",
        "-movflags", "+faststart", str(out)])

    # evidence: contact sheet + safe-zone sheet from the final file
    times = [0.05] + [c + 0.45 for c in sorted(set(cuts))] + [total - 0.1]
    frames = []
    for k, tt in enumerate(times):
        fp = work / f"f{k}.png"
        sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{min(tt, total-0.05):.2f}", "-i", str(out), "-frames:v", "1", str(fp)])
        frames.append(Image.open(fp).convert("RGB"))
    def sheet(ims, path, overlay=False):
        from PIL import ImageDraw
        tw, th = 270, 480
        c = Image.new("RGB", (tw * len(ims), th))
        for k, im in enumerate(ims):
            im = im.copy()
            if overlay:
                o = Image.new("RGBA", im.size, (0, 0, 0, 0)); dr = ImageDraw.Draw(o); R_ = (220, 40, 40, 110)
                dr.rectangle([0, 0, W, SAFE["y0"]], fill=R_); dr.rectangle([0, SAFE["y1"], W, H], fill=R_)
                dr.rectangle([SAFE["rail_x"], SAFE["rail_y"], W, SAFE["y1"]], fill=R_)
                dr.rectangle([0, SAFE["y0"], SAFE["x0"], SAFE["y1"]], fill=R_); dr.rectangle([SAFE["x1"], SAFE["y0"], W, SAFE["rail_y"]], fill=R_)
                im = Image.alpha_composite(im.convert("RGBA"), o).convert("RGB")
            c.paste(im.resize((tw, th)), (tw * k, 0))
        c.save(path, quality=88)
    sheet(frames, d / "contact.jpg"); sheet(frames, d / "safezone.jpg", overlay=True)
    shutil.rmtree(work, ignore_errors=True)

    rep = {"pass": not problems, "duration": round(total, 2), "cuts": [round(c, 2) for c in sorted(set(cuts))],
           "problems": problems, "output": str(out.name)}
    (d / "build.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
