# yuri-svb.github.io

Personal site of Yuri da Silva Villas Boas — applied cryptographer, author of
BIP-450 (Formosa) and of the Great Wall protocol.

Live at <https://yuri-svb.github.io>.

## What's here

| | |
|---|---|
| `index.html` | profile and front door |
| `audit/` | four questions about your self-custody arrangement (en) |
| `consultoria/` | the same, pt-BR |
| `assets/` | one stylesheet, the artwork |
| `tools/sync-logo.sh` | re-copies the artwork from the logo repository |

Plain static HTML. No build step, no JavaScript, no dependencies, no
third-party requests — the page you get is the file in this repository.
`.nojekyll` tells GitHub Pages to serve the tree verbatim rather than running
it through Jekyll.

## Editing

Change the HTML and push. There is nothing to compile.

The artwork is generated from a master held in the logo repository; don't edit
the PNGs here, run `./tools/sync-logo.sh` instead.

## Licence

Prose and artwork © Yuri da Silva Villas Boas. The markup and stylesheet are
MIT — take them if they're useful.
