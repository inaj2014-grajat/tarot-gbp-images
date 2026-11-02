# Tarot by Charu — content rules (Rajat's approvals and rejections)

Read this file at the start of every draft and revise run, for Instagram and Google. These rules come from Rajat's own feedback, and they sit on top of each skill's brand canon. When a skill default conflicts with this file, this file wins. Add new rules here whenever Rajat rejects or reworks something, quoting his words, so the same rework never happens twice.

Last updated: 2 Nov 2026.

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
- So prefer short, punchy, parallel lines about her own life, choice or pace, over "your light / your glow" imagery.
- Hindi is always in Devanagari, even single words. "zindagi" becomes ज़िंदगी.

## 4. Image text
- Every word visible in an image must be correct and readable. That includes card names printed in base photos. If a card label in a photo is small or garbled, don't use that photo. A blur patch over it looks worse than the problem.
- Label lines need proper punctuation, e.g. "A kind ‘no’ is still love." not "A kind no is still love". Quote a word when it is being said, and end a full sentence with a full stop.
- Match the photo to the card when you can. A Card Insight post about Strength shouldn't show a different card if a better photo exists.

## 5. Photos and video
- Rajat wants varied photos, not the same look each week. When the library is thin, get new text-free ones from the sources in §7, and add them to `ig-kit/photos/` and `photos.json` with tags.
- Use candid, natural, understated people: a soft smile at most, face turned partly away, real Indian homes and offices.
- Rajat rejected an AI video with big laughing, over-the-top expressions as "completely fake… no one will watch it". Never use exaggerated expressions in photos or video.
- When generating a set of images, ask for "one single photograph, one continuous frame". Multi-image requests came back as low-resolution 3-panel collages.

## 6. How to handle Rajat's rework requests
- When he says he doesn't like a caption or a line and gives no wording, give him 2–3 clearly different options with a recommendation. Don't send a single rewrite. In a scheduled run with no one to ask, write the options into Run Log, put option 1 in the row, and set Status to Pending Approval.
- Read Notion page comments as well as the Feedback field. He often leaves feedback as a comment on the Status property.

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
- Never crop, cover or remove any watermark, on video or on images. If a downloaded image shows a visible mark, don't use it: go to the next source and note it in Run Log.
- If Chrome or Flow can't be reached, move to the next source. Never call a different generation tool.

## 8. Draft with the craft skill (Rajat, 2 Nov 2026)
For Instagram draft, build and revise runs, load the `tarot-post-craft` skill and follow it for the hook, slides and caption. If it isn't installed, carry on without it and say so in Run Log. This file still wins over that skill.

Where the hook is new, put the two hooks not chosen in Run Log so Rajat can swap one in.
