#!/usr/bin/env python3
"""Build the cover for every edition. Title face: Nosifer (Typomondo), SIL OFL 1.1.

The font is read back out of the English cover SVG, where it is embedded, so
this script needs nothing outside this directory.
"""
import re
from xml.sax.saxutils import escape

FONT = re.search(r"base64,([A-Za-z0-9+/=]+)\)", open("cover-1200x675.svg").read()).group(1)
SANS = "font-family=\"'Helvetica Neue',Helvetica,Arial,sans-serif\""
EDITIONS = {  # suffix: (title lines, title size, subtitle lines)
    "":       (["BLOODSHED"], 118, ["What the maximalist future looks like,",
                                    "extrapolating today's wrench-attack stats"]),
    "-pt-BR": (["BANHO", "DE SANGUE"], 108, ["Como fica o futuro maximalista, extrapolando",
                                                   "as estatísticas de wrench attack de hoje"]),
    "-es":    (["DERRAMAMIENTO", "DE SANGRE"], 82, ["Cómo se ve el futuro maximalista si extrapolas",
                                                  "las estadísticas de wrench attacks de hoy"]),
    "-fr":    (["BAIN DE SANG"], 96, ["À quoi ressemble l'avenir maximaliste, en extrapolant",
                                      "les statistiques actuelles des attaques à la clé à molette"]),
    "-it":    (["SPARGIMENTO", "DI SANGUE"], 90, ["Com'è il futuro massimalista, estrapolando",
                                                 "le statistiche di oggi sui wrench attack"]),
}
for suf, (title, size, sub) in EDITIONS.items():
    if len(title) == 1:
        ty, sy = [330], 455
    else:
        ty, sy = [265, 265 + int(size * 1.35)], 265 + int(size * 1.35) + 120
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">',
         "<!-- Title face: Nosifer, Copyright (c) 2011 Typomondo. SIL Open Font License 1.1, embedded for rendering. -->",
         f"<style>@font-face{{font-family:'Nosifer';src:url(data:font/woff2;base64,{FONT}) format('woff2');}}</style>",
         '<rect width="100%" height="100%" fill="#fcfcfb"/>']
    for line, y in zip(title, ty):
        o.append(f'<text x="600" y="{y}" font-family="Nosifer" font-size="{size}" fill="#9e0b0f" text-anchor="middle">{escape(line)}</text>')
    for i, line in enumerate(sub):
        o.append(f'<text x="600" y="{sy + i * 42}" {SANS} font-size="32" fill="#0b0b0b" text-anchor="middle">{escape(line)}</text>')
    o.append("</svg>")
    open(f"cover-1200x675{suf}.svg", "w").write("\n".join(o) + "\n")
