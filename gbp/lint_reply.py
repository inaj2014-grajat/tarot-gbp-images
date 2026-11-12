#!/usr/bin/env python3
import argparse, json, re, sys
ERR = [
    (r"(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b|\b\d{3}[\s.-]\d{3}[\s.-]\d{4}\b", "phone number"),
    (r"https?://|www\.|wa\.me|\.com\b|\.in\b", "link"),
    (r"[\w.+-]+@[\w-]+\.[\w.]+", "email address"),
    (r"#\w+", "hashtag"),
    (r"\b(discount|offer|% off|free session|coupon|promo)\b", "offer/incentive (not allowed in review replies)"),
    (r"\b(change|update|edit|remove|delete|revise)\b.{0,20}\breview\b", "asking to change the review (Google prohibits)"),
    (r"\b(you will|will happen|guarantee[sd]?|100\s?%|definitely)\b", "prediction or guarantee"),
    (r"\b(your|the) (reading|cards?) (showed|said|revealed)\b", "reveals reading content (confidentiality)"),
    (r"\b(fake|liar|lying|never (came|visited)|not a (real )?client)\b", "accusatory language"),
    (r"\b(famil(y|ies)|loved ones?|husband|wife|spouse|partner|children|kids|son|daughter|parents|in-laws|relatives|household)\b", "mentions family or others (keep it about the client)"),
]
def lint(reply, recent=()):
    r = reply.strip(); errors, warnings = [], []
    words = len(re.findall(r"\b[\w'’]+\b", r))
    if words > 55: errors.append(f"too long: {words} words (max 55)")
    elif words < 12: warnings.append(f"very short: {words} words")
    if not r.endswith("— Charu"): errors.append("must end with the signature '— Charu'")
    for pat, msg in ERR:
        m = re.search(pat, r, re.I)
        if m: errors.append(f"{msg} -> '{m.group(0)}'")
    if len(re.findall("[\U0001F300-\U0001FAFF\U00002600-\U000027BF]", r)) > 1: errors.append("more than 1 emoji")
    opener = " ".join(r.split()[:4]).lower()
    for prev in recent:
        if " ".join(prev.split()[:4]).lower() == opener:
            warnings.append(f"same opening as a recent reply: '{opener}'"); break
    return {"pass": not errors, "words": words, "errors": errors, "warnings": warnings}
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--reply", required=True); ap.add_argument("--recent", action="append", default=[])
    a = ap.parse_args(); res = lint(a.reply, a.recent); print(json.dumps(res, ensure_ascii=False)); sys.exit(0 if res["pass"] else 1)
