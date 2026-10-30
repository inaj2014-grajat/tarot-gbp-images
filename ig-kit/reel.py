#!/usr/bin/env python3
"""Build a 1080x1920 Instagram Reel from rendered carousel slides + an original synthesized track.

Usage:
  python3 reel.py SLIDES_DIR OUT.mp4 [SEED]

Takes every NN-*.jpg in SLIDES_DIR (output of render.py), in order.
Timing: first slide 2.7s (hook, text on screen from frame 1), middle slides 3.0s,
last slide 4.4s; 0.4s fade-through-black between slides. 4 slides -> ~12s, 5 -> ~15s.
Each slide: blurred, darkened copy fills 9:16; the 4:5 slide sits centred with a slow 1.00->1.035 push-in.
Music: music.py, bells timed to each cut. Prints total length and cut times.
"""
import pathlib, subprocess, sys

KIT = pathlib.Path(__file__).resolve().parent
X, FPS = 0.4, 30


def main():
    sd, out = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
    seed = sys.argv[3] if len(sys.argv) > 3 else "7"
    slides = sorted(p for p in sd.glob("[0-9][0-9]-*.jpg"))
    if len(slides) < 3:
        sys.exit("need at least 3 slides")
    n = len(slides)
    durs = [2.7] + [3.0] * (n - 2) + [4.4]
    total = sum(durs) - X * (n - 1)
    cuts = [round(sum(durs[:k]) - X * k, 2) for k in range(1, n)]
    if total > 15.5:
        print(f"warning: reel is {total:.1f}s; brand target is under 15s — use at most 5 slides")
    wav = out.with_suffix(".wav")
    subprocess.run([sys.executable, "-I", str(KIT / "music.py"), f"{total:.2f}", ",".join(map(str, cuts)), str(wav), seed], check=True)

    inputs, filters = [], []
    for i, (p, d) in enumerate(zip(slides, durs)):
        inputs += ["-loop", "1", "-t", f"{d}", "-i", str(p)]
        fr = int(d * FPS)
        filters.append(
            f"[{i}:v]split[a{i}][b{i}];"
            f"[a{i}]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,eq=brightness=-0.28:saturation=0.8[bg{i}];"
            f"[b{i}]scale=2160:-1,zoompan=z='min(1+0.035*on/{fr},1.035)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1350:fps={FPS}[fg{i}];"
            f"[bg{i}][fg{i}]overlay=0:285,format=yuv420p,setsar=1,fps={FPS}[v{i}]")
    chain, off, prev = [], 0.0, "v0"
    for i in range(1, n):
        off += durs[i - 1] - X
        chain.append(f"[{prev}][v{i}]xfade=transition=fadeblack:duration={X}:offset={off:.2f}[x{i}]")
        prev = f"x{i}"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-i", str(wav),
           "-filter_complex", ";".join(filters + chain), "-map", f"[{prev}]", "-map", f"{n}:a",
           "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    wav.unlink(missing_ok=True)
    # cover frame for Buffer/Instagram thumbnail = slide 1
    print(f"{out}  total={total:.2f}s  cuts={cuts}  size={out.stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()
