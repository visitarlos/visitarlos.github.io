# Visitation Calendar — Agent Handoff Documentation

**Case:** Elliott v. Johnson — Case No. 04 DR 2018-748-6
**Court:** Benton County Circuit Court, Domestic Relations Division, Arkansas
**Order date:** November 13, 2023
**School district:** Bentonville, AR (Rogers School District area)

---

## What this project is

This folder contains color-coded annual visitation calendars (HTML files, open in any browser) generated from the court's Standard Visitation Schedule. The script `calendar_gen.py` produces one calendar per year and can be re-run whenever school calendar data is updated or a new year needs to be added.

To regenerate all calendars: `python3 calendar_gen.py`

---

## The parties

| Role in script | Person | Role in case | Color |
|---|---|---|---|
| **P1** | Magdalene Johnson | Defendant / primary custodian / mother | Green |
| **P2** | Wesley Elliott | Plaintiff / noncustodial / father | Yellow |

**Critical:** P1 = mother is confirmed by the fact that the Standard Visitation Schedule assigns Mother's Day to "Parent 1" always, and Father's Day to "Parent 2" always. Do not swap these.

---

## Regular (non-holiday) schedule

- **Default:** All days belong to P1 (Magdalene). She has primary custody.
- **Every Thursday:** P2 (Wesley) has midweek visitation — after school (≈3:30 pm) through Friday morning (≈7:30 am school start). Per the order, Thursday is the designated midweek day.
- **Alternating weekends:** P2 (Wesley) gets every other weekend — Friday after school through Sunday night. Children return to school Monday morning.

### Alternating weekend anchor

The alternating weekend pattern is anchored to `FIRST_P2_FRIDAY = date(2024, 1, 12)` — the first Friday in January 2024 when Wesley's standard-schedule weekends began (the order transitioned to Standard Visitation Schedule in January 2024). The 14-day cycle from this date determines every Wesley weekend going forward.

**Confirmed anchor:** The children were with Magdalene on January 17–18, 2026 (user-verified). This means January 16, 2026 was **not** a Wesley Friday, which is consistent with `FIRST_P2_FRIDAY = 2024-01-12` (delta = 735 days; 735 / 14 = 52.5 → not a P2 Friday ✓). January 9, 2026 was Wesley's weekend (delta = 728 days; 728 / 14 = 52 ✓).

---

## Holiday schedule

Holidays are governed by the Benton County **Suggested Standard Visitation Guideline** (effective January 4, 2021), attached as Exhibit 1 to the order. Holidays alternate by odd/even year. **2026 is an even year.**

| Holiday | Even years | Odd years | Notes |
|---|---|---|---|
| Spring Break | P2 (Wesley) | P1 (Magdalene) | School-calendar dependent; starts last school Friday before break, ends Sunday after break |
| Easter Weekend | P1 (Magdalene) | P2 (Wesley) | Fri–Sun; computed algorithmically |
| Mother's Day Weekend | **Always P1** (Magdalene) | **Always P1** | Fri–Sun |
| Memorial Day | P2 (Wesley) | P1 (Magdalene) | Fri–Mon (Mon = holiday); last Monday of May |
| Father's Day Weekend | **Always P2** (Wesley) | **Always P2** | Fri–Sun |
| Independence Day | P1 (Magdalene) | P2 (Wesley) | July 4 overnight only (ends 7:30 am July 5) |
| Summer visitation | **Always P2** (Wesley) | **Always P2** | 5 weeks: Jul 5 (10 am) – Aug 8; see below |
| Labor Day | P2 (Wesley) | P1 (Magdalene) | Fri–Mon; first Monday of September |
| Halloween | P2 (Wesley) | P1 (Magdalene) | Oct 31 + overnight (Nov 1) |
| Thanksgiving | P1 (Magdalene) | P2 (Wesley) | Starts last school Friday before break, ends Sunday after break |
| Christmas (start → Dec 26) | P2 (Wesley) | P1 (Magdalene) | Starts last school day before winter break |
| Christmas (Dec 27 → year end) | P1 (Magdalene) | P2 (Wesley) | P1/P2 flips at 10:00 am Dec 27 |
| Children's birthdays | P1 (Magdalene) | P2 (Wesley) | S.E.: January 6; D.E.: November 22 |

### Summer visitation detail

Summer visitation runs in two phases, both beginning when school lets out for the year:

**Phase 1 — School end through July 4:** Magdalene (P1, custodial) has primary custody. Wesley (P2) receives Thursday midweek visits only. There is no alternating weekend rotation during this phase. The script applies this by resetting all non-Thursday days in this window to P1 after the regular schedule is built.

**Phase 2 — July 5 (10:00 am) through August 8:** Wesley (P2, noncustodial) has 5 consecutive weeks of primary custody. Magdalene (P1) receives Thursday midweek visits only. There is no alternating weekend rotation during this phase either. The script marks the full Jul 5–Aug 8 block as P2, then restores Thursdays to P1.

