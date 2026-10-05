#!/usr/bin/env python3
"""Build m2-kidnapping-ladder.svg. Inputs pinned here; sources in SOURCE.md."""
TOTAL = 26.22e9            # ADAN/Deloitte/Ipsos 2025, upper bound of French holdings
YEARS = 20 / 12            # Jan 2025 - Aug 2026
HOLDERS_2026, CASES_2026 = 5.9e6, 105   # ADAN 2026 (11%); PNACO >70 in 8 months, annualised
STATED = [1e6, 2e6, 8e6, 9e5, 7e5, 6.8e4]  # household holdings stated in press, French cases
NIGERIA, HAITI = 3.4, 5.5
FR_MILLIONAIRE_SHARE = 2.388e6 / 57.5e6   # UBS Global Wealth Report 2026
CRYPTO_MILLIONAIRES = 241700              # Henley Crypto Wealth Report 2025
EST_1M = sum(v >= 1e6 for v in STATED) / YEARS / (FR_MILLIONAIRE_SHARE * CRYPTO_MILLIONAIRES) * 1e5
rungs = [("All holders", CASES_2026 / HOLDERS_2026 * 1e5, None)]
for th, lab in [(2.5e5, "€250k+"), (5e5, "€500k+"), (1e6, "€1M+"), (2e6, "€2M+"), (5e6, "€5M+")]:
    n = sum(v >= th for v in STATED)
    rungs.append((lab, n / YEARS / (TOTAL / th) * 1e5, n))

W, H = 1200, 850
X0, X1, YB, YT, YMAX = 150, 1120, 610, 215, 20.0
y = lambda v: YB - (YB - YT) * v / YMAX
F = "font-family=\"'Helvetica Neue',Helvetica,Arial,sans-serif\""
INK, INK2, MUTE, ACC, SURF = "#0b0b0b", "#52514e", "#8a8781", "#eb6834", "#fcfcfb"
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="100%" height="100%" fill="{SURF}"/>',
     f'<text x="80" y="70" {F} font-size="22" letter-spacing="4" fill="{MUTE}">KIDNAPPED, BY WHAT YOU HOLD</text>',
     f'<text x="80" y="118" font-family="Georgia,\'Times New Roman\',serif" font-size="34" fill="{INK}">French crypto holders, kidnappings per 100,000 a year, at least</text>']
for v in range(0, 21, 4):
    o.append(f'<line x1="{X0}" y1="{y(v):.1f}" x2="{X1}" y2="{y(v):.1f}" stroke="#e6e3dc" stroke-width="1"/>')
    o.append(f'<text x="{X0-14}" y="{y(v)+7:.1f}" {F} font-size="20" fill="{MUTE}" text-anchor="end">{v}</text>')
for val, lab in [(HAITI, "Haiti 5.5"), (NIGERIA, "Nigeria 3.4")]:
    o.append(f'<line x1="{X0}" y1="{y(val):.1f}" x2="{X1}" y2="{y(val):.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="10 6"/>')
    o.append(f'<text x="{X0+14}" y="{y(val)-10:.1f}" {F} font-size="20" font-weight="bold" fill="{INK}">{lab}</text>')
BW, step = 110, (X1 - X0) / len(rungs)
for i, (lab, v, n) in enumerate(rungs):
    x = X0 + step * (i + 0.5); l = x - BW / 2
    fill = MUTE if n is None else ACC
    if lab == "€1M+":   # realistic estimate, drawn as a dashed extension above the floor
        o.append(f'<rect x="{l+1.5}" y="{y(EST_1M):.1f}" width="{BW-3}" height="{y(v)-y(EST_1M)-2:.1f}" fill="{ACC}" fill-opacity="0.12" stroke="{ACC}" stroke-width="3" stroke-dasharray="9 6"/>')
        o.append(f'<text x="{x}" y="{y(EST_1M)-14:.1f}" {F} font-size="24" font-weight="bold" fill="{INK}" text-anchor="middle">~{EST_1M:.0f}</text>')
        o.append(f'<text x="{x}" y="{y(EST_1M)-42:.1f}" {F} font-size="17" fill="{INK2}" text-anchor="middle">estimate</text>')
    o.append(f'<rect x="{l}" y="{y(v):.1f}" width="{BW}" height="{YB-y(v):.1f}" fill="{fill}"/>')
    ty = y(v) - 14
    if lab == "€1M+" or any(abs(ty - 8 - y(r)) < 22 for r in (NIGERIA, HAITI)):   # label would sit on a reference line
        o.append(f'<text x="{x}" y="{y(v)+30:.1f}" {F} font-size="24" font-weight="bold" fill="{SURF}" text-anchor="middle">{v:.1f}</text>')
    else:
        o.append(f'<text x="{x}" y="{ty:.1f}" {F} font-size="24" font-weight="bold" fill="{INK}" text-anchor="middle">{v:.1f}</text>')
    o.append(f'<text x="{x}" y="{YB+34}" {F} font-size="21" fill="{INK}" text-anchor="middle">{lab}</text>')
    sub = "~5.9M people" if n is None else f"{n} case{'s' if n != 1 else ''}"
    o.append(f'<text x="{x}" y="{YB+60}" {F} font-size="18" fill="{MUTE}" text-anchor="middle">{sub}</text>')
o.append(f'<line x1="{X0}" y1="{YB}" x2="{X1}" y2="{YB}" stroke="{INK}" stroke-width="2"/>')
o.append(f'<text x="80" y="156" {F} font-size="19" fill="{INK2}">By crypto held. Floors: only cases where the press reported what the household held,</text>')
o.append(f'<text x="80" y="180" {F} font-size="19" fill="{INK2}">over the most people France could possibly have in each bracket.</text>')
cap = ["All holders: prosecutor's count (PNACO), 2026 pace, over ~5.9M holders. Brackets: French cases Jan 2025–Aug 2026 with the",
       "household's holding reported (stolen, transferred, or \"millionaire\"), annualised, over the ceiling the survey total allows",
       "(€26.2bn ÷ bracket). Most victims' holdings are never reported, so every bar is an undercount; the top bars rest on 1–2 cases.",
       "Dashed lines: Nigeria, 2025–26 (SBM Intelligence press count); Haiti, 2025 (BINUH, UN). Both reported counts, both minimums.",
       "Dashed box, €1M+: estimate if France has its ordinary share (4.2%, UBS) of the world's ~242,000 crypto millionaires (Henley)."]
for i, t in enumerate(cap):
    o.append(f'<text x="80" y="{H-145+i*27}" {F} font-size="18" fill="{INK2}">{t}</text>')
o.append('</svg>')
open("m2-kidnapping-ladder.svg", "w").write("\n".join(o) + "\n")
for lab, v, n in rungs: print(f"{lab:12} {v:5.1f}  n={n}")
