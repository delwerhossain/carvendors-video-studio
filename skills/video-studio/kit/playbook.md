# CarVendors editing playbook

How every CarVendors / B&F video is cut. Read with `frame.md` before planning any ad. Built from 2026 short-form
research and a swipe file of live UK car ads (see `swipe-file.md`). Treat numbers as defaults, not laws.

## 1. Pick the length first
| Cut | Use | Shape |
|---|---|---|
| 15 s | paid prospecting, Stories, retargeting | hook 0-3 · one problem line · one proof · CTA last 3 s |
| 30 s | default paid Reels/TikTok/Shorts | hook 0-3 · problem 3-8 · how CarVendors helps 8-18 · proof 18-25 · CTA 25-30 |
| 60 s | story / testimonial / organic | hook · story beats · real review by 20 s · CTA |
Always deliver 2-3 hook variants of the same body (only the first 3 s change). Live UK car ads run 6-33 s.

## 2. The first 3 seconds
- Open on motion or a face, never on a logo. Hook text big, centred, in a green sign panel (y 180-700).
- Hook types that fit CarVendors: question to the viewer ("New to the UK? Not sure which car?"), the problem
  shown ("Hundreds of listings… which one?"), the real customer's own line ("I bought my first car when I
  just moved to the UK"), a direct promise ("Tell us what you need. We'll do the searching.").
- Sound and text must both land the hook: many viewers start muted.

## 3. Proof early
- A real review or real B&F footage by second 8-12 in a 30 s cut (by 20 s in a 60 s cut).
- Proof is a real person, real forecourt, real number. Never an AI person presented as a customer.
- Only quote review counts or ratings after checking the live Google profile on the day.

## 4. Shot rhythm
- Average shot 1.5-3 s. Talking heads: a punch-in or B-roll cutaway every 2-3 s.
- Cut on words: each concrete noun in the voice gets its picture (budget → notebook/£ plate, family → child
  seat, tax → plate "LOW TAX", Northampton → location sign, call → phone screen).
- B-roll goes over A-roll whenever the speaker names a thing; the speaker's audio keeps running underneath.
- UI inserts (the CarVendors form, a phone call screen) appear as a card over footage, like the swipe file's
  valuation screens. Never invent UI text that the real site does not have.

## 5. Captions
- Every spoken word captioned, 2-4 words per chunk, each chunk on screen 0.6-0.9 s.
- Montserrat 800 white with hard ink drop; the active word sits in a yellow plate chip.
- Caption band y 1230-1420; hook text and captions never share a zone.
- Real customers: their exact words, spelling fixed only, fillers not displayed.

## 6. Motion graphics library (kit/components)
| Component | Says | Use |
|---|---|---|
| sign-hook | a question or promise | first 3 s, chapter changes |
| plate-stack | values, needs, specs | "budget · family · low tax" beats |
| info-panel (blue) | a fact or step | "Free · No obligation", how-it-works steps |
| location-sign | a place | "B&F Cars → Northampton" |
| front-plate name tag | who is speaking | real customer / advisor names |
| lane-bg | movement under graphics-only scenes | network search, transitions |
| sign-wipe | chapter transition | problem → solution, story → proof |
| end-card | the action | last 3 s: sign CTA, yellow phone plate, logo card |
Add a new component only when a beat needs one; then add it to this table.

## 7. Picture treatment
- Real people: `Natural Portrait` (media-use treatments). Cars and forecourt: `Product Polish`.
- AI dramatisation footage: make it sit next to phone footage: slight desaturation, soft grain, no extra
  sharpening, shorter shots (≤ 2.5 s) so the AI look never lingers; always the "Dramatisation" label.
- No full-frame light leaks over faces; a white flash only on the cut into real proof.

## 8. Sound
- Voice first. Narration via ElevenLabs `eleven_v4` (British voice; audio tags for emotion), or the
  customer's real voice. Music bed carved under voice (`carve.mjs`), ducked hard under real reviews.
- SFX only on graphic hits (plate drop = soft click/pop, sign wipe = short whoosh). Max one SFX per second.
- Master to -14 LUFS, true peak ≤ -1.5 dB (`work/master.sh` pattern).

## 9. CTA
- One action: "Request a free callback" or "Call 0330 113 1668". Phone number as a yellow plate.
- Say it and show it in the last 3 s; keep it on screen ≥ 2 s. Mention "free help, no obligation to buy".

## 10. Compliance (UK)
- "Dramatisation" label on AI or acted scenes. Testimonials genuine, consented, unedited in meaning.
- No "cheapest", "guaranteed", "best in UK", fake urgency. No finance offers without full APR wording.
- CarVendors finds and connects; B&F Cars Northampton (same group) sells. Never blur that line.

## 11. QA before showing anything
- [ ] Hook readable in the first frame at phone size, muted.
- [ ] Proof on screen by the target second. CTA on screen ≥ 2 s.
- [ ] No text in 0-150 px or 1540-1920 px; captions inside the band; no panel on a face.
- [ ] `npx hyperframes check` clean; midpoint snapshots of every scene looked at.
- [ ] -14 LUFS master; real review audio untouched apart from level.
