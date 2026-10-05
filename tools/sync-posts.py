#!/usr/bin/env python3
"""Render the posts from great-wall-posts into this site.

The posts repository owns the words. This script owns nothing: it reads that
repository and writes posts/ here, so the site is a rendering of the source and
never a second copy of it. Run it again after any post changes; it overwrites.

    pip install markdown
    ./tools/sync-posts.py [--posts ../great-wall-posts] [--check]

--check writes nothing and exits non-zero if the output would differ, which is
what you want before publishing.
"""

import argparse
import html
import json
import pathlib
import re
import shutil
import sys

try:
    import markdown
except ImportError:
    sys.exit("sync-posts: needs python-markdown — pip install markdown")

LANG_NAMES = {
    "en": "English", "pt-BR": "Português", "es": "Español",
    "fr": "Français", "it": "Italiano", "sv": "Svenska",
}
# Language files only. BRIEF.md is private drafting notes and must never render;
# *.publicar.md is a publisher handoff, not an edition.
LANG_RE = re.compile(r"^(" + "|".join(re.escape(k) for k in LANG_NAMES) + r")\.md$")

ROOT = pathlib.Path(__file__).resolve().parent.parent


def page(title, description, body, depth, lang="en", extra_head=""):
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
{extra_head}</head>
<body>
<div class="wrap">
{body}
</div>
</body>
</html>
"""


FRONT_MATTER = re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.S)


def strip_front_matter(md_text):
    """Drop the YAML block entirely.

    The posts repo writes editorial state and the SEO handoff into every
    language file's front matter, and none of it is the reader's: `estado`,
    every `seo_*` key, and a `veículo`/`data_publicação` that is still null.
    `build-public.py` strips those on the way to the mirror; this script renders
    the same files and has to do the same.

    It strips the WHOLE block rather than the private keys, which is the
    allowlist and not a denylist: a field reaches the page only because the
    renderer went and asked for it by name. A new private key added upstream
    cannot leak here by default, which is the one property that matters.
    """
    return FRONT_MATTER.sub("", md_text, count=1).lstrip()


def first_heading(md_text):
    m = re.search(r"^#\s+(.+?)\s*$", strip_front_matter(md_text), re.M)
    return m.group(1) if m else "Untitled"


def first_paragraph(md_text):
    body = re.sub(r"^#\s+.+?$", "", strip_front_matter(md_text), count=1, flags=re.M)
    for chunk in re.split(r"\n\s*\n", body):
        chunk = chunk.strip()
        if chunk and not chunk.startswith(("#", "<", "!", "|", ">")):
            return re.sub(r"\s+", " ", re.sub(r"[*_`\[\]]|\(http[^)]*\)", "", chunk))
    return ""


def render_post(md_text, slug, lang, title, date, langs):
    body_md = re.sub(r"^#\s+.+?$", "", strip_front_matter(md_text),
                     count=1, flags=re.M).lstrip()
    body = markdown.markdown(body_md, extensions=["extra", "sane_lists"])

    switch = " · ".join(
        LANG_NAMES[l] if l == lang
        else f'<a href="{"index" if l == "en" else l}.html">{LANG_NAMES[l]}</a>'
        for l in langs
    )
    head = f"""<header class="top">
  <img class="mark" src="../../assets/mark.png" alt="">
  <h1>{html.escape(title)}</h1>
  <p class="role"><time datetime="{date}">{date}</time></p>
  <nav class="lang"><a href="../">All posts</a> · {switch}</nav>
</header>

<hr>
"""
    foot = """
<footer>
  <p>Free to read, translate and republish. Every figure comes from a
  press-sourced registry with survivorship bias, coded by headline rather than
  measured; shares overlap and the fatality share is a floor. A number without
  its caveat is a bug.</p>
  <p>The arguments are developed in
  <a href="https://zenodo.org/doi/10.5281/zenodo.22018891"><em>The Deadly Race</em></a> and
  <a href="https://zenodo.org/doi/10.5281/zenodo.22778480"><em>The Denial Spiral</em></a>,
  both open access. Source for this post:
  <a href="https://github.com/Yuri-SVB/great-wall-posts/tree/main/posts/%s">great-wall-posts</a>.</p>
  <p><a href="../../audit/">Self-custody audit</a> ·
     <a href="../../course/">The course</a> ·
     <a href="../../">Home</a></p>
