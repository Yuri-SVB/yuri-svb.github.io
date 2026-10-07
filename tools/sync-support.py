#!/usr/bin/env python3
"""Render the Support and Delivered pages from the support repository.

Same contract as sync-posts.py, for the same reason. The support repository
owns the words; this script owns nothing. It reads `README.md` and
`DELIVERED.md` from there and writes support/ here, so the site is a rendering
of the source and never a second copy of it that can drift. Run it again after
either file changes; it overwrites.

    pip install markdown
    ./tools/sync-support.py [--support ../support] [--check]

--check writes nothing and exits non-zero if the output would differ, which is
what you want before publishing.

Two pages, and the source of each is named here and nowhere else:

    README.md     -> support/index.html
    DELIVERED.md  -> support/delivered/index.html

**That list is the allowlist, and it is the point.** A file in the support
repository renders because it is named above, not because it is a `.md` the
script happened to find. The same goes for the images: a file ships only if a
rendered page asks for it by name AND its extension is on IMAGE_SUFFIXES, so a
note dropped into `assets/` cannot reach the site by sitting next to a QR code.
A denylist fails open exactly once, and once is enough.

What this script does NOT do is edit the words. The links in `DELIVERED.md`
point where that file points them, `doi.org` entries and version DOIs included:
a version DOI is correct in a changelog entry about that version, so a blanket
rewrite to the concept DOI would corrupt the record it is there to keep. The
rewrites below are all layout — GitHub markup that has no meaning on a page
that is not GitHub.
"""

import argparse
import html
import pathlib
import re
import sys

try:
    import markdown
except ImportError:
    sys.exit("sync-support: needs python-markdown — pip install markdown")

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The allowlist. Nothing else in the support repository renders.
PAGES = [
    {
        "src": "README.md",
        "out": "index.html",
        "nav": "Support",
        "depth": 1,
        "description": "Support the work on coercion-resistant Bitcoin "
                       "self-custody: Lightning (BOLT12) and on-chain (silent "
                       "payment), no signup, nothing expected in return.",
    },
    {
        "src": "DELIVERED.md",
        "out": "delivered/index.html",
        "nav": "Delivered",
        "depth": 2,
        "description": "What has actually shipped on Great Wall, BIP-450, "
                       "BTC-D20 and the wrench-attack research, dated, newest "
                       "first.",
    },
]

# An image ships only if a rendered page references it. This bounds what the
# reference can be: a .md or .txt in assets/ never reaches the site, however it
# is linked.
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".ico"}

# Where the support repository's images land under this site's assets/.
ASSET_DIR = "assets/support/"
ASSET_REF = re.compile(
    r'(?:src|href)="(?:\.\./)*' + ASSET_DIR + r'([^"?#/]+)"')


def page(title, description, body, depth, lang="en"):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="icon" href="{up}favicon.ico">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<div class="wrap">
{body}
</div>
</body>
</html>
"""


MASTHEAD = re.compile(r'\A<p align="center">.*?^---\s*$\n', re.S | re.M)


def drop_masthead(md_text):
    """Remove the GitHub masthead: portrait, name, role, social row, rule.

    It is there because a README has no page furniture of its own. This site
    does, so rendering it would put the name and the social row on the page
    twice. Only a file that opens on that centred block is touched.
    """
    return MASTHEAD.sub("", md_text, count=1).lstrip()


H1 = re.compile(r"^#\s+(.+?)\s*$", re.M)
LEADING_EMOJI = re.compile(r"\A[^\w(\[]+\s*")


def split_title(md_text):
    """Return (heading text, body with that heading removed).

    The emoji is kept in the body, where the source put it, and dropped from
    the masthead and the <title>: a browser tab and a search result are the two
    places on this site where no other heading carries one.
    """
    m = H1.search(md_text)
    if not m:
        sys.exit("sync-support: no '# ' heading — refusing to guess a title")
    title = LEADING_EMOJI.sub("", m.group(1)).strip()
    return title, (md_text[:m.start()] + md_text[m.end():]).lstrip()


def rewrite_github_markup(md_text, depth):
    """Turn GitHub-only markup into something a page can use.

    Every rewrite here is layout, not words:

    * `?raw=true` is how a README forces GitHub to serve the file instead of
      its blob viewer. On a static site it is a query string on a path.
    * `align="left"` floats the QR code beside the payment string. The column
      here is 40rem and the strings are 300-plus characters, so a float leaves
      the string in a 20-character gutter. The pair stacks instead.
    * `<br clear="all">` exists only to end that float.
    * `./DELIVERED.md` and `./README.md` are repository paths. On the site they
      are the two pages this script writes.
    * `<details>` needs `markdown="1"`, or python-markdown passes the block
      through verbatim and the reader gets literal asterisks.
    """
    up = "../" * (depth - 1)
    text = md_text.replace("?raw=true", "")
    text = re.sub(r'\s+align="(?:left|right)"', "", text)
    text = re.sub(r"<br\s+clear=\"all\"\s*>\s*(?:<br\s*/?>\s*)?", "", text)
    text = re.sub(r'<details(?![^>]*markdown=)', '<details markdown="1"', text)
    text = re.sub(r'\]\(\.?/?DELIVERED\.md\)', f']({up}delivered/)', text)
    text = re.sub(r'\]\(\.?/?README\.md\)', f']({up})', text)
    text = re.sub(r'(src|href)="assets/', rf'\1="{up}../' + ASSET_DIR, text)
    return text


LEDE = re.compile(r"\A\s*<p>", re.S)
# A dated entry in DELIVERED.md, and a project in README.md's "The work", is a
# bold title line and then a description, separated by a plain newline. GitHub
# renders that newline as a space, and so does this; on a 40rem column the
# title stops being an anchor and the log reads as one block of prose. The
# break is put back. It fires only where the source itself broke the line
# straight after the bold run, so a mid-sentence `**...**` is untouched.
ENTRY_TITLE = re.compile(
    r"(<p>(?:<em>)?<strong>[^\n]*?</strong>(?:</em>)?)\n(?=\S)")


def render(md_text, spec):
    md_text = rewrite_github_markup(drop_masthead(md_text), spec["depth"])
    title, body_md = split_title(md_text)
    body = markdown.markdown(
        body_md, extensions=["extra", "sane_lists", "md_in_html"])
    # The source opens on its own summary line. Promote that rather than write
    # a second one into the masthead, which is how the two came to say the same
    # thing twice.
    body = LEDE.sub('<p class="lede">', body, count=1)
    body = ENTRY_TITLE.sub(r"\1<br>\n", body)

    up = "../" * spec["depth"]
    # The other pages in PAGES, addressed from this one. Adding a third page
    # to the allowlist puts it in both navs without touching anything here.
    siblings = "".join(
        f'\n    <a href="{up}support/{o["out"][:-len("index.html")]}">{o["nav"]}</a> ·'
        for o in PAGES if o is not spec)
    head = f"""<header class="top">
  <img class="mark" src="{up}assets/mark.png" alt="">
  <h1>{html.escape(title)}</h1>
  <nav class="lang"><a href="{up}">Home</a> ·{siblings}
    <a href="{up}posts/">Posts</a></nav>
