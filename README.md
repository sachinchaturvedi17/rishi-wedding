# Rajendra weds Chanda: wedding invitation

A single-page, mobile-first digital invitation (Rajputana style).

## Run it
Double-click `index.html`. It opens in your browser and the music plays, as long as the `assets` folder
stays next to it. To deploy, upload the whole folder (Vercel, Netlify, GitHub Pages: drag the folder in).

## What is inside
- `index.html`: the finished invitation. All artwork (palace skyline, peacocks, elephant, arches, icons)
  is inline SVG.
- `assets/music.mp3`: the background song (loops, controlled by the music button).
- `rsvp-config.js`: one line to paste your RSVP counter link into (see "RSVP counting" below).
- `rsvp-backend/Code.gs`: the small script that saves the Yes / No answers in a Google Sheet.
- `vercel.json`: optional, for Vercel.
- `source/template.html` + `source/build.py`: editable source. Run `python3 source/build.py` to regenerate
  `index.html` after editing the template (Python 3, no packages needed).

## RSVP counting (5 minutes, free)
Just before the closing "Padharo Sa" card, guests see "So, are you coming?" with **Yes** and **No**.
Every Yes is counted and the total is shown to guests ("12 guests are coming"). Each phone counts once:
tapping again, or changing Yes to No, updates that guest's answer instead of adding a new one.

A web page cannot keep a shared count by itself, so the answers go into a Google Sheet that you own:
1. Create a new Google Sheet (name it e.g. "Wedding RSVP").
2. Open **Extensions > Apps Script**, delete the sample code, paste everything from `rsvp-backend/Code.gs`, click Save.
3. Click **Deploy > New deployment**, choose type **Web app**. Set **Execute as: Me** and **Who has access: Anyone**.
   Click Deploy and approve the permission prompt (Advanced > Go to project, if Google warns).
4. Copy the **Web app URL** (ends in `/exec`).
5. Open `rsvp-config.js`, paste it between the quotes after `endpoint:`, save, and upload the folder again.

The sheet gets an `RSVP` tab: one row per guest device, with live totals in cells G2 (Yes) and G3 (No).
If you change `Code.gs` later, use Deploy > Manage deployments > Edit > New version so the URL stays the same.

Until a URL is pasted, the buttons still work in preview mode (answer saved on that phone only, with a small
"Preview mode" note under the buttons), so you can try the design before setting up the sheet.

Good to know: a guest who opens the link in a different browser (for example WhatsApp's built-in browser and
then Chrome) can count twice, because each browser is a separate "device". The sheet shows no names, only the
Yes / No totals.

## Needs the internet
Only for the fonts (Rozha One, Alegreya, Tiro Devanagari Hindi from Google Fonts). Offline, the page and
music still work but text falls back to a system serif font.

## Change the song
Replace `assets/music.mp3` with another MP3 of the same name. Keep it under about 5 MB so it loads fast
on phones. Use music you have the right to use.

## Other things you may want to edit (all in `source/template.html`)
- Names, dates, times, family names: search for the text and change it.
- Countdown target: `TARGET` and `END` in the script (IST, +05:30).
- Map link: the `View Location` button in the `#baraat` section.
- Calendar text: `cal_text` in `source/build.py`.
- RSVP wording (question, Yes / No labels, thank-you lines): the `#rsvp` section and the RSVP block in the script.
