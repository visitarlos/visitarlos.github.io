#!/usr/bin/env python3
"""
Elliott/Johnson Custody Calendar Generator
Case No. 04 DR 2018-748-6 — Benton County, AR

P1 = Magdalene Johnson (Defendant / primary custodian / mother) — YELLOW
P2 = Wesley Elliott   (Plaintiff / noncustodial / father)        — GREEN

Confirmed:
 - P1 always has Mother's Day → P1 = mother = Magdalene ✓
 - P2 always has Father's Day → P2 = father = Wesley   ✓
 - Noncustodial (Wesley/P2) gets alternating weekends & Thursday midweek
 - Children were with Magdalene (P1) on Jan 17-18, 2026
   → Jan 16 is NOT a Wesley/P2 weekend Friday ✓ (FIRST_P2_FRIDAY = Jan 12, 2024)
"""
from datetime import date, timedelta
import calendar as cal_mod, os

P1 = 1   # Magdalene Johnson – YELLOW
P2 = 2   # Wesley Elliott    – GREEN

# First Wesley (P2 / noncustodial) alternating weekend Friday under Standard Schedule
# (Jan 2024 transition; confirmed Jan 9-11 2026 = Wesley, Jan 16-18 = Magdalene)
FIRST_P2_FRIDAY = date(2024, 1, 12)

BIRTHDAYS = [(1, 6), (11, 22)]   # S.E. Jan 6 / D.E. Nov 22

def easter(year):
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    month = (h + l - 7*m + 114) // 31
    day   = (h + l - 7*m + 114) % 31 + 1
    return date(year, month, day)

def is_p2_fri(d):
    """True if d is a Wesley (P2 / noncustodial) alternating-weekend Friday."""
    if d.weekday() != 4: return False
    delta = (d - FIRST_P2_FRIDAY).days
    return delta >= 0 and delta % 14 == 0

def nth_wday(year, month, n, wday):
    c, d = 0, date(year, month, 1)
    while True:
        if d.weekday() == wday:
            c += 1
            if c == n: return d
        d += timedelta(1)

def last_wday(year, month, wday):
    d = date(year, month, cal_mod.monthrange(year, month)[1])
    while d.weekday() != wday: d -= timedelta(1)
    return d

def prev_fri(d):
    while d.weekday() != 4: d -= timedelta(1)
    return d

def next_mon(d):
    while d.weekday() != 0: d += timedelta(1)
    return d

