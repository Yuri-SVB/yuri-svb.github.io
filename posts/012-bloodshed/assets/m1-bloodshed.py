#!/usr/bin/env python3
"""Build m1-bloodshed.svg. Every input is pinned here; sources in SOURCE.md."""
RATE, LO, HI = 0.046, 0.028, 0.073   # audited registry death share 16/351, and its 95% interval
UKR_WAR, UKR_POP = 2514, (33e6, 38e6)  # HRMMU, civilians killed in 2025
C = [  # name, residential burglaries (police-recorded), population, share with someone home
    ("England & Wales", 166577, 61.8e6, 0.50),   # ONS: "over half" (CSEW)
    ("United States",   405776, 340e6,  0.28),   # BJS/NCVS 2003-07
]
war = sorted(UKR_WAR / p * 1e5 for p in UKR_POP)   # 6.6, 7.6

W, H = 1200, 800
X0, X1, YB, YT, YMAX = 150, 1120, 600, 200, 11.0
y = lambda v: YB - (YB - YT) * v / YMAX
F = "font-family=\"'Helvetica Neue',Helvetica,Arial,sans-serif\""
INK, INK2, MUTE, ACC, SURF = "#0b0b0b", "#52514e", "#8a8781", "#eb6834", "#fcfcfb"
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="100%" height="100%" fill="{SURF}"/>',
     f'<text x="80" y="70" {F} font-size="22" letter-spacing="4" fill="{MUTE}">BLOODSHED, EXTRAPOLATED</text>',
     f'<text x="80" y="118" font-family="Georgia,\'Times New Roman\',serif" font-size="34" fill="{INK}">Extra deaths per 100,000 a year, if today\'s occupied-home</text>',
     f'<text x="80" y="160" font-family="Georgia,\'Times New Roman\',serif" font-size="34" fill="{INK}">burglaries were wrench attacks</text>']
for v in range(0, 11, 2):
    o.append(f'<line x1="{X0}" y1="{y(v):.1f}" x2="{X1}" y2="{y(v):.1f}" stroke="#e6e3dc" stroke-width="1"/>')
    o.append(f'<text x="{X0-14}" y="{y(v)+7:.1f}" {F} font-size="20" fill="{MUTE}" text-anchor="end">{v}</text>')
o.append(f'<rect x="{X0}" y="{y(war[1]):.1f}" width="{X1-X0}" height="{y(war[0])-y(war[1]):.1f}" fill="{MUTE}" opacity="0.25"/>')
o.append(f'<text x="{X1}" y="{y(war[1])-12:.1f}" {F} font-size="20" font-weight="bold" fill="{INK}" text-anchor="end">Ukraine, civilians killed in the war, 2025: {war[0]:.1f}–{war[1]:.1f}</text>')
BW, cx = 150, [420, 820]
for (n, b, pop, occ), x in zip(C, cx):
    f = lambda r: b * occ * r / pop * 1e5
    v, lo, hi = f(RATE), f(LO), f(HI)
    l = x - BW / 2
    o.append(f'<rect x="{l}" y="{y(v):.1f}" width="{BW}" height="{YB-y(v):.1f}" fill="{ACC}"/>')
    o.append(f'<line x1="{x}" y1="{y(hi):.1f}" x2="{x}" y2="{y(lo):.1f}" stroke="{INK}" stroke-width="2"/>')
    for e in (lo, hi):
        o.append(f'<line x1="{x-14}" y1="{y(e):.1f}" x2="{x+14}" y2="{y(e):.1f}" stroke="{INK}" stroke-width="2"/>')
    o.append(f'<text x="{l-12}" y="{y(v)+9:.1f}" {F} font-size="26" font-weight="bold" fill="{INK}" text-anchor="end">{v:.1f}</text>')
    o.append(f'<text x="{x}" y="{YB+34}" {F} font-size="22" fill="{INK}" text-anchor="middle">{n}</text>')
    o.append(f'<text x="{x}" y="{YB+60}" {F} font-size="18" fill="{MUTE}" text-anchor="middle">{int(occ*100)}% of burglaries with someone home</text>')
    print(f"{n:16} {v:.1f} ({lo:.1f}-{hi:.1f})")
o.append(f'<line x1="{X0}" y1="{YB}" x2="{X1}" y2="{YB}" stroke="{INK}" stroke-width="2"/>')
cap = ["Conditional extrapolation, not a forecast. Police-recorded home burglaries × share with someone home (ONS; BJS) × 4.6%, the",
       "share of recorded bitcoin wrench attacks ending in a death (16/351, media-sourced registry; black lines: 2.8–7.3%). Assumes a burglar",
       "who meets the holder of a bitcoin fortune behaves like a wrench attacker. Ukraine: UN-verified civilian deaths only, no soldiers."]
for i, t in enumerate(cap):
    o.append(f'<text x="80" y="{H-96+i*27}" {F} font-size="18" fill="{INK2}">{t}</text>')
o.append('</svg>')
open("m1-bloodshed.svg", "w").write("\n".join(o) + "\n")
print("Ukraine", [round(w, 1) for w in war])
