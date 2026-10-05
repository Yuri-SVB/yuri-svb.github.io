#!/usr/bin/env python3
"""Build 001's cover card: the gymnastics meme on the left, the caveat panel on
the right.

The meme itself is Yuri's. One word is repaired here rather than in the source
file: the original caption reads "buy a inheritance plan consultancy". The three
caption lines are re-set in Liberation Sans 14, which is metric-compatible with
the Arial the meme was made in, so the repair is invisible.

The right panel is the usual two-part card (see 004 and 005): title block on top,
accent rule, caveat block underneath. The caveat is not decoration. The meme's
own top row says "Buy Gold", and the post does not; standing rule 8 says the
card has to carry the qualification, because the card is what travels.
"""
from PIL import Image, ImageDraw, ImageFont

SRC = "../../../sandbox/bitcoin-gymnastic-meme.jpg"
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

LS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

f = ImageFont.truetype


def fix_caption(meme):
    """Re-set the three caption lines, with the article corrected."""
    d = ImageDraw.Draw(meme)
    d.rectangle([0, 213, meme.width - 1, 269], fill=(255, 255, 255))
    lines = [
        "Roll 666 dice, follow weekly hack news, take a cyber security course,",
        "install TailsOS, multi-sig, multi-vendor, multi-location setup, train your family,",
        "buy an inheritance plan consultancy, keep profile low, don't tell anyone about Bitcoin",
    ]
    font = f(LS, 14)
    for line, baseline in zip(lines, (228, 245, 262)):
        d.text((meme.width / 2, baseline), line, font=font, fill=(0, 0, 0), anchor="ms")
    return meme


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

    meme = fix_caption(Image.open(SRC).convert("RGB"))
    scale = IMG_W / meme.width
    meme = meme.resize((IMG_W, round(meme.height * scale)), Image.LANCZOS)
    left = Image.new("RGB", (IMG_W, H), (255, 255, 255))
    left.paste(meme, (0, (H - meme.height) // 2))
    card.paste(left, (0, 0))

    d = ImageDraw.Draw(card)
    x = IMG_W + PAD
    tw = W - x - PAD

    kicker = f(SANS_B, 15)
    d.text((x, 62), "T H E   C A R R Y I N G   C O S T", font=kicker, fill=MUTED)

    title = f(SERIF_B, 54)
    d.text((x, 96), "Gold With", font=title, fill=TITLE)
    d.text((x, 152), "Extra Steps", font=title, fill=TITLE)

    sub = f(SERIF, 26)
    d.text((x, 222), "what magic internet money turned into", font=sub, fill=SUB)

    body = f(SANS, 19)
    y = 282
    para = ("Self-custody as it is practiced now costs roughly what a vault "
            "costs. About 0.55% a year, on the most conservative parameters "
            "anyone uses. Nobody sends you that invoice, which is the only "
            "reason it does not feel like a fee.")
    for line in wrap(d, para, body, tw):
        d.text((x, y), line, font=body, fill=BODY)
        y += 28

    d.line([(x, 500), (W - PAD, 500)], fill=ACCENT, width=2)

    lab = f(SANS_B, 15)
    d.text((x, 524), "ON ONE AXIS ONLY", font=lab, fill=ACCENT)

    cav = f(SANS, 17)
    y = 552
    note = ("The comparison is what it costs to keep the thing safe, and "
            "nothing else. It is not a claim that metal is good money. The rate "
            "comes from a registry built out of press reports, so it is a floor.")
    for line in wrap(d, note, cav, tw):
        d.text((x, y), line, font=cav, fill=BODY)
        y += 24

    card.save(OUT + ".webp", quality=88, method=6)
    card.save(OUT + ".jpg", quality=88, subsampling=0, optimize=True)
    print("wrote", OUT + ".webp", OUT + ".jpg")


if __name__ == "__main__":
    main()
