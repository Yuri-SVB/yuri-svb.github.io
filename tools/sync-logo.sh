#!/bin/sh
# Re-copy the artwork from the logo repository, which owns the master.
# Reports what changed instead of overwriting in silence.
set -eu

LOGO=${LOGO:-../great-wall-logo}
[ -d "$LOGO/web" ] || { echo "sync-logo: no logo repo at $LOGO (set LOGO=)" >&2; exit 1; }

sync() {   # <source> <dest> <max-edge>
  python3 - "$1" "$2" "$3" <<'PY'
import sys, os
from PIL import Image
src, dst, edge = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = Image.open(src); im.thumbnail((edge, edge), Image.LANCZOS)
before = open(dst, 'rb').read() if os.path.exists(dst) else None
im.save(dst, optimize=True)
after = open(dst, 'rb').read()
print(f"  {dst}: {'unchanged' if before == after else 'UPDATED'} at {im.size[0]}x{im.size[1]}")
PY
}

echo "sync-logo: from $LOGO"
sync "$LOGO/web/lockup-1200.png" assets/great-wall.png 560
sync "$LOGO/web/mark-512.png"    assets/mark.png       180
cp "$LOGO/web/favicon.ico" favicon.ico
echo "  favicon.ico: copied"
