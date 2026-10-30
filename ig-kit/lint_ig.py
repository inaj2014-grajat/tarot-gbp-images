#!/usr/bin/env python3
"""Check an Instagram post (caption + slide spec) against Instagram limits and Tarot by Charu brand rules.

Usage: python3 lint_ig.py --caption caption.txt --spec spec.json
Prints JSON. Exit 0 = pass, 1 = errors (do not publish).
"""
import argparse, json, pathlib, re, sys

DEVA = re.compile("[ऀ-ॿ]")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF]")
# common Hindi words written in Latin script -> Hindi must be in Devanagari
ROMAN_HI = {"hai", "hain", "nahi", "nahin", "kya", "aur", "mein", "tum", "tumhara", "apna", "apni", "apne",
            "karo", "kar", "ho", "ko", "se", "ka", "ki", "ke", "dil", "sach", "log", "kehenge", "yeh", "woh",
            "toh", "bhi", "ab", "jo", "raat", "subah", "pyaar", "pyar", "darr", "dar", "kab", "kaise", "kyun",
            "baat", "saath", "ghar", "zaroor", "zaruri", "mat", "bas", "hum", "unka", "unki", "sabke", "liye"}
ERR = [
    (r"#\w+", "hashtag in caption (brand rule: hashtags go in the first comment, never the caption)"),
    (r"https?://|www\.|wa\.me|\.com\b|\.in\b", "link (not clickable in captions; brand rule: DM trigger instead)"),
    (r"(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b", "phone number"),
    (r"[\w.+-]+@[\w-]+\.[\w.]+", "email address"),
    (r"\b(guarantee[sd]?|100\s?%|definitely will|will surely|pakka|confirm(ed)? result|cure[sd]?|miracle)\b",
     "guarantee/claim language (brand rule: guidance, never certainty)"),
    (r"पक्का|गारंटी|ज़रूर होगा|जरूर होगा|निश्चित रूप से होगा", "guarantee language in Hindi"),
    (r"\b(you will (get|marry|meet|receive|find|lose|win)|will happen|is coming (to|into) your life|your ex will)\b",
     "definitive prediction (brand rule: frame as guidance and reflection)"),
    (r"\b(black magic|vashikaran|curse|evil eye removal|remedy for)\b", "restricted / fear-based service claim"),
    (r"\b(rahu|ketu|saturn|shani|mercury)\b[^.\n]{0,40}\b(will (ruin|destroy|harm|punish)|wrath|danger)", "fear framing of a planet"),
    (r"\b(diagnos\w*|medical advice|legal advice|investment advice|stock tip)\b", "health/legal/financial advice wording"),
]
WARN = [
    (r"\b(she|her)\b", "third-person she/her; brand voice is second-person 'you'"),
    (r"\bPOV\b", "POV hook is saturated; prefer a Named Situation hook"),
    (r"\blink in bio\b", "link-in-bio CTA; brand uses DM triggers"),
]


def roman_hindi(s):
    hits = []
    for line in s.splitlines():
        if DEVA.search(line):
            continue
        words = re.findall(r"[a-zA-Z]+", line.lower())
        h = [w for w in words if w in ROMAN_HI]
        # 'ho', 'se', 'ka' etc. can appear in English rarely; need 2+ distinct hits or 30%+ of the line
        if len(set(h)) >= 2 or (words and len(h) / len(words) >= 0.3 and len(h) >= 1 and len(words) <= 6 and h[0] not in {"ho", "se", "ka", "ki", "ke", "ab", "jo", "bas", "mat", "dar"}):
            hits.append(line.strip()[:60])
    return hits


def slide_texts(spec):
    out = []
    for i, s in enumerate(spec.get("slides", []), 1):
        for k in ("head", "sub", "title", "label", "quote", "trans", "line", "cta"):
            if s.get(k):
                out.append((f"slide {i} {k}", s[k]))
    return out


def lint(caption, spec):
    errors, warnings = [], []
    cap = caption.strip()
    n = len(cap)
    if n > 2200:
        errors.append(f"caption too long: {n} chars (Instagram max 2200)")
    if n < 120:
        warnings.append(f"caption short: {n} chars")
    texts = [("caption", cap)] + slide_texts(spec)
    for where, s in texts:
        for pat, msg in ERR:
            if where != "caption" and msg.startswith("hashtag"):
                continue
            m = re.search(pat, s, re.I)
            if m:
                errors.append(f"{where}: {msg} -> '{m.group(0)}'")
        for line in roman_hindi(s):
            errors.append(f"{where}: Hindi written in Latin letters (write Hindi in Devanagari) -> '{line}'")
    for pat, msg in WARN:
        m = re.search(pat, cap, re.I)
        if m:
            warnings.append(f"caption: {msg} -> '{m.group(0)}'")
    if len(EMOJI.findall(cap)) > 3:
        warnings.append("more than 3 emoji in caption")
    if not re.search(r"\bDM\b", cap) and not any("DM" in s for _, s in slide_texts(spec)):
        warnings.append("no DM trigger (CLARITY / TRUTH) in caption or slides")
    if not re.search(r"\bsave\b|\bsend this\b|\bshare\b", cap, re.I):
        warnings.append("no save/share trigger in caption")
    first = cap.split("\n")[0]
    if len(first) > 125:
        warnings.append(f"first caption line {len(first)} chars; Instagram cuts at ~125 before 'more'")
    slides = spec.get("slides", [])
    fmt = spec.get("format", "carousel")
    if fmt == "carousel" and not 3 <= len(slides) <= 10:
        errors.append(f"carousel needs 3-10 slides, has {len(slides)}")
    if fmt == "reel" and not 3 <= len(slides) <= 5:
        errors.append(f"reel needs 3-5 slides (under 15s), has {len(slides)}")
    if slides:
        if slides[0].get("type") != "hook":
            errors.append("slide 1 must be the hook (text on frame 1)")
        hw = len(re.findall(r"\S+", slides[0].get("head", "")))
        if hw > 12:
            warnings.append(f"hook headline {hw} words; keep to 12 or fewer")
        if not any(s.get("type") == "card" for s in slides):
            errors.append("no card slide: every post shows a real Rider-Waite card")
    return {"pass": not errors, "caption_chars": n, "errors": errors, "warnings": warnings}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--caption", required=True)
    ap.add_argument("--spec", required=True)
    a = ap.parse_args()
    r = lint(pathlib.Path(a.caption).read_text(encoding="utf-8"), json.loads(pathlib.Path(a.spec).read_text(encoding="utf-8")))
    print(json.dumps(r, indent=2, ensure_ascii=False))
    sys.exit(0 if r["pass"] else 1)
