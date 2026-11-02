# Tarot by Charu — Instagram production kit

Used by the `tarot-ig-publisher` skill. Everything renders in a cloud workspace with no design app.

| File | What it does |
|---|---|
| `render.py spec.json OUT/` | Carousel or Reel slides, 1080x1350 JPEG, plus `contact.jpg` for review. For carousels, also `phone.jpg`; exit 3 = text outside the Instagram frame |
| `phone_view.py POST_DIR out.jpg [slides...]` | Mock phone view of a carousel: 3:4 grid crop and each slide in the feed, in Chrome's Pixel 7 mode. Not the real app |
| `reel.py OUT/ reel.mp4 [seed]` | 1080x1920 Reel from rendered slides, with an original synthesized track |
| `music.py DUR CUTS out.wav [seed]` | Tanpura drone + pad + bells on each cut. No samples, no licensed audio |
| `flowreel.py spec.json OUT/` | Series Reel from scenes (AI clip with timed text, chat bubbles, card end slides), fade-through-black, 2 s hold, brand music; checks the Instagram safe area, length and frame-1 text; writes `reel.mp4`, `contact.jpg`, `safezone.jpg`, `build.json` (exit 1 = do not publish) |
| `fonts/` | Cinzel, Lora, Tiro Devanagari Hindi (OFL) used by `flowreel.py` |
| `lint_ig.py --caption c.txt --spec s.json` | Instagram limits + brand rules. Exit 1 = do not publish |
| `cards.json` | All 78 Rider-Waite (1909, public domain) cards → Hugging Face file |
| `cards/` | Cached card scans (`<key>.jpg`). Fetch missing ones with hf_fs `attach` |
| `photos/` + `photos.json` | Text-free lifestyle photos (Gemini), tagged |
| `assets/velvet.jpg` | Backdrop for the card slide |

Fonts (Cinzel, Lora, Tiro Devanagari Hindi) download from github.com/google/fonts on first run.