</footer>
""" % slug
    return head + "\n<article>\n" + body + "\n</article>\n" + foot


def build(posts_repo, out_dir):
    feed_path = posts_repo / "posts" / "feed.json"
    if not feed_path.exists():
        sys.exit(f"sync-posts: no {feed_path} — is --posts pointing at great-wall-posts?")
    feed = json.loads(feed_path.read_text(encoding="utf-8"))["posts"]
    feed.sort(key=lambda p: p["date"], reverse=True)

    written = {}
    cards = []

    for post in feed:
        src = posts_repo / "posts" / post["slug"]
        if not src.is_dir():
            print(f"  ! {post['slug']}: not in the posts repo, skipped")
            continue
        dst = out_dir / post["slug"]

        langs = [l for l in post["languages"] if LANG_RE.match(f"{l}.md")
                 and (src / f"{l}.md").exists()]
        if not langs:
            print(f"  ! {post['slug']}: no language files, skipped")
            continue
        if "en" in langs:                      # English first, then as listed
            langs = ["en"] + [l for l in langs if l != "en"]

        titles = {}
        for lang in langs:
            md_text = (src / f"{lang}.md").read_text(encoding="utf-8")
            titles[lang] = first_heading(md_text)
            summary = post.get("summary", {}).get(lang) or first_paragraph(md_text)
            name = "index.html" if lang == "en" else f"{lang}.html"
            written[dst / name] = page(
                titles[lang], summary[:300],
                render_post(md_text, post["slug"], lang, titles[lang], post["date"], langs),
                depth=2, lang=lang,
            )

        assets = src / "assets"
        if assets.is_dir():
            for f in sorted(assets.iterdir()):
                # SOURCE.md in an assets directory is private drafting material.
                if f.is_file() and f.name != "SOURCE.md":
                    written[dst / "assets" / f.name] = f.read_bytes()

        lang_links = " · ".join(
            f'<a href="{post["slug"]}/{"index" if l == "en" else l}.html">{LANG_NAMES[l]}</a>'
            for l in langs
        )
        head_lang = "en" if "en" in langs else langs[0]
        blurb = post.get("summary", {}).get(head_lang) or first_paragraph(
            (src / f"{head_lang}.md").read_text(encoding="utf-8"))
        cards.append(f"""<div class="entry">
  <span class="title"><a href="{post['slug']}/">{html.escape(titles[head_lang])}</a></span>
  <span class="doi"><time datetime="{post['date']}">{post['date']}</time></span>
  {html.escape(blurb)}
  <p class="small">{lang_links}</p>
</div>""")

    index_body = """<header class="top">
  <img class="mark" src="../assets/mark.png" alt="">
  <h1>Posts</h1>
  <nav class="lang"><a href="../">Home</a></nav>
</header>

<hr>

<p class="lede">Writing on coercion-resistant Bitcoin self-custody, and on why
the community's standing advice makes the problem worse.</p>

<p>Free to read, translate and republish. The papers behind it are open access,
the incident data goes upstream to
<a href="https://github.com/jlopp/physical-bitcoin-attacks">Jameson Lopp's
registry</a>, and the analysis scripts are public. Nothing is gated.</p>

<h2>The feed</h2>

""" + ("\n\n".join(cards) if cards else "<p class=\"muted\">Nothing published yet.</p>") + """

<footer>
  <p>Every figure comes from a press-sourced registry with survivorship bias,
  coded by headline rather than measured. Shares overlap. The fatality share is
  a floor, not an estimate. A number without its caveat attached is a bug —
  <a href="https://github.com/Yuri-SVB/great-wall-posts/issues">open an issue</a>.</p>
  <p>Source: <a href="https://github.com/Yuri-SVB/great-wall-posts">great-wall-posts</a></p>
</footer>
"""
    written[out_dir / "index.html"] = page(
        "Posts — Yuri da Silva Villas Boas",
        "Writing on coercion-resistant Bitcoin self-custody, and on why the "
        "community's standing advice makes the problem worse.",
        index_body, depth=1)
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts", default="../great-wall-posts")
    ap.add_argument("--check", action="store_true",
                    help="write nothing; exit 1 if the output would differ")
    args = ap.parse_args()

    posts_repo = pathlib.Path(args.posts).expanduser().resolve()
    out_dir = ROOT / "posts"
    print(f"sync-posts: from {posts_repo}")

    written = build(posts_repo, out_dir)

    stale = []
    if out_dir.exists():
        for existing in out_dir.rglob("*"):
            if existing.is_file() and existing not in written:
                stale.append(existing)

    changed = [p for p, c in written.items()
               if not p.exists()
               or (p.read_bytes() if isinstance(c, bytes) else p.read_text(encoding="utf-8")) != c]

    if args.check:
        for p in changed:
            print(f"  would change {p.relative_to(ROOT)}")
        for p in stale:
            print(f"  would remove {p.relative_to(ROOT)}")
        if changed or stale:
            sys.exit(f"sync-posts: {len(changed)} to write, {len(stale)} stale — out of date")
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