</header>

<hr>
"""
    foot = f"""
<footer>
  <p><a href="{up}posts/">Posts</a> ·
     <a href="{up}audit/">Self-custody audit</a> ·
     <a href="{up}course/">The course</a> ·
     <a href="{up}">Home</a></p>
  <p>Contact: <a href="mailto:yuri@t3infosecurity.com">yuri@t3infosecurity.com</a></p>
  <p>This page is rendered from
     <a href="https://github.com/Yuri-SVB/support/blob/main/{spec["src"]}"><code>{spec["src"]}</code></a>
     in <a href="https://github.com/Yuri-SVB/support">Yuri-SVB/support</a>, which
     is where the dates and the git history live.</p>
</footer>
"""
    return head + "\n<article>\n" + body + "\n</article>\n" + foot


def build(support_repo, out_dir, assets_out):
    written = {}
    wanted = set()

    for spec in PAGES:
        src = support_repo / spec["src"]
        if not src.is_file():
            sys.exit(f"sync-support: no {src} — is --support pointing at the "
                     f"support repository?")
        body = render(src.read_text(encoding="utf-8"), spec)
        title = html.unescape(re.search(r"<h1>(.*?)</h1>", body).group(1))
        rendered = page(f"{title} — Yuri da Silva Villas Boas",
                        spec["description"], body, depth=spec["depth"])
        written[out_dir / spec["out"]] = rendered
        wanted.update(m.group(1) for m in ASSET_REF.finditer(rendered))

    # An image ships because a page asked for it by name, and only then.
    src_assets = support_repo / "assets"
    for name in sorted(wanted):
        f = src_assets / name
        if pathlib.Path(name).suffix.lower() not in IMAGE_SUFFIXES:
            sys.exit(f"sync-support: {name} is referenced but is not an image "
                     f"— refusing to ship it")
        if not f.is_file():
            sys.exit(f"sync-support: {name} is referenced by a page and is not "
                     f"in {src_assets}")
        written[assets_out / name] = f.read_bytes()

    if src_assets.is_dir():
        for f in sorted(src_assets.iterdir()):
            if f.is_file() and f.name not in wanted:
                print(f"  . {f.name}: nothing references it, not shipped")

    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--support", default="../support")
    ap.add_argument("--check", action="store_true",
                    help="write nothing; exit 1 if the output would differ")
    args = ap.parse_args()

    support_repo = pathlib.Path(args.support).expanduser().resolve()
    out_dir = ROOT / "support"
    assets_out = ROOT / "assets" / "support"
    print(f"sync-support: from {support_repo}")

    written = build(support_repo, out_dir, assets_out)

    stale = []
    for d in (out_dir, assets_out):
        if d.exists():
            for existing in d.rglob("*"):
                if existing.is_file() and existing not in written:
                    stale.append(existing)

    changed = [p for p, c in written.items()
               if not p.exists()
               or (p.read_bytes() if isinstance(c, bytes)
                   else p.read_text(encoding="utf-8")) != c]

    if args.check:
        for p in changed:
            print(f"  would change {p.relative_to(ROOT)}")
        for p in stale:
            print(f"  would remove {p.relative_to(ROOT)}")
        if changed or stale:
            sys.exit(f"sync-support: {len(changed)} to write, "
                     f"{len(stale)} stale — out of date")
        print("  up to date")
        return

    for p in stale:
        p.unlink()
        print(f"  removed {p.relative_to(ROOT)}")
    for p, content in written.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(content, encoding="utf-8")
    print(f"  wrote {len(written)} file(s), {len(changed)} changed")


if __name__ == "__main__":
    main()