def build_schedule(year, spring_break, thanksgiving_break, xmas_last_schoolday,
                   school_last_day=None, prev_xmas_school_return=None):
    even = (year % 2 == 0)
    end  = date(year, 12, 31)
    S = {}

    # Default: P1 (Magdalene, custodial) has all days
    d = date(year, 1, 1)
    while d <= end:
        S[d] = P1
        d += timedelta(1)

    def mark(s, e, p):
        d = max(s, date(year, 1, 1))
        while d <= min(e, end):
            S[d] = p
            d += timedelta(1)

    # ── carry-over from previous year's Christmas break ──────
    # Odd prev year → P2 (Wesley) had Dec 27+; even → P1 (Magdalene) had Dec 27+
    if prev_xmas_school_return:
        prev_even = (year - 1) % 2 == 0
        xmas_carryover_p = P1 if prev_even else P2
        mark(date(year, 1, 1), prev_xmas_school_return - timedelta(1), xmas_carryover_p)

    # ── regular schedule ─────────────────────────────────────
    # Wesley (P2) gets every Thursday midweek
    d = date(year, 1, 1)
    while d <= end:
        if d.weekday() == 3:
            S[d] = P2
        elif is_p2_fri(d):          # Wesley's alternating weekend: Fri-Sun
            mark(d, d + timedelta(2), P2)
        d += timedelta(1)

    # ── summer phase 1: school end → July 4 ─────────────────
    # Magdalene (P1) primary; Wesley (P2) gets Thursdays only (no alternating weekends)
    # Phase 1 Thursdays are SPLIT days: Maggy has kids all morning,
    # Wesley picks up at school release / 3:30 PM (no school).
    splits = {}  # date → (morning_parent, afternoon_parent)
    if school_last_day:
        phase1_s = school_last_day + timedelta(1)
        phase1_e = date(year, 7, 4)
        d = phase1_s
        while d <= phase1_e:
            if d.weekday() != 3:   # not Thursday → P1 (Magdalene)
                S[d] = P1
            else:                  # Thursday → split: Maggy morning, Wesley from 3:30 PM
                splits[d] = (P1, P2)
            d += timedelta(1)

    # ── holiday overrides ────────────────────────────────────
    # SPRING BREAK  (P1=Magdalene odd years, P2=Wesley even years)
    spring_p = P2 if even else P1
    sb_s, sb_e = spring_break
    vis_fri = prev_fri(sb_s - timedelta(1))
    vis_end = next_mon(sb_e + timedelta(1)) - timedelta(1)
    mark(vis_fri, vis_end, spring_p)

    # EASTER WEEKEND Fri–Sun  (P1=Magdalene even, P2=Wesley odd)
    easter_p = P1 if even else P2
    esun = easter(year)
    mark(esun - timedelta(2), esun, easter_p)

    # MOTHER'S DAY WEEKEND Fri–Sun  (always P1 = always Magdalene)
    mday = nth_wday(year, 5, 2, 6)
    mark(mday - timedelta(2), mday, P1)

    # MEMORIAL DAY Fri–Mon  (P2=Wesley even, P1=Magdalene odd)
    memorial_p = P2 if even else P1
    mem = last_wday(year, 5, 0)
    mark(mem - timedelta(3), mem, memorial_p)

    # FATHER'S DAY WEEKEND Fri–Sun  (always P2 = always Wesley)
    # Friday is always in June (school out) → split: Maggy morning, Wesley from 3:30 PM
    fday = nth_wday(year, 6, 3, 6)
    mark(fday - timedelta(2), fday, P2)
    splits[fday - timedelta(2)] = (P1, P2)  # Father's Day Friday: Maggy AM → Wesley PM

    # INDEPENDENCE DAY overnight  (P1=Magdalene even, P2=Wesley odd)
    july4_p = P1 if even else P2
    S[date(year, 7, 4)] = july4_p

    # SUMMER VISITATION Jul 5–Aug 8 (5 weeks) → Wesley (P2 / noncustodial)
    # Starts at 10:00 AM on July 5 → split: Maggy morning, Wesley from 10 AM
    # During summer: Magdalene (P1 / custodial) gets Thursdays only (no alternating weekends)
    # Phase 2 Thursdays are SPLIT days: Wesley all morning, Maggy picks up at 3:30 PM
    sum_s = date(year, 7, 5)
    sum_e = sum_s + timedelta(34)
    mark(sum_s, sum_e, P2)
    splits[sum_s] = (P1, P2)   # July 5: Maggy morning → Wesley from 10 AM
    d = sum_s
    while d <= sum_e:
        if d.weekday() == 3:   # Thu → P1 (Magdalene) midweek only
            S[d] = P1
            splits[d] = (P2, P1)   # Wesley morning → Maggy from 3:30 PM
        d += timedelta(1)

    # LABOR DAY Fri–Mon  (P2=Wesley even, P1=Magdalene odd)
    labor_p = P2 if even else P1
    labor = nth_wday(year, 9, 1, 0)
    mark(labor - timedelta(3), labor, labor_p)

    # HALLOWEEN + overnight  (P2=Wesley even, P1=Magdalene odd)
    halloween_p = P2 if even else P1
    S[date(year, 10, 31)] = halloween_p
    nov1 = date(year, 11, 1)
    if nov1 <= end: S[nov1] = halloween_p

    # THANKSGIVING  (P1=Magdalene even, P2=Wesley odd)
    thanks_p = P1 if even else P2
    tb_s, tb_e = thanksgiving_break
    tb_fri = prev_fri(tb_s - timedelta(1))
    tb_end = next_mon(tb_e + timedelta(1)) - timedelta(1)
    mark(tb_fri, tb_end, thanks_p)

    # CHRISTMAS
    # Even: P2 (Wesley) gets break-start → Dec 26; P1 (Magdalene) gets Dec 27 → end
    # Odd:  P1 (Magdalene) gets break-start → Dec 26; P2 (Wesley) gets Dec 27 → end
    dec27 = date(year, 12, 27)
    if even:
        mark(xmas_last_schoolday, dec27 - timedelta(1), P2)
        mark(dec27, end, P1)
    else:
        mark(xmas_last_schoolday, dec27 - timedelta(1), P1)
        mark(dec27, end, P2)

    # CHILDREN'S BIRTHDAYS  (P1=Magdalene even, P2=Wesley odd)
    bday_p = P1 if even else P2
    for bm, bd in BIRTHDAYS:
        try: S[date(year, bm, bd)] = bday_p
        except ValueError: pass

    return S, splits

