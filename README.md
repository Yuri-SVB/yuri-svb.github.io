# yuri-svb.github.io

The personal site. Plain static HTML, no build step, no JavaScript, no
dependencies. GitHub Pages serves this repository's default branch as-is.

## ⛔ This is the private draft

The public repository is `Yuri-SVB/yuri-svb.github.io`. This one is
`yurisvb-pdgh/PRIV-DRAFT-yuri-svb.github.io`, and it may carry notes that are
not meant to ship. Push an explicit list of paths to the public repo rather than
excluding files from it.

## Layout

```
index.html            profile and front door (en)
audit/index.html      the four questions, full version (en)
consultoria/index.html  same, pt-BR
assets/style.css      one stylesheet, light and dark
assets/great-wall.png the lockup, 560px
assets/mark.png       the dragon alone, 180px
favicon.ico
.nojekyll             serve files verbatim, no Jekyll pass
tools/sync-logo.sh    re-copy the artwork from the logo repository
```

`.nojekyll` matters. Without it Pages runs the whole tree through Jekyll, which
ignores directories beginning with an underscore and can rewrite things
unasked.

## Canonical URL

**`https://yuri-svb.github.io` is canonical, for now.**

Setting a custom domain on a Pages site makes `yuri-svb.github.io` issue a 301
to that domain — the redirect runs that way round, and it cannot be reversed.
So the choice is between:

| Canonical | How | Cost |
|---|---|---|
| `yuri-svb.github.io` | do nothing | no DNS at all |
| `t3infosecurity.com` | set it as the Pages custom domain | needs DNS access |

Today the second is blocked: `t3infosecurity.com` is registered through PDR Ltd
behind a reseller, sits on `clientTransferProhibited`, and its nameservers are
`borovoi`/`satyr.armata.cloud`. Nothing changes until one of those panels opens.

Switching later is cheap and lossless. Set the custom domain and every existing
`github.io` link keeps working through the automatic 301.

**One thing not to do in the meantime.** Don't write `yuri-svb.github.io` into
anything that cannot be edited afterwards — Zenodo deposits, published articles,
OpenTimestamped bundles, PDFs in a release. Those depend on the redirect
surviving indefinitely, and a redirect can only be guaranteed on a namespace you
control. The `github.io` namespace is not one: rename or lose the account and
someone else can register `yuri-svb`. Immutable artifacts should carry DOIs and
repository links until the domain question is settled.

## Artwork

Comes from `priv-draft-great-wall-logo`, which owns the master and can rebuild
every derivative from it. Don't edit the PNGs here; run:

```sh
./tools/sync-logo.sh
```

It reports drift rather than silently overwriting.

## Contact

`yuri@t3infosecurity.com`. The domain's MX already points at Proton, so the
address receives independently of where the website is hosted.

Its outbound records need work before this address is used for cold outreach —
SPF omits `_spf.protonmail.ch` and hard-fails, DKIM is a single legacy inline
TXT rather than Proton's three CNAMEs, and SPF still authorises
`satyr.armata.cloud`, which is being decommissioned. Diagnosis and replacement
records are in `great-wall-posts/consultancy/contact/ALIASES.md`.

## Open

- Fee and turnaround are described as quoted-on-enquiry. Replace with real
  figures when they exist.
- No feed of Great Wall posts yet. The posts live in a separate repository and
  the public mirror is still unconfirmed, so there is nothing stable to link.
