#!/usr/bin/env python3
"""Build 007's cover card: the Who-Killed-Hannibal meme on the left, the panel
on the right.

The meme is Yuri's edit of the format. The argument it makes is mechanism 1 of
the Denial Spiral, in one frame: the advice is to deny holding, and the thing
that advice destroys is the ownership data that would let anyone size the
wrench-attack problem or tell which fixes work.

The panel exists because of standing rule 8. The joke states flatly that
obscurity killed the statistics, and that is a structural claim nobody can
count, by the mechanism itself. Without the panel the card reads as an
empirical finding.
"""
from PIL import Image, ImageDraw, ImageFont

SRC = "../../../sandbox/who-killed-btc-stats.jpg"
OUT = "cover-1200x675"

W, H = 1200, 675
IMG_W = 675
PAD = 38

GROUND = (252, 252, 250)
TITLE = (11, 11, 11)
SUB = (82, 81, 78)
BODY = (63, 63, 61)
MUTED = (125, 124, 122)
ACCENT = (235, 104, 52)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

f = ImageFont.truetype


def wrap(draw, text, font, width):
    out, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def main():
    card = Image.new("RGB", (W, H), GROUND)

    meme = Image.open(SRC).convert("RGB")
    scale = H / meme.height
    meme = meme.resize((round(meme.width * scale), H), Image.LANCZOS)
    left = Image.new("RGB", (IMG_W, H), GROUND)
    left.paste(meme, ((IMG_W - meme.width) // 2, 0))
    card.paste(left, (0, 0))

    d = ImageDraw.Draw(card)
    x = IMG_W + PAD
    tw = W - x - PAD

    d.text((x, 62), "W H Y   T H E   C O U N T   C A N N O T   H E L P",
           font=f(SANS_B, 15), fill=MUTED)

    d.text((x, 96), "Anosognosia", font=f(SERIF_B, 54), fill=TITLE)

    d.text((x, 172), "not knowing that you don't know",
           font=f(SERIF, 26), fill=SUB)

    body = f(SANS, 19)
    y = 234
    para = ("Obscurity degrades how reliable and how informative Bitcoin "
            "ownership data is. Degrade that, and you lose the ability to "
            "identify the problems driving the wrench-attack crisis, let alone "
            "to fix them.")
    for line in wrap(d, para, body, tw):
        d.text((x, y), line, font=body, fill=BODY)
        y += 28

    d.line([(x, 470), (W - PAD, 470)], fill=ACCENT, width=2)

    d.text((x, 494), "NOT A MEASUREMENT", font=f(SANS_B, 15), fill=ACCENT)

    cav = f(SANS, 17)
    y = 522
    note = ("The first of the Denial Spiral's four censoring mechanisms, and a "
            "structural claim rather than a counted one. A practice that works "
            "by not being visible leaves no record of working or of failing, "
            "which is the whole difficulty.")
    for line in wrap(d, note, cav, tw):
        d.text((x, y), line, font=cav, fill=BODY)
        y += 24

    card.save(OUT + ".webp", quality=88, method=6)
    card.save(OUT + ".jpg", quality=88, subsampling=0, optimize=True)
    print("wrote", OUT + ".webp", OUT + ".jpg")


if __name__ == "__main__":
    main()
