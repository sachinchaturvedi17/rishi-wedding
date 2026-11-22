# Rajendra weds Chanda: wedding invitation

A single-page, mobile-first digital invitation (Rajputana style).

## Run it
Double-click `index.html`. It opens in your browser and the music plays, as long as the `assets` folder
stays next to it. To deploy, upload the whole folder (Vercel, Netlify, GitHub Pages: drag the folder in).

## What is inside
- `index.html`: the finished invitation. All artwork (palace skyline, peacocks, elephant, arches, icons)
  is inline SVG.
- `assets/music.mp3`: the background song (loops, controlled by the music button).
- `vercel.json`: optional, for Vercel.
- `source/template.html` + `source/build.py`: editable source. Run `python3 source/build.py` to regenerate
  `index.html` after editing the template (Python 3, no packages needed).

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
