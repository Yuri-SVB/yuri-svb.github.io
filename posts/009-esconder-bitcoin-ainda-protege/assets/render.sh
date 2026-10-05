#!/bin/sh
# Rasterise every .svg here to .png, and covers to .webp as well.
#
# Renders on a canvas TALLER than the artwork and crops back, because a
# headless Chromium screenshot at exactly the SVG's height silently clips
# the bottom of the page. That has eaten a caveat line twice.
set -eu

# Find a browser. $CHROME wins; otherwise the usual places, in order.
find_chrome() {
  [ -n "${CHROME:-}" ] && { printf '%s' "$CHROME"; return 0; }
  for c in /opt/pw-browsers/chromium-*/chrome-linux/chrome \
           /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell \
           "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux/chrome \
           "$HOME"/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium \
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; do
    [ -x "$c" ] && { printf '%s' "$c"; return 0; }
  done
  for n in chromium chromium-browser google-chrome google-chrome-stable; do
    p=$(command -v "$n" 2>/dev/null) && { printf '%s' "$p"; return 0; }
  done
  return 1
}

if [ -n "${CHROME:-}" ] && [ ! -x "$CHROME" ]; then
  echo "render.sh: CHROME=$CHROME is not an executable file." >&2
  exit 1
fi
CH=$(find_chrome) || {
  echo "render.sh: no Chromium found." >&2
  echo "  Set CHROME=/path/to/chrome, or install one. On this repo's remote" >&2
  echo "  sessions Playwright's build lives under /opt/pw-browsers/." >&2
  exit 1
}
echo "render.sh: using $CH"

LOG=$(mktemp); trap 'rm -f "$LOG" .render.html .raw.png' EXIT

for f in *.svg; do
  [ -e "$f" ] || { echo "render.sh: no .svg files in $PWD" >&2; exit 1; }
  b=${f%.svg}
  W=$(grep -o 'width="[0-9]*"' "$f" | head -1 | tr -dc 0-9)
  H=$(grep -o 'height="[0-9]*"' "$f" | head -1 | tr -dc 0-9)
  [ -n "$W" ] && [ -n "$H" ] || {
    echo "render.sh: $f has no integer width/height on its <svg> element." >&2
    exit 1
  }
  printf '<!doctype html><html><head><style>html,body{margin:0;padding:0}svg{display:block}</style></head><body>%s</body></html>' "$(cat "$f")" > .render.html
  rm -f .raw.png
  "$CH" --headless --disable-gpu --no-sandbox --hide-scrollbars \
        --force-device-scale-factor=1 --window-size="$W,$((H+225))" \
        --screenshot=.raw.png "file://$PWD/.render.html" >"$LOG" 2>&1 || true
  [ -s .raw.png ] || {
    echo "render.sh: Chromium wrote no screenshot for $f. Its output:" >&2
    tail -20 "$LOG" >&2
    exit 1
  }
  python3 -c "
from PIL import Image; import os
im = Image.open('.raw.png').convert('RGB').crop((0,0,$W,$H))
im.save('$b.png')
if '$b'.startswith('cover-'):
    im.save('$b.webp','WEBP',quality=92,method=6)
    print(f'$b  {im.size}  webp {os.path.getsize(\"$b.webp\")/1024:.0f} KB')
else:
    print(f'$b  {im.size}')"
done
