"""Generates the animated SVGs used by the profile README.

Run:  python3 tools/build_assets.py
Output goes to ../assets/. Everything is plain SVG + CSS animation, so it
renders inside GitHub's <img> tags (no JavaScript, no web fonts).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
CAT = "#fb923c"        # orange tabby
CAT_DARK = "#c2410c"
CAT_PINK = "#fda4af"
GREEN = "#3fb950"


def pct(x: float) -> str:
    return f"{max(0.0, min(100.0, x * 100)):.2f}%"


# --------------------------------------------------------------------------
# The cat (side view, facing right). Origin = point between the feet,
# on the ground. Legs carry classes so they can be animated.
# --------------------------------------------------------------------------
def cat_walker(prefix: str) -> str:
    return f"""
  <g class="{prefix}-tail"><path d="M-28 -30 C-46 -32 -52 -50 -44 -64" fill="none" stroke="{CAT}" stroke-width="7" stroke-linecap="round"/></g>
  <rect class="{prefix}-leg {prefix}-legB" x="-22" y="-20" width="7" height="20" rx="3.5" fill="{CAT_DARK}"/>
  <rect class="{prefix}-leg {prefix}-legB2" x="16" y="-20" width="7" height="20" rx="3.5" fill="{CAT_DARK}"/>
  <ellipse cx="0" cy="-28" rx="32" ry="14" fill="{CAT}"/>
  <path d="M-14 -40 q3 8 0 16 M-4 -41 q3 9 0 18 M6 -41 q3 9 0 18" stroke="{CAT_DARK}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".55"/>
  <rect class="{prefix}-leg {prefix}-legA" x="-26" y="-20" width="7" height="20" rx="3.5" fill="{CAT}"/>
  <rect class="{prefix}-leg {prefix}-legA2" x="20" y="-20" width="7" height="20" rx="3.5" fill="{CAT}"/>
  <ellipse cx="24" cy="-36" rx="12" ry="10" fill="{CAT}"/>
  <path d="M25 -50 L28 -66 L37 -54 Z" fill="{CAT}"/>
  <path d="M28 -54 L29.5 -61 L33.5 -55 Z" fill="{CAT_PINK}"/>
  <path d="M37 -53 L45 -65 L47 -50 Z" fill="{CAT}"/>
  <circle cx="35" cy="-42" r="13" fill="{CAT}"/>
  <g class="{prefix}-eye"><ellipse cx="40" cy="-44" rx="2.2" ry="2.8" fill="#1f1300"/></g>
  <circle cx="47.5" cy="-39" r="1.7" fill="{CAT_PINK}"/>
  <path d="M44 -36 h10 M44 -34 l9 3" stroke="#fed7aa" stroke-width="0.9" opacity=".8"/>
