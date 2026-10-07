"""Builds assets/footer.svg from your real GitHub contribution graph.

GitHub Actions runs this once a day (see .github/workflows/footer.yml).
It reads the same contribution calendar shown on your profile, draws it,
and puts the sleeping cat on the most recent week.

Run locally with sample data:  python3 tools/build_footer.py --sample
"""
import json
import os
import random
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_assets import BG, BORDER, CAT, CAT_DARK, CAT_PINK, MUTED, SANS, TEXT  # noqa: E402

USER = os.environ.get("PROFILE_USER", "ricodane")
OUT = Path(__file__).resolve().parent.parent / "assets" / "footer.svg"

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
GREENS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]   # GitHub dark-theme scale

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionLevel } }
      }
    }
  }
}"""


def fetch_calendar(token: str) -> tuple[int, list[list[int]]]:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": f"{USER}-profile-footer"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return parse_calendar(payload)


def parse_calendar(payload: dict) -> tuple[int, list[list[int]]]:
    cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[LEVELS[d["contributionLevel"]] for d in w["contributionDays"]] for w in cal["weeks"]]
    if len(weeks) < 50:
        raise RuntimeError(f"unexpected calendar shape: {len(weeks)} weeks")
    return int(cal["totalContributions"]), weeks


def sample_calendar() -> tuple[int, list[list[int]]]:
    random.seed(7)
    weeks = []
    for w in range(53):
        days = 7 if w < 52 else (date.today().weekday() + 2) % 7 or 7
        weeks.append([random.choices([0, 1, 2, 3, 4], [12, 23, 27, 24, 14])[0] for _ in range(days)])
    return 3899, weeks


def sleeping_cat() -> str:
    """Curled-up cat; origin is the middle of its belly on the surface it lies on."""
    return f"""
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
      <text class="z" x="-50" y="-44">z</text><text class="z z2" x="-50" y="-44">z</text><text class="z z3" x="-50" y="-44">z</text>"""


def footer(total: int, weeks: list[list[int]]) -> str:
    W, H = 900, 222
    cs, gap = 12, 3
    n = len(weeks)
    x0 = (W - n * (cs + gap) + gap) / 2
    y0 = 82
    cells = []
    for wi, days in enumerate(weeks):
        for di, lvl in enumerate(days):
            cells.append(
                f'<rect class="cell" style="animation-delay:{wi * .018:.2f}s" x="{x0 + wi * (cs + gap):.1f}" '
                f'y="{y0 + di * (cs + gap)}" width="{cs}" height="{cs}" rx="2.5" fill="{GREENS[lvl]}"/>')
    grid_end = x0 + n * (cs + gap) - gap
    cat_x, cat_y, cat_s = grid_end - 33, y0 + 1, .62

    css = f"""
    .h {{ font: 800 24px {SANS}; fill: {TEXT}; letter-spacing: -.3px }}
    .s {{ font: 500 13px {SANS}; fill: {MUTED} }}
    .cell {{ opacity: 0; animation: pop .5s ease-out forwards }}
    @keyframes pop {{ from {{ opacity: 0; transform: translateY(4px) }} to {{ opacity: 1; transform: none }} }}
    .breath {{ transform-box: fill-box; transform-origin: 50% 100%; animation: breath 3.2s ease-in-out infinite }}
    @keyframes breath {{ 0%,100% {{ transform: scale(1,1) }} 50% {{ transform: scale(1.02,1.06) }} }}
    .z {{ font: 800 16px {SANS}; fill: {CAT}; opacity: 0; animation: z 3.6s ease-out infinite }}
    .z2 {{ animation-delay: 1.2s; font-size: 13px }} .z3 {{ animation-delay: 2.4s; font-size: 11px }}
    @keyframes z {{ 0% {{ opacity: 0; transform: translate(0,0) }} 20% {{ opacity: 1 }} 100% {{ opacity: 0; transform: translate(14px,-34px) }} }}
    .tail {{ transform-box: fill-box; transform-origin: 0% 50%; animation: flick 5s ease-in-out infinite }}
    @keyframes flick {{ 0%,80%,100% {{ transform: rotate(0) }} 86% {{ transform: rotate(-8deg) }} 92% {{ transform: rotate(4deg) }} }}
    """
    label = f"{total:,} contributions in the last year"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Thanks for stopping by. {label}.">
  <title>Thanks for stopping by</title>
  <style>{css}</style>
  <defs><clipPath id="ff"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <radialGradient id="fg" cx="80%" cy="100%" r="60%"><stop offset="0" stop-color="{CAT}" stop-opacity=".12"/><stop offset="1" stop-color="{CAT}" stop-opacity="0"/></radialGradient></defs>
  <g clip-path="url(#ff)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#fg)"/>
    <text class="h" x="{x0:.0f}" y="52">Thanks for stopping by.</text>
    {''.join(cells)}
    <text class="s" x="{x0:.0f}" y="{y0 + 7 * (cs + gap) + 22}">{label}</text>
    <g transform="translate({cat_x:.1f} {cat_y}) scale({cat_s})">{sleeping_cat()}</g>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{BORDER}"/>
</svg>
"""


def main() -> int:
    if "--sample" in sys.argv:
        total, weeks = sample_calendar()
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print("GITHUB_TOKEN is not set; use --sample for a local preview", file=sys.stderr)
            return 1
        try:
            total, weeks = fetch_calendar(token)
        except Exception as e:                      # keep the existing footer if anything goes wrong
            print(f"Could not fetch the contribution calendar: {e}", file=sys.stderr)
            return 1
    OUT.write_text(footer(total, weeks), encoding="utf-8")
    print(f"wrote {OUT.name}: {total:,} contributions, {len(weeks)} weeks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
