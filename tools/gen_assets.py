#!/usr/bin/env python3
"""Generates the animated retro-PC SVG assets used by the profile README.

Run from the repo root:  python3 tools/gen_assets.py
All animation is SMIL/CSS inside the SVG, because GitHub strips JS/CSS from READMEs
but still plays animated SVGs rendered as <img>.
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
FONT = "'VT323','Courier New',Courier,'Liberation Mono',monospace"
GREEN, DIM, AMBER, BG = "#33ff66", "#1fa344", "#ffb000", "#0a0f0a"
CW = 0.6  # monospace glyph width / font-size


def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


def common_defs():
    return f"""
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="2" fill="#000" fill-opacity=".33"/>
    </pattern>
    <filter id="glow" x="-10%" y="-30%" width="120%" height="160%">
      <feGaussianBlur stdDeviation="1.3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{GREEN}" stop-opacity=".09"/>
      <stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>
    </linearGradient>"""


BASE_CSS = f"""
    text {{ font-family:{FONT}; fill:{GREEN}; }}
    .dim {{ fill:{DIM}; }} .amber {{ fill:{AMBER}; }} .white {{ fill:#d9ffe2; }}
    .blink {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity:0 }} }}"""


# ---------------------------------------------------------------- header ---
T = 16.0  # full boot -> show -> glitch -> power-off cycle, in seconds


def kt(*secs):
    return ";".join(f"{s / T:.4f}" for s in secs)


def show(on, off):
    """Discrete opacity window [on, off) inside the looping cycle."""
    return (f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" '
            f'calcMode="discrete" values="0;1;0" keyTimes="{kt(0, on, off)}"/>')


def typing(cid, x, y, h, text_len, size, t0, t1, off):
    """clipPath that reveals text char by char between t0 and t1, hidden at off."""
    cw = CW * size
    n = text_len
    times = [0] + [t0 + (t1 - t0) * i / n for i in range(n)] + [off]
    widths = [0] + [round(cw * (i + 1), 1) for i in range(n)] + [0]
    widths[-2] += cw  # slack for font-width differences
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="0" height="{h}">'
            f'<animate attributeName="width" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
            f'values="{";".join(map(str, widths))}" keyTimes="{kt(*times)}"/></rect></clipPath>')


def cursor(x, y, w, h, size, n, t0, t1, off):
    cw = CW * size
    times = [0, t0] + [t0 + (t1 - t0) * i / n for i in range(1, n + 1)]
    xs = [x, x] + [round(x + cw * i, 1) for i in range(1, n + 1)]
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{GREEN}" opacity="0">'
            f'{show(t0, off)}'
            f'<animate attributeName="x" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
            f'values="{";".join(map(str, xs))}" keyTimes="{kt(*times)}"/></rect>')


def header():
    sx, sy, sw, sh = 70, 48, 760, 330
    cy = sy + sh / 2
    defs, body = [], []
    tx = 100

    # boot lines
    body.append(f'<text x="{tx}" y="88" font-size="20" opacity="0">{show(0.7, T - .3)}'
                f'RMM-BIOS v2.05 <tspan class="dim">(C) 2026 Moreno Menendez Systems</tspan></text>')
    body.append(f'<text x="{tx}" y="114" font-size="20" opacity="0">{show(1.1, T - .3)}'
                f'CPU: Human Brain @ ∞ coffee MHz ......</text>')
    body.append(f'<text x="590" y="114" font-size="20" opacity="0">{show(1.6, T - .3)}[ OK ]</text>')
    body.append(f'<text x="{tx}" y="140" font-size="20" opacity="0">{show(1.8, T - .3)}'
                f'Memory test: </text>')
    for i in range(1, 11):  # counting memory 064K -> 640K
        on = 1.8 + (i - 1) * 0.09
        off = on + 0.09 if i < 10 else T - .3
        body.append(f'<text x="250" y="140" font-size="20" opacity="0">{show(on, off)}{i * 64:03d}K</text>')
    body.append(f'<text x="590" y="140" font-size="20" opacity="0">{show(2.8, T - .3)}[ OK ]</text>')

    # command
    cmd = "RUN PROFILE.EXE"
    body.append(f'<text x="{tx}" y="172" font-size="20" class="amber" opacity="0">{show(3.0, T - .3)}C:\\&gt;</text>')
    defs.append(typing("tcmd", 160, 150, 30, len(cmd), 20, 3.1, 3.9, T - .3))
    body.append(f'<g clip-path="url(#tcmd)"><text x="160" y="172" font-size="20">{cmd}</text></g>')

    # name + glitch
    name = "RODRIGO MORENO MENÉNDEZ"
    fs = 44
    defs.append(typing("tname", tx, 218, 56, len(name), fs, 4.2, 6.0, T - .3))
    body.append(cursor(tx, 226, 22, 40, fs, len(name), 4.2, 6.0, 6.4))
    jitter = "0 0;-6 0;5 -2;-3 2;7 0;0 0;-4 1;0 0"
    jt = kt(0, 14.4, 14.5, 14.6, 14.7, 14.8, 14.95, 15.1)
    body.append(
        f'<g clip-path="url(#tname)">'
        f'<g><animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" '
        f'calcMode="discrete" values="{jitter}" keyTimes="{jt}"/>'
        f'<text x="{tx - 3}" y="262" font-size="{fs}" font-weight="bold" style="fill:#ff3355" opacity="0">'
        f'{show(14.4, 15.1)}{name}</text>'
        f'<text x="{tx + 3}" y="262" font-size="{fs}" font-weight="bold" style="fill:#33ccff" opacity="0">'
        f'{show(14.4, 15.1)}{name}</text>'
        f'<text x="{tx}" y="262" font-size="{fs}" font-weight="bold">{name}</text></g></g>')

    # rotating taglines
    tags = ["CS Student @ UCJC · Madrid", "Automation & scripting addict",
            "Python · Java · C# · JS · C", "Open to collabs & internships"]
    for i, tag in enumerate(tags):
        t0 = 6.4 + 2 * i
        defs.append(typing(f"ttag{i}", 126, 286, 28, len(tag), 22, t0, t0 + 0.8, t0 + 1.95))
        body.append(f'<g clip-path="url(#ttag{i})"><text x="126" y="306" font-size="22">{tag.replace("&", "&amp;")}</text></g>')
    body.append(f'<text x="{tx}" y="306" font-size="22" class="amber" opacity="0">{show(6.4, T - .3)}&gt;</text>')

    # prompt
    body.append(f'<text x="{tx}" y="346" font-size="22" opacity="0">{show(6.4, T - .3)}'
                f'C:\\&gt; <tspan class="blink">█</tspan></text>')
    # top-right status
    body.append(f'<text x="800" y="88" font-size="18" text-anchor="end" class="amber" opacity="0">'
                f'{show(0.7, T - .3)}<tspan class="blink">●</tspan> ONLINE</text>')

    # power on / off: content is revealed through a clip that grows from a line
    defs.append(
        f'<clipPath id="power"><rect x="{sx}" y="{cy - 1}" width="{sw}" height="2">'
        f'<animate attributeName="y" dur="{T}s" repeatCount="indefinite" values="{cy - 1};{cy - 1};{sy};{sy};{cy - 1};{cy - 1}" '
        f'keyTimes="{kt(0, .1, .45, 15.3, 15.6, T)}"/>'
        f'<animate attributeName="height" dur="{T}s" repeatCount="indefinite" values="2;2;{sh};{sh};2;2" '
        f'keyTimes="{kt(0, .1, .45, 15.3, 15.6, T)}"/></rect></clipPath>')

    floppy_led = (f'<animate attributeName="fill" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
                  f'values="#3a2a00;{AMBER};#3a2a00;{AMBER};#3a2a00;{AMBER};#3a2a00;{AMBER};#3a2a00" '
                  f'keyTimes="{kt(0, 0.7, 1.0, 1.5, 1.9, 2.4, 3.0, 3.4, 4.0)}"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="480" viewBox="0 0 900 480" role="img" aria-label="Rodrigo Moreno Menéndez: animated retro computer boot screen">
  <defs>{common_defs()}
    <linearGradient id="bezel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ebe3cb"/><stop offset="1" stop-color="#b6ab8c"/>
    </linearGradient>
    <linearGradient id="stand" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#cfc5a8"/><stop offset="1" stop-color="#968c70"/>
    </linearGradient>
    <radialGradient id="glass" cx="50%" cy="45%" r="70%">
      <stop offset="0" stop-color="#0e3017"/><stop offset="1" stop-color="#020904"/>
    </radialGradient>
    <radialGradient id="vignette" cx="50%" cy="50%" r="62%">
      <stop offset=".7" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/>
    </radialGradient>
    <clipPath id="crt"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="28"/></clipPath>
    {"".join(defs)}
  </defs>
  <style>{BASE_CSS}
    .flicker {{ animation: flicker 5s infinite; }}
    @keyframes flicker {{ 0%,100%{{opacity:1}} 61%{{opacity:1}} 62%{{opacity:.85}} 63%{{opacity:.97}} 64%{{opacity:.9}} 65%{{opacity:1}} }}
    .sweep {{ animation: sweep 6s linear infinite; }}
    @keyframes sweep {{ from{{transform:translateY(-90px)}} to{{transform:translateY(420px)}} }}
    .led {{ animation: led 1.8s ease-in-out infinite; }}
    @keyframes led {{ 0%,100%{{fill:#39ff6a}} 50%{{fill:#11702a}} }}
  </style>

  <path d="M360 410 L540 410 L578 458 L322 458 Z" fill="url(#stand)"/>
  <rect x="286" y="454" width="328" height="18" rx="6" fill="#a39a7e"/>
  <rect x="30" y="14" width="840" height="404" rx="34" fill="url(#bezel)" stroke="#8f876d" stroke-width="2"/>
  <rect x="56" y="34" width="788" height="358" rx="30" fill="#25251f"/>

  <g clip-path="url(#crt)">
    <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#glass)"/>
    <g clip-path="url(#power)">
      <g class="flicker" filter="url(#glow)">{"".join(body)}</g>
    </g>
    <rect x="{sx}" y="{cy - 2}" width="{sw}" height="4" fill="#d9ffe2" opacity="0">
      <animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="0;1;0;0;1;0;0" keyTimes="{kt(0, .1, .45, 15.3, 15.6, 15.85, T)}"/>
    </rect>
    <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#scan)"/>
    <rect class="sweep" x="{sx}" y="{sy}" width="{sw}" height="80" fill="url(#beam)"/>
    <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#vignette)"/>
  </g>

  <text x="70" y="410" font-size="15" style="fill:#6b6450;font-weight:bold;letter-spacing:3px">RMM-86 · PERSONAL COMPUTER</text>
  <rect x="560" y="399" width="120" height="10" rx="2" fill="#4a463a"/>
  <rect x="563" y="403" width="114" height="2" fill="#1d1b16"/>
  <circle cx="694" cy="404" r="4" fill="#3a2a00">{floppy_led}</circle>
  <circle cx="760" cy="404" r="9" fill="#cfc5a8" stroke="#8f876d"/>
  <circle class="led" cx="790" cy="404" r="5" fill="#39ff6a"/>
  <text x="808" y="409" font-size="12" style="fill:#6b6450;font-weight:bold">PWR</text>
</svg>
'''


# -------------------------------------------------------------- nav keys ---
def nav_key(i, key, label):
    w, h = 152, 50
    delay = i * 0.35
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{key} {label}">
  <defs>{common_defs()}
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{GREEN}" stop-opacity=".28"/>
      <stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="c"><rect x="2" y="2" width="{w - 4}" height="{h - 4}"/></clipPath>
  </defs>
  <style>{BASE_CSS}
    .frame {{ animation: pulse 2.4s ease-in-out {delay}s infinite; }}
    @keyframes pulse {{ 0%,100% {{ stroke:{DIM}; }} 50% {{ stroke:{GREEN}; }} }}
    .shine {{ animation: shine 3.5s ease-in-out {delay}s infinite; }}
    @keyframes shine {{ 0% {{ transform:translateX(-120px) }} 45%,100% {{ transform:translateX({w + 40}px) }} }}
    .arrow {{ animation: nudge 1.2s ease-in-out {delay}s infinite; }}
    @keyframes nudge {{ 0%,100% {{ transform:translateX(0) }} 50% {{ transform:translateX(4px) }} }}
  </style>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="{BG}"/>
  <rect class="frame" x="2" y="2" width="{w - 4}" height="{h - 4}" fill="none" stroke-width="2"/>
  <rect x="5" y="{h - 6}" width="{w - 10}" height="2" fill="{DIM}" opacity=".5"/>
  <g clip-path="url(#c)"><rect class="shine" x="0" y="0" width="80" height="{h}" fill="url(#shine)"/></g>
  <rect x="12" y="12" width="36" height="26" fill="{AMBER}"/>
  <text x="30" y="32" font-size="18" text-anchor="middle" style="fill:{BG};font-weight:bold">{key}</text>
  <g filter="url(#glow)">
    <text x="56" y="32" font-size="18" style="font-weight:bold">{label}</text>
    <text class="arrow amber" x="{w - 20}" y="32" font-size="15">▶</text>
  </g>
</svg>
'''


# -------------------------------------------------------- section titles ---
def section(num, total, cmd):
    w, h, fs = 900, 58, 26
    n = len(cmd)
    cw = CW * fs
    x0 = 92
    t0, dt = 0.4, 0.07
    steps = ";".join(str(round(cw * i, 1)) for i in range(n + 1))
    xs = ";".join(str(round(x0 + cw * i, 1)) for i in range(n + 1))
    dur = n * dt
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="C:\\&gt; {cmd}">
  <defs>{common_defs()}
    <clipPath id="t"><rect x="{x0}" y="0" width="0" height="{h}">
      <animate attributeName="width" begin="{t0}s" dur="{dur:.2f}s" fill="freeze" calcMode="discrete" values="{steps};{round(cw * (n + 1), 1)}"/>
    </rect></clipPath>
  </defs>
  <style>{BASE_CSS}
    .ants {{ stroke-dasharray: 6 6; animation: march 1s linear infinite; }}
    @keyframes march {{ to {{ stroke-dashoffset: -12; }} }}
    .scanbar {{ animation: run 4s ease-in-out infinite; }}
    @keyframes run {{ 0% {{ transform:translateX(-140px) }} 60%,100% {{ transform:translateX({w}px) }} }}
  </style>
  <g filter="url(#glow)">
    <text x="4" y="36" font-size="{fs}" class="amber">C:\\&gt;</text>
    <g clip-path="url(#t)"><text x="{x0}" y="36" font-size="{fs}" style="font-weight:bold">{cmd}</text></g>
    <rect x="{x0}" y="16" width="14" height="24" fill="{GREEN}" class="blink">
      <animate attributeName="x" begin="{t0}s" dur="{dur:.2f}s" fill="freeze" calcMode="discrete" values="{xs}"/>
    </rect>
    <text x="{w - 4}" y="34" font-size="18" text-anchor="end" class="dim">[ {num:02d}/{total:02d} ]</text>
  </g>
  <line class="ants" x1="0" y1="{h - 6}" x2="{w}" y2="{h - 6}" stroke="{DIM}" stroke-width="2"/>
  <rect class="scanbar" x="0" y="{h - 8}" width="140" height="5" fill="{GREEN}" opacity=".8"/>
</svg>
'''


# --------------------------------------------------------------- divider ---
def divider():
    blocks, bw, x0, D = 30, 18, 190, 4.5
    times = [i / blocks * 0.8 for i in range(blocks + 1)] + [1.0]
    widths = [i * bw for i in range(blocks + 1)] + [blocks * bw]
    kts = ";".join(f"{t:.4f}" for t in times)
    pct = []
    for p in range(0, 101, 10):
        on = p / 100 * 0.8
        off = on + 0.08 if p < 100 else 1.0
        pct.append(f'<text x="{x0 + blocks * bw + 20}" y="27" font-size="18" opacity="0">'
                   f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" calcMode="discrete" '
                   f'values="0;1;0" keyTimes="0;{on:.4f};{off:.4f}"/>{p:3d}%</text>'.replace("keyTimes=\"0;0.0000", "keyTimes=\"0;0.0001"))
    spin = []
    for i, ch in enumerate("|/-\\"):
        spin.append(f'<text x="150" y="27" font-size="20" class="amber" opacity="0">'
                    f'<animate attributeName="opacity" dur=".6s" begin="{i * 0.15:.2f}s" repeatCount="indefinite" '
                    f'calcMode="discrete" values="1;0;0;0" keyTimes="0;.25;.5;.75"/>{ch}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="40" viewBox="0 0 900 40" role="img" aria-label="loading bar">
  <defs>{common_defs()}
    <pattern id="blk" width="{bw}" height="16" patternUnits="userSpaceOnUse" x="{x0}">
      <rect x="2" y="0" width="{bw - 4}" height="16" fill="{GREEN}"/>
    </pattern>
    <clipPath id="fill"><rect x="{x0}" y="12" width="0" height="16">
      <animate attributeName="width" dur="{D}s" repeatCount="indefinite" calcMode="discrete" values="{";".join(map(str, widths))}" keyTimes="{kts}"/>
    </rect></clipPath>
  </defs>
  <style>{BASE_CSS}</style>
  <g filter="url(#glow)">
    <text x="20" y="27" font-size="20">LOADING<tspan class="blink">_</tspan></text>
    {"".join(spin)}
    <rect x="{x0 - 4}" y="8" width="{blocks * bw + 8}" height="24" fill="none" stroke="{DIM}" stroke-width="2"/>
    <rect x="{x0}" y="12" width="{blocks * bw}" height="16" fill="url(#blk)" fill-opacity=".12"/>
    <rect x="{x0}" y="12" width="{blocks * bw}" height="16" fill="url(#blk)" clip-path="url(#fill)"/>
    {"".join(pct)}
  </g>
</svg>
'''


# ---------------------------------------------------- footer screensaver ---
def footer():
    w, h = 900, 250
    cx, cy = w / 2, 105
    rnd = random.Random(86)
    stars = []
    for _ in range(70):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(2.2, 5.0)
        r0 = rnd.uniform(4, 30)
        x1, y1 = cx + math.cos(a) * r0, cy + math.sin(a) * r0 * .55
        x2, y2 = cx + math.cos(a) * 520, cy + math.sin(a) * 300
        b = -rnd.uniform(0, d)
        col = AMBER if rnd.random() < .15 else GREEN
        stars.append(
            f'<circle r="1" fill="{col}">'
            f'<animate attributeName="cx" values="{x1:.1f};{x2:.1f}" dur="{d:.2f}s" begin="{b:.2f}s" repeatCount="indefinite" keySplines=".6 0 1 1" calcMode="spline" keyTimes="0;1"/>'
            f'<animate attributeName="cy" values="{y1:.1f};{y2:.1f}" dur="{d:.2f}s" begin="{b:.2f}s" repeatCount="indefinite" keySplines=".6 0 1 1" calcMode="spline" keyTimes="0;1"/>'
            f'<animate attributeName="r" values=".3;2.4" dur="{d:.2f}s" begin="{b:.2f}s" repeatCount="indefinite" keySplines=".6 0 1 1" calcMode="spline" keyTimes="0;1"/>'
            f'<animate attributeName="opacity" values="0;1" dur="{d:.2f}s" begin="{b:.2f}s" repeatCount="indefinite"/>'
            f'</circle>')
    # bouncing logo (independent x / y periods -> wanders around the screen)
    bw_, bh_ = 120, 44
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Screensaver: thanks for visiting">
  <defs>{common_defs()}
    <clipPath id="scr"><rect x="0" y="0" width="{w}" height="{h - 40}" rx="18"/></clipPath>
  </defs>
  <style>{BASE_CSS}</style>
  <rect x="0" y="0" width="{w}" height="{h - 40}" rx="18" fill="#020904" stroke="{DIM}" stroke-width="2"/>
  <g clip-path="url(#scr)">
    {"".join(stars)}
    <g filter="url(#glow)">
      <g>
        <animateTransform attributeName="transform" type="translate" additive="sum" values="10 0;{w - bw_ - 10} 0;10 0" dur="9.3s" repeatCount="indefinite"/>
        <g>
          <animateTransform attributeName="transform" type="translate" values="0 10;0 {h - 40 - bh_ - 10};0 10" dur="5.1s" repeatCount="indefinite"/>
          <rect width="{bw_}" height="{bh_}" fill="{BG}" stroke="{AMBER}" stroke-width="2">
            <animate attributeName="stroke" values="{AMBER};{GREEN};#33ccff;#ff3355;{AMBER}" dur="10.2s" calcMode="discrete" repeatCount="indefinite"/>
          </rect>
          <text x="{bw_ / 2}" y="31" font-size="26" text-anchor="middle" style="font-weight:bold;letter-spacing:4px">RMM
            <animate attributeName="fill" values="{AMBER};{GREEN};#33ccff;#ff3355;{AMBER}" dur="10.2s" calcMode="discrete" repeatCount="indefinite"/>
          </text>
        </g>
      </g>
    </g>
    <rect x="0" y="0" width="{w}" height="{h - 40}" fill="url(#scan)"/>
  </g>
  <g filter="url(#glow)">
    <text x="{w / 2}" y="{h - 10}" font-size="20" text-anchor="middle">
      <tspan class="amber">SYSTEM IDLE</tspan> · THANKS FOR VISITING · PRESS ANY KEY TO REBOOT<tspan class="blink">█</tspan>
    </text>
  </g>
</svg>
'''


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    write("header.svg", header())
    write("divider.svg", divider())
    write("footer.svg", footer())
    keys = [("F1", "ABOUT"), ("F2", "WORK"), ("F3", "STACK"), ("F4", "STATS"), ("F5", "PLAY"), ("F6", "CONTACT")]
    for i, (k, l) in enumerate(keys):
        write(f"key-{l.lower()}.svg", nav_key(i, k, l))
    sections = ["TYPE ABOUT.TXT", "TYPE WORK.LOG", "DIR /STACK", "RUN STATS.EXE", "PLAY ADVENTURE.EXE", "TYPE GOALS.LOG", "DIAL CONTACT.BBS"]
    for i, c in enumerate(sections, 1):
        slug = c.split()[-1].split(".")[0].strip("/").lower()
        write(f"title-{slug}.svg", section(i, len(sections), c))
    print("assets generated")