"""


def leg_keyframes(name: str, walk_end: float, period: float, total: float, amp: float, phase: int) -> str:
    """Leg swing while walking, then stand still."""
    frames = []
    step = period / 4 / total
    t, i = 0.0, phase
    seq = [0, amp, 0, -amp]
    while t < walk_end:
        frames.append(f"{pct(t)}{{transform:rotate({seq[i % 4]}deg)}}")
        t += step
        i += 1
    frames.append(f"{pct(walk_end)}{{transform:rotate(0deg)}}")
    frames.append("100%{transform:rotate(0deg)}")
    return f"@keyframes {name}{{{''.join(frames)}}}"


# --------------------------------------------------------------------------
# 1. Header
# --------------------------------------------------------------------------
def header() -> str:
    W, H = 900, 330
    T = 12.0                       # loop length (s)
    walk_end = 0.55                # fraction of loop the cat spends walking
    x_start = -90.0
    key_top = 262
    paw_offset = 19                # front paw is 19px ahead of cat origin

    keys = list("git") + [" "] + list("push") + ["⏎"]
    widths = [50 if k not in (" ", "⏎") else (96 if k == " " else 64) for k in keys]
    xs, x = [], 48
    for w in widths:
        xs.append(x)
        x += w + 8
    centers = [xs[i] + widths[i] / 2 for i in range(len(keys))]
    x_stop = centers[-1] - paw_offset          # cat stops with paw on Enter
    dist = x_stop - x_start

    def frac_at(cx: float) -> float:
        return (cx - paw_offset - x_start) / dist * walk_end

    press = [frac_at(c) for c in centers]
    enter_t = press[-1]
    fade_out = 0.93

    css = [f"""
    .name {{ font: 800 46px {SANS}; fill: {TEXT}; letter-spacing: -.5px }}
    .cat-word {{ fill: {CAT} }}
    .sub {{ font: 500 20px {SANS}; fill: #c9d1d9 }}
    .stack {{ font: 500 15px {MONO}; fill: {MUTED} }}
    .key-label {{ font: 600 17px {MONO}; fill: #c9d1d9; text-anchor: middle }}
    .term {{ font: 500 15px {MONO}; fill: #c9d1d9 }}
    .bubble {{ font: 700 13px {MONO}; fill: {BG} }}
    .walker {{ animation: walk {T}s linear infinite }}
    @keyframes walk {{
      0% {{ transform: translateX({x_start}px); opacity: 1 }}
      {pct(walk_end)} {{ transform: translateX({x_stop}px); opacity: 1 }}
      {pct(fade_out)} {{ transform: translateX({x_stop}px); opacity: 1 }}
      {pct(fade_out + .03)} {{ transform: translateX({x_stop}px); opacity: 0 }}
      100% {{ transform: translateX({x_start}px); opacity: 0 }}
    }}
    .cat-leg {{ transform-box: fill-box; transform-origin: 50% 0% }}
    .cat-legA, .cat-legB2 {{ animation: legA {T}s linear infinite }}
    .cat-legA2, .cat-legB {{ animation: legB {T}s linear infinite }}
    {leg_keyframes('legA', walk_end, 0.5, T, 22, 0)}
    {leg_keyframes('legB', walk_end, 0.5, T, 22, 2)}
    .cat-tail {{ transform-box: fill-box; transform-origin: 100% 100%; animation: tail 1.6s ease-in-out infinite }}
    @keyframes tail {{ 0%,100% {{ transform: rotate(-6deg) }} 50% {{ transform: rotate(10deg) }} }}
    .cat-eye {{ transform-box: fill-box; transform-origin: center; animation: blink 4s infinite }}
    @keyframes blink {{ 0%,92%,100% {{ transform: scaleY(1) }} 95% {{ transform: scaleY(.1) }} }}
    .bob {{ animation: bob .25s ease-in-out infinite alternate }}
    @keyframes bob {{ from {{ transform: translateY(0) }} to {{ transform: translateY(-1.5px) }} }}
    .dot {{ animation: pulse 1.8s ease-in-out infinite; transform-box: fill-box; transform-origin: center }}
    @keyframes pulse {{ 0%,100% {{ opacity: 1; transform: scale(1) }} 50% {{ opacity: .35; transform: scale(.7) }} }}
    .caret {{ animation: caret {T}s linear infinite, blinkc 1s steps(1) infinite }}
    @keyframes blinkc {{ 50% {{ fill-opacity: 0 }} }}
    """]

    # Keys go down when stepped on
    for i, t in enumerate(press):
        a, b, c = t - .006, t + .004, t + .035
        css.append(f"""
    .k{i} {{ animation: k{i} {T}s linear infinite }}
    @keyframes k{i} {{ 0%,{pct(a)} {{ transform: translateY(0) }} {pct(b)} {{ transform: translateY(4px) }} {pct(c)},100% {{ transform: translateY(0) }} }}
    .kc{i} {{ animation: kc{i} {T}s linear infinite }}
    @keyframes kc{i} {{ 0%,{pct(a)} {{ fill: #1f2630 }} {pct(b)} {{ fill: #3b2a1c }} {pct(c + .05)},100% {{ fill: #1f2630 }} }}""")

    # Typed characters appear as each key is pressed
    typed = [k for k in keys[:-1]]
    term_x, term_y = 668, 278
    cw = 9.0
    for i, t in enumerate(press[:-1]):
        css.append(f"""
    .c{i} {{ opacity: 0; animation: c{i} {T}s linear infinite }}
    @keyframes c{i} {{ 0%,{pct(t)} {{ opacity: 0 }} {pct(t + .003)},{pct(fade_out)} {{ opacity: 1 }} {pct(fade_out + .03)},100% {{ opacity: 0 }} }}""")
    # caret position steps along with typing
    caret_frames = [f"0%{{transform:translateX(0)}}"]
    for i, t in enumerate(press[:-1]):
        caret_frames.append(f"{pct(t)}{{transform:translateX({i * cw}px)}}")
        caret_frames.append(f"{pct(t + .003)}{{transform:translateX({(i + 1) * cw}px)}}")
    caret_frames.append(f"{pct(enter_t)}{{transform:translateX({len(typed) * cw}px)}}")
    caret_frames.append(f"{pct(enter_t + .003)}{{transform:translateX(0);opacity:0}}")
    caret_frames.append(f"{pct(fade_out + .03)}{{transform:translateX(0);opacity:0}}")
    caret_frames.append(f"{pct(fade_out + .035)}{{transform:translateX(0);opacity:1}}")
    caret_frames.append("100%{transform:translateX(0);opacity:1}")
    css.append("@keyframes caret{" + "".join(caret_frames) + "}")

    out_t = enter_t + .03
    css.append(f"""
    .out {{ opacity: 0; animation: out {T}s linear infinite }}
    @keyframes out {{ 0%,{pct(out_t)} {{ opacity: 0 }} {pct(out_t + .01)},{pct(fade_out)} {{ opacity: 1 }} {pct(fade_out + .03)},100% {{ opacity: 0 }} }}
    .bub {{ opacity: 0; animation: bub {T}s ease-out infinite; transform-box: fill-box; transform-origin: 0% 100% }}
    @keyframes bub {{ 0%,{pct(out_t + .04)} {{ opacity: 0; transform: scale(.6) }} {pct(out_t + .07)},{pct(fade_out - .02)} {{ opacity: 1; transform: scale(1) }} {pct(fade_out)},100% {{ opacity: 0; transform: scale(.6) }} }}""")

    key_svg = []
    for i, k in enumerate(keys):
        label = "space" if k == " " else k
        size = ' style="font-size:13px"' if k == " " else ""
        key_svg.append(f"""
    <rect x="{xs[i]}" y="{key_top}" width="{widths[i]}" height="46" rx="8" fill="#0a0d12" stroke="{BORDER}"/>
    <g class="k{i}">
      <rect class="kc{i}" x="{xs[i]}" y="{key_top - 6}" width="{widths[i]}" height="46" rx="8" fill="#1f2630" stroke="#3d4654"/>
      <text class="key-label" x="{centers[i]}" y="{key_top + 22}"{size}>{label}</text>
    </g>""")

    chars = "".join(
        f'<text class="term c{i}" x="{term_x + i * cw}" y="{term_y}">{"&#160;" if ch == " " else ch}</text>'
        for i, ch in enumerate(typed)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Rico Daniel Catacutan, full-stack developer. A cat walks across the keyboard and ships the code.">
  <title>Rico Daniel Catacutan · full-stack developer</title>
  <style>{''.join(css)}</style>
  <defs>
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#ffffff" opacity=".05"/></pattern>
    <radialGradient id="glow" cx="12%" cy="0%" r="70%"><stop offset="0" stop-color="{CAT}" stop-opacity=".16"/><stop offset="1" stop-color="{CAT}" stop-opacity="0"/></radialGradient>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#dots)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>

    <text class="name" x="46" y="98">Rico Daniel <tspan class="cat-word">Cat</tspan>acutan</text>
    <text class="sub" x="48" y="138">Full-stack developer</text>
    <text class="stack" x="48" y="170">Next.js · TypeScript · Laravel · React Native</text>

    {''.join(key_svg)}

    <rect x="652" y="218" width="214" height="96" rx="10" fill="{PANEL}" stroke="{BORDER}"/>
    <circle cx="668" cy="234" r="4.5" fill="#ff5f57"/><circle cx="682" cy="234" r="4.5" fill="#febc2e"/><circle cx="696" cy="234" r="4.5" fill="#28c840"/>
    <text class="term" x="{term_x - 14}" y="{term_y}" fill="{GREEN}" style="fill:{GREEN}">$</text>
    {chars}
    <text class="term out" x="{term_x - 14}" y="{term_y + 24}" style="fill:{GREEN}">✓ shipped to prod</text>
    <rect class="caret" x="{term_x}" y="{term_y - 13}" width="8" height="16" fill="{CAT}"/>

    <g transform="translate(0 {key_top - 6})">
      <g class="walker">
        <g class="bob">{cat_walker('cat')}</g>
        <g transform="translate(52 -96)"><g class="bub">
          <path d="M0 0 h58 a8 8 0 0 1 8 8 v14 a8 8 0 0 1 -8 8 h-44 l-10 10 l2 -10 h-6 a8 8 0 0 1 -8 -8 v-14 a8 8 0 0 1 8 -8 z" transform="translate(8 0)" fill="{TEXT}"/>
          <text class="bubble" x="22" y="20">meow.</text>
        </g></g>
      </g>
    </g>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{BORDER}"/>
</svg>
"""


# --------------------------------------------------------------------------
# Shared browser-window frame for product cards
# --------------------------------------------------------------------------
W_CARD, H_CARD = 900, 280


def window(url: str, accent: str, body: str, css: str, label: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W_CARD}" height="{H_CARD}" viewBox="0 0 {W_CARD} {H_CARD}" role="img" aria-label="{label}">
  <title>{label}</title>
  <style>
    .t {{ font: 800 32px {SANS}; fill: {TEXT}; letter-spacing: -.3px }}
    .tag {{ font: 500 15px {SANS}; fill: {MUTED} }}
    .m {{ font: 500 13px {MONO}; fill: #c9d1d9 }}
    .ms {{ font: 600 11px {MONO}; fill: {MUTED}; letter-spacing: .6px }}
    .chip {{ font: 600 11.5px {SANS}; fill: #c9d1d9 }}
    .url {{ font: 500 12px {MONO}; fill: {MUTED} }}
    .live {{ font: 700 10.5px {SANS}; fill: {GREEN}; letter-spacing: .8px }}
    .ld {{ animation: lp 1.8s ease-in-out 4; transform-box: fill-box; transform-origin: center }}
    @keyframes lp {{ 0%,100% {{ opacity: 1; transform: scale(1) }} 50% {{ opacity: .3; transform: scale(.6) }} }}
    {css}
  </style>
  <defs>
    <clipPath id="f"><rect width="{W_CARD}" height="{H_CARD}" rx="16"/></clipPath>
    <radialGradient id="g" cx="100%" cy="0%" r="80%"><stop offset="0" stop-color="{accent}" stop-opacity=".20"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  </defs>
  <g clip-path="url(#f)">
    <rect width="{W_CARD}" height="{H_CARD}" fill="{BG}"/>
    <rect width="{W_CARD}" height="{H_CARD}" fill="url(#g)"/>
    <rect width="{W_CARD}" height="38" fill="{PANEL}"/>
    <line x1="0" y1="38" x2="{W_CARD}" y2="38" stroke="{BORDER}"/>
    <circle cx="20" cy="19" r="5" fill="#ff5f57"/><circle cx="36" cy="19" r="5" fill="#febc2e"/><circle cx="52" cy="19" r="5" fill="#28c840"/>
    <rect x="76" y="9" width="300" height="20" rx="10" fill="{BG}" stroke="{BORDER}"/>
    <path d="M88 17.5 v-2 a3 3 0 0 1 6 0 v2 M86.5 17.5 h9 v6 h-9 z" fill="none" stroke="{MUTED}" stroke-width="1.2"/>
    <text class="url" x="101" y="23">{url}</text>
    <g transform="translate({W_CARD - 82} 10)">
      <rect width="62" height="18" rx="9" fill="#0f2417" stroke="#238636"/>
      <circle class="ld" cx="12" cy="9" r="3.5" fill="{GREEN}"/>
      <text class="live" x="21" y="13">LIVE</text>
    </g>
    {body}
  </g>
  <rect x=".5" y=".5" width="{W_CARD - 1}" height="{H_CARD - 1}" rx="16" fill="none" stroke="{BORDER}"/>
</svg>
"""


# Label widths at 600 11.5px, measured in a browser with Helvetica/Arial metrics.
# Labels are centered, so small differences between system fonts stay even on both sides.
LABEL_W = {"Chrome": 43.5, "Firefox": 38.3, "Edge": 28.1, "Coursera": 50.5, "Udemy": 38.3, "edX": 21.1,
           "Codecademy": 71.6, "Udacity": 41.5, "Pluralsight": 59.4, "Scrimba": 45.4}


def chip(x: float, y: float, text: str, fill: str = PANEL, stroke: str = BORDER, cls: str = "chip", extra: str = "") -> tuple[str, float]:
    tw = LABEL_W.get(text, len(text) * 6.4) * 1.06   # macOS system font runs slightly wider
    w = round(tw + 22, 1)
    return (f'<g transform="translate({x} {y})"{extra}><rect width="{w}" height="22" rx="11" fill="{fill}" stroke="{stroke}"/>'
            f'<text class="{cls}" x="{w / 2:.1f}" y="15" text-anchor="middle">{text}</text></g>'), w


# --------------------------------------------------------------------------
# 2a. SpacePrompts card
# --------------------------------------------------------------------------
def spaceprompts() -> str:
    A = "#818cf8"       # indigo
    T = 9.0
    css = f"""
    .var {{ fill: {A}; font-weight: 700 }}
    .var {{ animation: glow 2.4s ease-in-out 2 }}
    @keyframes glow {{ 0%,100% {{ fill: {A} }} 50% {{ fill: #c7d2fe }} }}
    .fill {{ transform-box: fill-box; transform-origin: 0 50%; animation: fill {T}s cubic-bezier(.3,.7,.2,1) 1 forwards }}
    @keyframes fill {{ 0%,10% {{ transform: scaleX(0) }} 40%,100% {{ transform: scaleX(1) }} }}
    .chk {{ opacity: 0; animation: chk {T}s ease-out 1 forwards }}
    .chk1 {{ animation-name: chk1 }} .chk2 {{ animation-name: chk2 }} .chk3 {{ animation-name: chk3 }}
    @keyframes chk1 {{ 0%,40% {{ opacity: 0 }} 44%,100% {{ opacity: 1 }} }}
    @keyframes chk2 {{ 0%,46% {{ opacity: 0 }} 50%,100% {{ opacity: 1 }} }}
    @keyframes chk3 {{ 0%,52% {{ opacity: 0 }} 56%,100% {{ opacity: 1 }} }}
    .v {{ opacity: 0; animation: {T}s ease-out 1 forwards }}
    .v1 {{ animation-name: v1 }} .v2 {{ animation-name: v2 }} .v3 {{ animation-name: v3 }}
    @keyframes v1 {{ 0%,2% {{ opacity: 0 }} 6%,100% {{ opacity: 1 }} }}
    @keyframes v2 {{ 0%,20% {{ opacity: 0 }} 24%,100% {{ opacity: 1 }} }}
    @keyframes v3 {{ 0%,60% {{ opacity: 0 }} 64%,100% {{ opacity: 1 }} }}
    .vhl {{ opacity: 0; animation: vhl {T}s ease-out 1 forwards }}
    @keyframes vhl {{ 0%,60% {{ opacity: 0 }} 64%,100% {{ opacity: 1 }} }}
    .cur {{ animation: cur 1s steps(1) 6 }}
    @keyframes cur {{ 50% {{ opacity: 0 }} }}
    """
    checks = ""
    for i, (x, label) in enumerate([(24, "clarity"), (114, "context"), (206, "format")], 1):
        checks += (f'<g class="chk chk{i}" transform="translate({x} 262)"><circle cx="8" cy="8" r="8" fill="{A}" fill-opacity=".2"/>'
                   f'<path d="M4.5 8.2 l2.4 2.4 l4.6 -5" stroke="{A}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                   f'<text class="m" x="22" y="12.5">{label}</text></g>')

    versions = ""
    for i, v in enumerate(["v1", "v2", "v3"], 1):
        y = 138 + (3 - i) * 24
        versions += (f'<g class="v v{i}" transform="translate(334 {y})"><rect width="82" height="20" rx="6" fill="{PANEL}" stroke="{BORDER}"/>'
                     f'<circle cx="12" cy="10" r="3" fill="{MUTED}"/><text class="m" x="22" y="14.5" style="font-size:11.5px">{v}</text>'
                     f'<rect x="44" y="8" width="28" height="4" rx="2" fill="{MUTED}" fill-opacity=".5"/></g>')
    versions += (f'<g class="vhl" transform="translate(334 138)"><rect width="82" height="20" rx="6" fill="none" stroke="{A}" stroke-width="1.5"/>'
                 f'<circle cx="12" cy="10" r="3" fill="{A}"/></g>')

    ext = ""
    x = 32
    for name in ["Chrome", "Firefox", "Edge"]:
        c, w = chip(x, 226, name)
        ext += c
        x += w + 6

    body = f"""
    <text class="t" x="32" y="104">SpacePrompts</text>
    <text class="tag" x="32" y="136">Save, organize, and reuse</text>
    <text class="tag" x="32" y="158">every prompt that works.</text>
    {ext}
    <g transform="translate(436 -53)">
    <rect x="24" y="136" width="296" height="70" rx="10" fill="{PANEL}" stroke="{BORDER}"/>
    <text class="m" x="36" y="161">Summarize <tspan class="var">{{{{article}}}}</tspan> for</text>
    <text class="m" x="36" y="187">a <tspan class="var">{{{{audience}}}}</tspan> in 3 bullets.<tspan class="cur" style="fill:{A}">▍</tspan></text>

    {versions}

    <rect x="24" y="242" width="296" height="8" rx="4" fill="{PANEL}" stroke="{BORDER}"/>
    <rect class="fill" x="24" y="242" width="296" height="8" rx="4" fill="{A}"/>
    {checks}
    </g>
    """
    return window("spaceprompts.com", A, body, css, "SpacePrompts: prompt playground with variables, version history, evaluator, and browser extensions for Chrome, Firefox and Edge")


# --------------------------------------------------------------------------
# 2b. Tudlora card
# --------------------------------------------------------------------------
def tudlora() -> str:
    A = "#2dd4bf"       # teal; swap for Tudlora's brand color if you like
    T = 9.0
    query = "best laravel courses"
    css_parts = [f"""
    .q {{ opacity: 0; animation: {T}s linear 1 forwards }}
    .res {{ opacity: 0; animation: {T}s ease-out 1 forwards }}
    .r1 {{ animation-name: r1 }} .r2 {{ animation-name: r2 }} .r3 {{ animation-name: r3 }}
    @keyframes r1 {{ 0%,34% {{ opacity: 0; transform: translateY(8px) }} 39%,100% {{ opacity: 1; transform: translateY(0) }} }}
    @keyframes r2 {{ 0%,39% {{ opacity: 0; transform: translateY(8px) }} 44%,100% {{ opacity: 1; transform: translateY(0) }} }}
    @keyframes r3 {{ 0%,44% {{ opacity: 0; transform: translateY(8px) }} 49%,100% {{ opacity: 1; transform: translateY(0) }} }}
    .marq {{ animation: marq 14s linear 1 forwards }}
    .cur {{ animation: cur 1s steps(1) 6 }}
    @keyframes cur {{ 50% {{ opacity: 0 }} }}
    .curpos {{ animation: curpos {T}s linear 1 forwards }}
    """]
    cw = 7.8
    qx = 56
    chars = ""
    cur_frames = ["0%{transform:translateX(0)}"]
    for i, ch in enumerate(query):
        a = 0.04 + i * 0.014
        css_parts.append(f"@keyframes q{i}{{0%,{pct(a)}{{opacity:0}}{pct(a + .002)},100%{{opacity:1}}}}")
        chars += f'<text class="m q" style="animation-name:q{i}" x="{qx + i * cw}" y="146">{ch}</text>'
        cur_frames.append(f"{pct(a)}{{transform:translateX({i * cw}px)}}")
        cur_frames.append(f"{pct(a + .002)}{{transform:translateX({(i + 1) * cw}px)}}")
    cur_frames.append(f"100%{{transform:translateX({len(query) * cw}px)}}")
    css_parts.append("@keyframes curpos{" + "".join(cur_frames) + "}")

    results = ""
    providers = [("Udemy", "#a78bfa"), ("Coursera", "#60a5fa"), ("edX", "#f472b6")]
    widths = [210, 176, 196]
    for i, ((prov, col), w) in enumerate(zip(providers, widths), 1):
        y = 168 + (i - 1) * 42
        c, cwid = chip(0, 0, prov, fill=BG, stroke=col)
        results += f"""
    <g class="res r{i}"><g transform="translate(24 {y})">
      <rect width="392" height="36" rx="8" fill="{PANEL}" stroke="{BORDER}"/>
      <rect x="8" y="7" width="38" height="22" rx="5" fill="{col}" fill-opacity=".25"/>
      <path d="M22 13 l9 5 l-9 5 z" fill="{col}"/>
      <rect x="56" y="11" width="{w}" height="6" rx="3" fill="#c9d1d9" fill-opacity=".55"/>
      <rect x="56" y="22" width="{w * .55:.0f}" height="5" rx="2.5" fill="{MUTED}" fill-opacity=".45"/>
      <g transform="translate({384 - cwid} 7)">{c}</g>
    </g></g>"""

    names = ["Coursera", "Udemy", "edX", "Codecademy", "Udacity", "Pluralsight", "Scrimba"]
    strip, x = "", 0.0
    for n in names * 2:
        c, w = chip(x, 0, n)
        strip += c
        x += w + 8
    half = x / 2
    css_parts.append(f"@keyframes marq{{from{{transform:translateX(0)}}to{{transform:translateX(-{half:.1f}px)}}}}")

    body = f"""
    <text class="t" x="32" y="104">Tudlora</text>
    <text class="tag" x="32" y="136">Find your next course</text>
    <text class="tag" x="32" y="158">in one place.</text>
    <g transform="translate(436 -48)">
    <rect x="24" y="122" width="392" height="36" rx="18" fill="{PANEL}" stroke="{A}" stroke-opacity=".7"/>
    <circle cx="42" cy="139" r="6" fill="none" stroke="{A}" stroke-width="2"/>
    <line x1="46.5" y1="143.5" x2="51" y2="148" stroke="{A}" stroke-width="2" stroke-linecap="round"/>
    {chars}
    <g class="curpos"><rect class="cur" x="{qx}" y="133" width="2" height="16" fill="{A}"/></g>
    {results}
    </g>

    <defs><clipPath id="strip"><rect x="32" y="224" width="360" height="26"/></clipPath>
    <linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
    <linearGradient id="fadeR" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>
    <g clip-path="url(#strip)"><g transform="translate(32 226)"><g class="marq">{strip}</g></g></g>
    <rect x="32" y="224" width="24" height="26" fill="url(#fadeL)"/>
    <rect x="368" y="224" width="24" height="26" fill="url(#fadeR)"/>
    """
    return window("tudlora.com", A, body, "".join(css_parts), "Tudlora: search developer courses from Coursera, Udemy, edX, Codecademy, Udacity, Pluralsight and Scrimba in one place")


# --------------------------------------------------------------------------
# 3. Paw-print divider: a trail of prints walks across, then fades
# --------------------------------------------------------------------------
PAW = ('<ellipse cx="0" cy="3" rx="6.5" ry="5.5"/><ellipse cx="-7" cy="-5" rx="2.6" ry="3.3"/>'
       '<ellipse cx="-2.4" cy="-9" rx="2.6" ry="3.3"/><ellipse cx="2.4" cy="-9" rx="2.6" ry="3.3"/>'
       '<ellipse cx="7" cy="-5" rx="2.6" ry="3.3"/>')


def paws() -> str:
    W, H, T, n = 900, 44, 7.0, 16
    css, prints = [], []
    for i in range(n):
        a = 0.03 + i * 0.042
        css.append(f".p{i}{{animation:p{i} {T}s ease-out infinite}}"
                   f"@keyframes p{i}{{0%,{pct(a)}{{opacity:0}}{pct(a + .02)}{{opacity:.9}}{pct(min(a + .3, .9))}{{opacity:.35}}{pct(.93)},100%{{opacity:0}}}}")
        x = 40 + i * (W - 80) / (n - 1)
        y = 15 if i % 2 == 0 else 30
        prints.append(f'<g class="p{i}" opacity="0" transform="translate({x:.1f} {y}) rotate(90) scale(.85)">{PAW}</g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Paw print divider">
  <style>{''.join(css)}</style>
  <g fill="{CAT}">{''.join(prints)}</g>
</svg>
"""


# --------------------------------------------------------------------------
# 4. Footer: the cat sleeps on the warm laptop
# --------------------------------------------------------------------------
def footer() -> str:
    W, H = 900, 170
    css = f"""
    .h {{ font: 800 24px {SANS}; fill: {TEXT}; letter-spacing: -.3px }}
    .s {{ font: 500 15px {SANS}; fill: {MUTED} }}
    .code {{ font: 500 11px {MONO} }}
    .breath {{ transform-box: fill-box; transform-origin: 50% 100%; animation: breath 3.2s ease-in-out infinite }}
    @keyframes breath {{ 0%,100% {{ transform: scale(1,1) }} 50% {{ transform: scale(1.02,1.06) }} }}
    .z {{ font: 800 16px {SANS}; fill: {CAT}; opacity: 0; animation: z 3.6s ease-out infinite }}
    .z2 {{ animation-delay: 1.2s; font-size: 13px }} .z3 {{ animation-delay: 2.4s; font-size: 11px }}
    @keyframes z {{ 0% {{ opacity: 0; transform: translate(0,0) }} 20% {{ opacity: 1 }} 100% {{ opacity: 0; transform: translate(14px,-34px) }} }}
    .tail {{ transform-box: fill-box; transform-origin: 0% 50%; animation: flick 5s ease-in-out infinite }}
    @keyframes flick {{ 0%,80%,100% {{ transform: rotate(0) }} 86% {{ transform: rotate(-8deg) }} 92% {{ transform: rotate(4deg) }} }}
    .ln {{ animation: ln 2.8s ease-in-out infinite }}
    @keyframes ln {{ 0%,100% {{ opacity: .9 }} 50% {{ opacity: .45 }} }}
    """
    # laptop screen lines (decorative code)
    lines = ""
    for i, (w, col) in enumerate([(70, "#ff7b72"), (110, "#79c0ff"), (54, "#d2a8ff"), (90, "#7ee787"), (64, "#79c0ff")]):
        lines += f'<rect class="ln" style="animation-delay:{i * .4:.1f}s" x="{618 + (i % 2) * 12}" y="{62 + i * 11}" width="{w}" height="5" rx="2.5" fill="{col}" fill-opacity=".8"/>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Thanks for stopping by. A cat is asleep on a laptop.">
  <title>Thanks for stopping by</title>
  <style>{css}</style>
  <defs><clipPath id="ff"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <radialGradient id="fg" cx="80%" cy="100%" r="60%"><stop offset="0" stop-color="{CAT}" stop-opacity=".14"/><stop offset="1" stop-color="{CAT}" stop-opacity="0"/></radialGradient></defs>
  <g clip-path="url(#ff)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#fg)"/>
    <text class="h" x="48" y="94">Thanks for stopping by.</text>

    <!-- laptop -->
    <rect x="600" y="44" width="190" height="86" rx="8" fill="{PANEL}" stroke="{BORDER}" stroke-width="2"/>
    {lines}
    <path d="M580 130 h230 l-10 12 h-210 z" fill="#21262d" stroke="{BORDER}"/>

    <!-- sleeping cat curled on the keyboard deck -->
    <g transform="translate(700 131)">
      <g class="tail"><path d="M30 -4 C 52 -2, 58 -18, 44 -24" fill="none" stroke="{CAT}" stroke-width="8" stroke-linecap="round"/></g>
      <g class="breath">
        <ellipse cx="0" cy="-17" rx="38" ry="19" fill="{CAT}"/>
        <path d="M-14 -33 q4 10 0 22 M-2 -36 q4 12 0 26 M10 -35 q4 11 0 24" stroke="{CAT_DARK}" stroke-width="3.5" fill="none" stroke-linecap="round" opacity=".5"/>
      </g>
      <circle cx="-30" cy="-16" r="14" fill="{CAT}"/>
      <path d="M-42 -24 L-44 -40 L-32 -29 Z" fill="{CAT}"/><path d="M-41 -28 L-42 -35 L-36 -30 Z" fill="{CAT_PINK}"/>
      <path d="M-27 -29 L-19 -40 L-17 -24 Z" fill="{CAT}"/>
      <path d="M-38 -15 q3 3 6 0 M-28 -15 q3 3 6 0" stroke="#7c2d12" stroke-width="1.8" fill="none" stroke-linecap="round"/>
      <circle cx="-30" cy="-10" r="1.6" fill="{CAT_PINK}"/>
      <ellipse cx="-14" cy="-3" rx="9" ry="4" fill="#fdba74"/>
      <text class="z" x="-50" y="-44">z</text><text class="z z2" x="-50" y="-44">z</text><text class="z z3" x="-50" y="-44">z</text>
    </g>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{BORDER}"/>
</svg>
"""


if __name__ == "__main__":
    for name, fn in [("header", header), ("spaceprompts", spaceprompts), ("tudlora", tudlora),
                     ("paws", paws)]:
        # assets/footer.svg is built by tools/build_footer.py from your real contribution graph
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print(f"wrote {name}.svg")