YEAR_DATA = {
    # school_last_day       = last day students are in school before summer
    # prev_xmas_school_return = first day of school after Christmas break
    # SOURCE: 2025-2026 calendar (user-confirmed) + 2026-2027 calendar (BOE approved 04-15-2025)
    # 2025 is odd → P2 (Wesley) had Dec 27+; children returned Jan 5, 2026 (user confirmed)
    2026: dict(spring_break=(date(2026,3,23),date(2026,3,27)),        # CONFIRMED: 2025-26 calendar
               thanksgiving_break=(date(2026,11,23),date(2026,11,27)), # CONFIRMED: 2026-27 calendar
               xmas_last_schoolday=date(2026,12,18),                   # CONFIRMED: 2026-27 calendar
               school_last_day=date(2026,5,22),                        # estimated; update from 2025-26 calendar
               prev_xmas_school_return=date(2026,1,5)),                # CONFIRMED: user
    # 2026 is even → P1 (Magdalene) has Dec 27+; return Jan 4, 2027 (CONFIRMED: 2026-27 calendar)
    2027: dict(spring_break=(date(2027,3,22),date(2027,3,26)),        # CONFIRMED: 2026-27 calendar
               thanksgiving_break=(date(2027,11,22),date(2027,11,26)), # estimated (Thanksgiving = Nov 25)
               xmas_last_schoolday=date(2027,12,17),                   # estimated
               school_last_day=date(2027,5,21),                        # CONFIRMED: 2026-27 calendar
               prev_xmas_school_return=date(2027,1,4)),                # CONFIRMED: 2026-27 calendar
    # 2027 is odd → P2 (Wesley) has Dec 27+; approx return Jan 3, 2028
    2028: dict(spring_break=(date(2028,3,20),date(2028,3,24)),
               thanksgiving_break=(date(2028,11,20),date(2028,11,24)),
               xmas_last_schoolday=date(2028,12,15),
               school_last_day=date(2028,5,23),                        # estimated
               prev_xmas_school_return=date(2028,1,3)),
    # 2028 is even → P1 (Magdalene) has Dec 27+; approx return Jan 2, 2029
    2029: dict(spring_break=(date(2029,3,25),date(2029,3,29)),
               thanksgiving_break=(date(2029,11,25),date(2029,11,29)),
               xmas_last_schoolday=date(2029,12,19),
               school_last_day=date(2029,5,22),                        # estimated
               prev_xmas_school_return=date(2029,1,2)),
    # 2029 is odd → P2 (Wesley) has Dec 27+; approx return Jan 6, 2030
    2030: dict(spring_break=(date(2030,3,18),date(2030,3,22)),
               thanksgiving_break=(date(2030,11,25),date(2030,11,29)),
               xmas_last_schoolday=date(2030,12,20),
               school_last_day=date(2030,5,21),                        # estimated
               prev_xmas_school_return=date(2030,1,6)),
    # 2030 is even → P1 (Magdalene) has Dec 27+; approx return Jan 5, 2031
    2031: dict(spring_break=(date(2031,3,24),date(2031,3,28)),
               thanksgiving_break=(date(2031,11,24),date(2031,11,28)),
               xmas_last_schoolday=date(2031,12,19),
               school_last_day=date(2031,5,20),                        # estimated
               prev_xmas_school_return=date(2031,1,5)),
}

