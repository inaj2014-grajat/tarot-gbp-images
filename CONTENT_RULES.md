# Tarot by Charu — content rules (Rajat's approvals and rejections)

Read this file at the start of every draft and revise run, for Instagram and Google. These rules come from Rajat's own feedback, and they sit on top of each skill's brand canon. When a skill default conflicts with this file, this file wins. Add new rules here whenever Rajat rejects or reworks something, quoting his words, so the same rework never happens twice.

Last updated: 9 Nov 2026.

## 1. Every post ends on hope
Every post and video, whatever the theme, must leave her feeling good, or hopeful that talking to Charu will help.

The shape is: name the tension lightly in the hook (that's what stops the scroll), then turn to warmth and possibility, and end with Charu as a warm invitation.

| Theme | Approved hopeful turn | Card used |
|---|---|---|
| Log Kya Kahenge (marriage and timeline questions) | "What if this year you chose you?" | The Star |
| Guilt about saying no to family | "Saying no with love is still love." | Strength |
| Invisible labour at work | "Your effort deserves to be seen." | Six of Wands |

Prefer cards that carry hope (The Star, Strength, Six of Wands, The Sun, Ten of Cups, Ace of Cups, Three of Cups, Four of Wands, Temperance). A "hard" card (Ten of Wands, Four of Cups, Tower, Nine of Swords) can be used only if the post clearly turns it toward relief and hope.

Never let hope become a prediction. "Your effort deserves to be seen" is allowed. "Your effort is about to be seen" is not.

## 2. Captions
Write captions the way Rajat chose them (2 Nov, The Star, option B).

The approved caption:
```
What if this Diwali, you chose you?

रिश्तेदार पूछेंगे, “शादी कब?” तुम मुस्कुराकर कहना, “जब सही लगेगा।”

The Star reminds you that hope does not need anyone's permission. Look closer: one big star, and seven small ones shining right beside it.

Send this to the friend who dreads the family lunch. DM TRUTH and Charu can help you find your own answer.
```

What made this caption work:
- **A ready-to-use line she can say or send.** Here it's a witty, warm reply to the relatives' question. Give her a line to use, not a reflection to read.
- **One short, concrete card line.** Name what is actually in the card.
- **A send or save trigger tied to a real moment,** such as the family lunch.
- **The DM trigger, followed by a warm promise of help from Charu.** Use "can help", never "will".

Rajat rejected two other versions:
- A reflective, abstract version: "The Star comes after the storm… Your light and theirs can both shine. Neither has to dim."
- A softer rewrite in the same mood.

Avoid poetic metaphors about light, storms or shining. Be playful-warm and practical instead.

## 3. Short Hindi lines (slide 4 closing line and similar)
- He rejected "तुम्हारी रोशनी भी ज़रूरी है।" (an abstract metaphor) and chose "तुम्हारी ज़िंदगी, तुम्हारी रफ़्तार।"
- For a wedding post (2 Nov sample) he rejected "जवाब बाद में। मिठाई पहले।" and chose "तुम्हारी शादी, तुम्हारा फ़ैसला।" Don't make a joke line the card's message.
- So prefer short, punchy, parallel lines about her own life, choice or pace, over "your light / your glow" imagery.
- Hindi is always in Devanagari, even single words. "zindagi" becomes ज़िंदगी.
- Everyday English words stay in English, in Roman letters, even inside a Hindi line. Rajat rejected कज़िन: "I don't like cousin in Hindi. It's a common word so can be in English." So: "Cousin की शादी।"

## 3b. Hindi must sound like real people talking (Rajat, 5 Nov 2026)
Rajat rejected both "Kab badlega" Reels (#1 Temperance, #2 Pick a card): "I think the issue is with you Hindi messages. Doesn't look/sound real or common usage."

The lines he rejected, so they aren't repeated:
- "पता नहीं यार। पर कल का एक काम बता, साथ करते हैं।"
- "पानी cup से cup तक। थोड़ा-थोड़ा भी बदलाव ही है।"
- "जब मन पूछे, “कब बदलेगा?” तो कहना, “पता नहीं। पर आज 1, 2 या 3 तो चुन सकती हूँ।”"
- "बिना लगाम, खुली बाँहें। थोड़ा ढीला छोड़ना भी ठीक है।"
- "छड़ी पर नए पत्ते। शुरू करने की इजाज़त नहीं चाहिए।"
- "तीन cup, एक साथ ऊपर। सब अकेले उठाना ज़रूरी नहीं।"

On 6 Nov he added: "It's a bad Hindi text. Unrelatable, non captivating." So a line must also land on a moment she has lived (a boss, a group chat, a girls' night that keeps getting cancelled, comparing her life on Instagram), not on what the card looks like. Card imagery goes in the caption's card line, not in the Hindi. And when a post is marked Rejected with feedback, treat it as Changes Requested: a 6 Nov miss happened because Rejected rows were never reworked.

Before any Hindi line goes in: would a woman in Delhi actually say or text this, in these words? A line that is an English thought translated into Hindi fails, and so does a card description written as Hindi poetry. New Hindi lines are not final until Rajat has seen them.

## 3a. The last slide must lead to Charu (Rajat, 2 Nov 2026)
Rajat: "I am not sure how this is driving the viewer to Charu." So the last slide names Charu and gives a reason to message her. He also said its text was longer than he likes.

Shape: one short Hindi line from the card, then the invitation, then the DM word. No separate closing line and no English translation on the slide. The caption carries the English.

Default invitation, on DM TRUTH posts (his line, "Yes I like that line on last slide"):
"Charu से पूछो, ताकि तुम्हें पता हो।" / "बस अपने लिये।"
Caption form: "DM TRUTH to ask Charu, so that you know. Just for yourself."

## 4. Image text
- Every word visible in an image must be correct and readable. That includes card names printed in base photos. If a card label in a photo is small or garbled, don't use that photo. A blur patch over it looks worse than the problem.
- All text must be easy to read on a phone, above all the English line. Rajat on a slide where it sat on bright garlands: "English is barely readable." `render.py` now keeps text on a dark band and stops with READABILITY FAIL below 4.5:1 contrast (3:1 for large text). Fix the placement or photo; never lower the limit.
- Label lines need proper punctuation, e.g. "A kind ‘no’ is still love." not "A kind no is still love". Quote a word when it is being said, and end a full sentence with a full stop.
- Keep text inside the Instagram frame. Rajat, 2 Nov 2026: "check for instagram borders.. run every post through emulator." `render.py` stops with FRAME FAIL if text is under 40 px from a side or 80 px from the top or bottom, and writes `phone.jpg`: the grid crop and each slide at Pixel 7 size. Look at `phone.jpg` before the row goes up for approval. Fix the spec; never lower the limits. It is a mock in phone mode, not the real app: no Android emulator can run here (no `adb`, no `/dev/kvm`).
- Match the photo to the card when you can. A Card Insight post about Strength shouldn't show a different card if a better photo exists.

## 5. Photos and video
- Rajat wants varied photos, not the same look each week. When the library is thin, get new text-free ones from the sources in §7, and add them to `ig-kit/photos/` and `photos.json` with tags.
- Use candid, natural, understated people: a soft smile at most, face turned partly away, real Indian homes and offices.
- Rajat rejected an AI video with big laughing, over-the-top expressions as "completely fake… no one will watch it". Never use exaggerated expressions in photos or video.
- No unnatural or artificial shimmer, glow or sparkle in photos and video. Rajat: "By sparkle I meant unnatural/artificial shimmer etc."
- When generating a set of images, ask for "one single photograph, one continuous frame". Multi-image requests came back as low-resolution 3-panel collages.

## 6. How to handle Rajat's rework requests
- When he says he doesn't like a caption or a line and gives no wording, give him 2–3 clearly different options with a recommendation. Don't send a single rewrite. In a scheduled run with no one to ask, write the options into Run Log, put option 1 in the row, and set Status to Pending Approval.
- Read Notion page comments as well as the Feedback field. He often leaves feedback as a comment on the Status property.

## 6a. One clear message per post (Rajat, 9 Nov 2026)
On the 11 Nov Google post "How a Clarity Session Works" Rajat wrote: "the post is not clear on what it is trying to say." The draft stacked a festival opener ("After the Diwali rush…") on top of a process explainer, and used abstract lines ("we name the pattern… where your energy is going").
- Each post says one thing. Before writing, finish the sentence "This post tells her that…" in under 15 words, and cut anything that doesn't serve it.
- Don't bolt a timely hook onto an explainer post if it pulls in a second idea. No hook is better than a muddled one.
- Use concrete, everyday words for what happens ("you share your question", "you leave knowing what to do next"), not abstract tarot-speak ("energy", "patterns", "alignment") on its own.

## 7. Where images and video come from (Rajat, 2 Nov 2026)
**Never use Creative Claw.** Rajat: "I don't plan to use Creative Claw." Don't call its tools, even when they are connected to the run.

Try these in order, and write the source used in Run Log.

| Need | First choice | If that isn't available | Last resort |
|---|---|---|---|
| AI video clip | Google Flow in Chrome, model **Veo 3.1 – Fast**, 9:16, x1. Flow's default is another model, so set it each time. Credit limits stay as in `ig-kit/SKILL.md`. | No-clip Reel from text and card scenes (`flowreel.py`) | Skip the row if it is 3+ days away and retry next build run |
| Lifestyle photo | Google Flow in Chrome, model **Nano Banana 2.1**, 3:4, x1. For Google posts, 4:3, cropped to 3:2. | A photo Rajat makes in Gemini and adds by hand | The least recently used photo, plus the "photo library small" note in Run Log |
| Tarot card | The real Rider-Waite scan in `ig-kit/cards/`. Never an AI card. | Fetch the scan from the source in `cards.json` | None |
| Text on images | Rendered by the kit. Never ask an AI to draw text. | None | None |
| Music | `music.py` (local, no licensed audio) | None | None |

Rules for Flow:
- Send the prompt with "using this prompt exactly as written". The Flow agent may not stop to confirm before generating, so check the settings first.
- Download the file the same day. Flow warns that its oldest creations expire.
- Flow images carry a small visible Gemini mark in India. Rajat allowed it on 2 Nov 2026. Never crop, cover or remove any watermark, on video or images. Keep slide text clear of it.
- No per-post AI label is needed for AI photos. Rajat, 2 Nov 2026: the Instagram account is already labelled AI. Reels with an AI video clip keep their label as `ig-kit/SKILL.md` says.
- If Chrome or Flow can't be reached, move to the next source. Never call a different generation tool.
- Make the photos yourself. Rajat, 2 Nov 2026: "dont ask em for photos.. you should be doing it yourself." Ask him only if Chrome or Flow can't be reached.
- Getting a Flow photo into the repo, with no download and no folder access: open the image in Flow and reload the page so it shows the 896x1200 `flow-content.google` file, not the 382x512 thumbnail. Put that image in a full-window overlay at natural size with page JavaScript. Capture it with the Chrome `zoom` action and `save_to_disk`, which keeps full pixels in a PNG; a plain screenshot is scaled down. The window showed 951 px, so take a second capture with the image moved up 249 px. Join the two, check the overlap matches, save as JPG in `ig-kit/photos/`, and remove the overlay.

## 8. Draft with the craft skill (Rajat, 2 Nov 2026)
For Instagram draft, build and revise runs, load the `tarot-post-craft` skill and follow it for the hook, slides and caption. If it isn't installed, carry on without it and say so in Run Log. This file still wins over that skill.

Where the hook is new, put the two hooks not chosen in Run Log so Rajat can swap one in.
