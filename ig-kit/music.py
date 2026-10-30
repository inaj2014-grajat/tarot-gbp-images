"""Original ambient track for Tarot by Charu Reels: tanpura drone + pad + bell plucks.
Fully synthesized (no samples, no licensed audio), so there is no music-rights risk.
Usage: python3 music.py DURATION CUT1,CUT2,... OUT.wav [SEED]
Bells land on each slide cut."""
import numpy as np
from scipy.signal import lfilter, butter
from scipy.io import wavfile
import pathlib, sys

SR = 44100
DUR = float(sys.argv[1])
CUTS = [float(x) for x in sys.argv[2].split(",")]
OUT = pathlib.Path(sys.argv[3])
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 7
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(SEED)

def env_exp(n, tau):
    return np.exp(-np.arange(n) / (SR * tau))

def place(buf, sig, start):
    i = int(start * SR)
    if i >= len(buf): return
    sig = sig[: len(buf) - i]
    buf[i : i + len(sig)] += sig

# --- Tanpura: Pa - Sa' - Sa' - Sa cycle, each pluck rich in harmonics with jawari buzz ---
def tanpura_pluck(f0, length=4.0, amp=1.0):
    n = int(length * SR); tt = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 22):
        # jawari: upper harmonics bloom slightly after the attack, then fade
        bloom = (1 - np.exp(-tt / (0.05 + 0.012 * k))) * np.exp(-tt / (2.6 / (1 + 0.08 * k)))
        detune = 1 + rng.normal(0, 0.0007)
        s += (1.0 / k ** 1.05) * bloom * np.sin(2 * np.pi * f0 * k * detune * tt + rng.uniform(0, 6.28))
    return amp * s / 6.0

SA, PA_LOW, SA_HIGH = 146.83, 110.00, 146.83 * 2 / 2  # D3, A2, D3 (two Sa strings)
drone = np.zeros(N)
cycle = [(PA_LOW, 0.85), (SA_HIGH, 0.7), (SA_HIGH, 0.7), (SA / 2, 1.0)]
step, tcur, i = 0.62, 0.0, 0
while tcur < DUR:
    f, a = cycle[i % 4]
    place(drone, tanpura_pluck(f, 4.5, a), tcur)
    tcur += step * (1.6 if i % 4 == 3 else 1.0)
    i += 1

# --- Pad: D minor (D4 F4 A4) slow swell, warm ---
pad = np.zeros(N)
for f, a in [(293.66, 1.0), (349.23, 0.7), (440.0, 0.8), (146.83, 0.6)]:
    for d in (-0.6, 0.6):  # gentle chorus
        pad += a * np.sin(2 * np.pi * (f + d) * t)
swell = 0.5 - 0.5 * np.cos(2 * np.pi * t / 9.0)
pad *= (0.35 + 0.65 * swell)
b, a_ = butter(2, 1400 / (SR / 2), "low")
pad = lfilter(b, a_, pad) / 6.0

# --- Bells (Karplus-Strong) on each slide change, D minor pentatonic ---
def ks(f, length=3.5, damp=0.996):
    n = int(length * SR); p = int(SR / f)
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for j in range(n):
        out[j] = buf[j % p]
        buf[j % p] = damp * 0.5 * (buf[j % p] + buf[(j + 1) % p])
    # add a soft sine "bell" body for clarity
    tt = np.arange(n) / SR
    out = 0.55 * out + 0.45 * np.sin(2 * np.pi * f * tt) * env_exp(n, 1.1)
    return out * np.minimum(1, tt / 0.004)

bells = np.zeros(N)
notes = [587.33, 698.46, 880.0, 783.99, 587.33]        # D5 F5 A5 G5 D5
place(bells, ks(notes[0], 4.0) * 0.55, 0.35)
for k, c in enumerate(CUTS):
    f = notes[1 + k % (len(notes) - 1)]
    place(bells, ks(f, 4.0) * 0.6, c)
    place(bells, ks(f / 2, 4.0) * 0.25, c + 0.02)      # soft octave below
# final resolving chord on the last slide
for f in (293.66, 440.0, 587.33):
    place(bells, ks(f, 5.0, 0.9975) * 0.28, CUTS[-1] + 1.4)

mix = 0.95 * drone + 0.55 * pad + 0.75 * bells

# --- Reverb (Schroeder): 4 combs + 2 allpasses ---
def comb(x, d, g):
    a = np.zeros(d + 1); a[0] = 1; a[d] = -g
    return lfilter([1], a, x)
def allpass(x, d, g):
    b = np.zeros(d + 1); b[0] = -g; b[d] = 1
    a = np.zeros(d + 1); a[0] = 1; a[d] = -g
    return lfilter(b, a, x)
def reverb(x, pre=0):
    wet = sum(comb(x, int(SR * dt), g) for dt, g in [(0.0297, .80), (0.0371, .79), (0.0411, .78), (0.0437, .77)]) / 4
    wet = allpass(allpass(wet, int(SR * 0.005), 0.7), int(SR * 0.0017), 0.7)
    return wet

wl, wr = reverb(mix), reverb(np.roll(mix, int(SR * 0.011)))
L = 0.62 * mix + 0.55 * wl
R = 0.62 * mix + 0.55 * wr
# fades
fade_in = np.minimum(1, t / 0.6)
fade_out = np.clip((DUR - t) / 1.6, 0, 1) ** 1.5
L *= fade_in * fade_out; R *= fade_in * fade_out
st = np.stack([L, R], axis=1)
st = st / np.max(np.abs(st)) * 0.89  # peak about -1 dBFS
wavfile.write(OUT, SR, (st * 32767).astype(np.int16))
print(OUT, f"{DUR:.2f}s", "peak", float(np.max(np.abs(st))))