MONTH_NAMES = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
DOW = ['Su','Mo','Tu','We','Th','Fr','Sa']

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#dde1e7;padding:14px}
header{text-align:center;margin-bottom:10px}
h1{font-size:22px;color:#111;font-weight:700}
.sub{font-size:11px;color:#555;margin-top:3px}
.leg{display:flex;justify-content:center;gap:26px;margin-bottom:12px;font-size:12px;flex-wrap:wrap}
.li{display:flex;align-items:center;gap:6px}
.sw{width:21px;height:21px;border-radius:4px;border:1px solid rgba(0,0,0,.18);flex-shrink:0}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;max-width:1020px;margin:0 auto}
.mo{background:#fff;border-radius:9px;padding:9px;box-shadow:0 1px 5px rgba(0,0,0,.09)}
.mn{text-align:center;font-weight:700;font-size:11px;color:#333;margin-bottom:5px;
    text-transform:uppercase;letter-spacing:.8px}
.dg{display:grid;grid-template-columns:repeat(7,1fr);gap:1.5px}
.dh{text-align:center;font-size:7.5px;font-weight:700;color:#bbb;padding-bottom:2px}
.dg span{text-align:center;font-size:10.5px;padding:3px 0;border-radius:3px;
         font-weight:600;min-height:19px;display:block}
.e{background:transparent!important}
.a{background:#3d9e41;color:#fff}
.b{background:#FFD700;color:#4a3000}
/* Split cells: diagonal gradient — upper-left triangle / lower-right triangle */
/* .ab = Maggy(green) morning → Wesley(yellow) afternoon */
.ab{background:linear-gradient(135deg,#3d9e41 50%,#FFD700 50%);
    color:#fff;text-shadow:0 0 3px rgba(0,0,0,.7)}
/* .ba = Wesley(yellow) morning → Maggy(green) afternoon */
.ba{background:linear-gradient(135deg,#FFD700 50%,#3d9e41 50%);
    color:#222;text-shadow:0 0 3px rgba(255,255,255,.8)}
"""

def render(year, S, splits):
    months_html = ""
    for mo in range(1, 13):
        first  = date(year, mo, 1)
        offset = (first.weekday() + 1) % 7
        dim    = cal_mod.monthrange(year, mo)[1]
        cells  = "".join(f'<span class="dh">{h}</span>' for h in DOW)
        cells += '<span class="e"></span>' * offset
        for day in range(1, dim + 1):
            d = date(year, mo, day)
            if d in splits:
                morn, _ = splits[d]
                cls = "ab" if morn == P1 else "ba"
            else:
                cls = "a" if S[d] == P1 else "b"
            cells += f'<span class="{cls}">{day}</span>'
        months_html += f'<div class="mo"><div class="mn">{MONTH_NAMES[mo-1]}</div><div class="dg">{cells}</div></div>'

    split_swatch = ("linear-gradient(135deg,#3d9e41 50%,#FFD700 50%)")
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{year} Visitation Calendar</title>
<style>{CSS}</style></head>
<body>
<header>
  <h1>{year} Visitation Calendar</h1>
</header>
<div class="leg">
  <div class="li"><div class="sw" style="background:#3d9e41"></div><b>Maggy</b></div>
  <div class="li"><div class="sw" style="background:#FFD700"></div><b>Wesley</b></div>
  <div class="li"><div class="sw" style="background:{split_swatch}"></div><b>Split day</b> (AM → PM)</div>
</div>
<div class="grid">{months_html}</div>
</body></html>"""

out_dir = "/sessions/friendly-tender-brahmagupta/mnt/visitation-calendar"
os.makedirs(out_dir, exist_ok=True)

for year, params in YEAR_DATA.items():
    S, splits = build_schedule(year, **params)
    html = render(year, S, splits)
    with open(f"{out_dir}/visitation_calendar_{year}.html", "w") as f:
        f.write(html)
    print(f"✓ {year}  {'(even)' if year%2==0 else '(odd) '}")

# Quick verification for 2026
print("\n── 2026 key date check ──")
S26, splits26 = build_schedule(2026, **YEAR_DATA[2026])
checks = [
    (date(2026,1,9),  P2, "Jan 9-11 = Wesley (P2) weekend"),
    (date(2026,1,17), P1, "Jan 17-18 = Magdalene (P1) — user confirmed"),
    (date(2026,5,10), P1, "Mother's Day May 10 = Magdalene (P1) always ✓"),
    (date(2026,6,21), P2, "Father's Day Jun 21 = Wesley (P2) always ✓"),
    (date(2026,4,5),  P1, "Easter Apr 5 = Magdalene (P1) even year ✓"),
    (date(2026,11,26),P1, "Thanksgiving Nov 26 = Magdalene (P1) even year ✓"),
    (date(2026,12,25),P2, "Christmas Dec 25 = Wesley (P2) first-half even ✓"),
    (date(2026,12,27),P1, "Christmas Dec 27 = Magdalene (P1) second-half even ✓"),
]
all_ok = True
for d, expected, label in checks:
    got = S26[d]
    ok = "✓" if got == expected else "✗ FAIL"
    print(f"  {ok}  {label}")
    if got != expected: all_ok = False
print(f"\n{'All checks passed!' if all_ok else 'SOME CHECKS FAILED'}")