The `school_last_day` parameter in `YEAR_DATA` drives Phase 1. Holiday overrides (Memorial Day, Father's Day, Independence Day) are applied on top of the phase 1 reset and will take precedence as usual.

### Christmas carry-over into January

The Christmas holiday straddles two calendar years. The script accepts a `prev_xmas_school_return` parameter for each year, which is the **first day students return to school** after the winter break. Days from January 1 through the day before that date are assigned to whichever parent had the Dec 27+ portion of the **previous** year's Christmas holiday (odd previous year → P2/Wesley; even previous year → P1/Magdalene).

---

## Children's birthdays

- **S.E.** — January 6 (born approx. 2012; was age 11 at time of order)
- **D.E.** — November 22 (born approx. 2014; was age 9 at time of order)

In even years both birthdays go to P1 (Magdalene); in odd years to P2 (Wesley). The birthday override applies to the single calendar day only — it does not expand the surrounding weekend.

---

## School calendar data (what the script needs per year)

The script requires five pieces of data per calendar year, all sourced from the **Bentonville Schools official calendar**:

| Parameter | What it is | Where to find it |
|---|---|---|
| `spring_break` | `(first_no_school_day, last_no_school_day)` — the Monday–Friday of spring break | School calendar; look for "Spring Break" block |
| `thanksgiving_break` | `(first_no_school_day, last_no_school_day)` — the Monday–Friday of Thanksgiving break | School calendar; look for "Thanksgiving Break" block |
| `xmas_last_schoolday` | Last day students are in school before winter break | School calendar; look for "Student Last Day" or "Last Day" in December |
| `school_last_day` | Last day of school before summer break | School calendar; look for "Last Day of School" or "Student Last Day" in May/June |
| `prev_xmas_school_return` | First day students return from the **previous** year's winter break | School calendar for the year being generated; look for first Monday in January with school in session |

The script computes visitation start/end times automatically: it walks back to the preceding Friday for break starts, and forward to the following Sunday for break ends.

### Confirmed vs. estimated data

| Year | Spring Break | Thanksgiving | Xmas last day | School last day | Jan return | Source |
|---|---|---|---|---|---|---|
| 2026 | Mar 23–27 ✓ | Nov 23–27 ✓ | Dec 18 ✓ | May 22 est. | Jan 5 ✓ | 2025-26 & 2026-27 official calendars + user |
| 2027 | Mar 22–26 ✓ | Nov 22–26 est. | Dec 17 est. | May 21 ✓ | Jan 4 ✓ | 2026-27 official calendar (spring, school last day, Jan return confirmed) |
| 2028 | Mar 20–24 est. | Nov 20–24 est. | Dec 15 est. | May 23 est. | Jan 3 est. | Estimated |
| 2029 | Mar 25–29 est. | Nov 25–29 est. | Dec 19 est. | May 22 est. | Jan 2 est. | Estimated |
| 2030 | Mar 18–22 est. | Nov 25–29 est. | Dec 20 est. | May 21 est. | Jan 6 est. | Estimated |
| 2031 | Mar 24–28 est. | Nov 24–28 est. | Dec 19 est. | May 20 est. | Jan 5 est. | Estimated |

---

## How to add or update a year

1. Obtain the official Bentonville Schools calendar PDF for the relevant school year (e.g., the 2027-2028 calendar covers Thanksgiving 2027, Christmas 2027, the January 2028 return, and Spring Break 2028).
2. Extract the five parameters listed above (spring break, thanksgiving break, xmas last school day, school last day, and January return).
3. Update the `YEAR_DATA` dict in `calendar_gen.py`, replacing estimated dates with confirmed ones and updating the source comment.
4. If adding a new year beyond 2031, append a new entry to `YEAR_DATA` following the same pattern.
5. Run `python3 calendar_gen.py` from this folder. The script overwrites existing HTML files and saves an updated copy of itself.

**One school year calendar covers two calendar years of data:**
- The **N / N+1** school calendar confirms: Thanksgiving break year N, Christmas last school day year N, January return year N+1, Spring Break year N+1.

---

## Key design decisions (for future reference)

- **Day coloring** reflects majority custody for that calendar day. Exchange days (typically Monday mornings) are colored for the receiving parent since they have the child for most of the day.
- **Holiday precedence:** Holidays override the regular alternating weekend / Thursday schedule. A holiday override is applied after the regular schedule, so it always wins.
- **Summer during P2's block:** During Wesley's 5-week summer period, Magdalene's alternating weekends and Thursdays are explicitly re-applied inside the summer loop (the schedule document says summer IS subject to alternating weekend and midweek visitation by the custodial parent).
- **Halloween:** In 2026, Oct 30 is a Wesley (P2) Friday under the regular schedule. The Halloween override gives Oct 31–Nov 1 to Magdalene (P1, odd year... wait — 2026 even year → P2 gets Halloween). So Wesley gets Oct 31–Nov 1 in 2026, and Oct 30 (his regular Friday) as well. In 2027 (odd), Magdalene gets Halloween.
- **Christmas Dec 27:** The order specifies the handoff occurs at 10:00 am on December 27. The script assigns the whole day of Dec 27 to the receiving parent since they have the majority of the day.

---

## Output files

| File | Description |
|---|---|
| `calendar_gen.py` | The generator script. Run with `python3 calendar_gen.py`. Requires Python 3.6+ standard library only. |
| `visitation_calendar_YYYY.html` | Self-contained calendar for year YYYY. Open in any browser. |
| `2026-2027_Calendar.pdf` | Official Bentonville Schools calendar used as source data. |
| `AGENTS.md` | This file. |
