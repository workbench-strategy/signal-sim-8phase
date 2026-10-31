# WSDOT standard plan traceability

Primary reference: [1330.pdf](1330.pdf) (Design Manual M 22-01 Chapter 1330).

Configuration: [data/wsdot_8phase.json](../data/wsdot_8phase.json)

## Phase sum rules (WSDOT numbering)

On each **approach**, the through phase number plus the left-turn phase number equals a fixed total:

| Street role | Sum | Example |
|-------------|-----|---------|
| Major | **7** | NB: 2 + 5 = 7, SB: 6 + 1 = 7 |
| Minor | **11** | WB: 4 + 7 = 11, EB: 8 + 3 = 11 |

## Phase table (NS major, phase 2 = NB through)

| Phase | Movement | Pair |
|-------|----------|------|
| 2 | NB through | with 5 |
| 5 | NB protected left | 2+5=7 |
| 6 | SB through | with 1 |
| 1 | SB protected left | 6+1=7 |
| 4 | WB through | with 7 |
| 7 | WB protected left | 4+7=11 |
| 8 | EB through | with 3 |
| 3 | EB protected left | 8+3=11 |

## Preemption / overlap channels (same pairs)

| Channel | Phases | Sum |
|---------|--------|-----|
| A | 2 + 5 | 7 (NB) |
| C | 1 + 6 | 7 (SB) |
| B | 4 + 7 | 11 (WB) |
| D | 3 + 8 | 11 (EB) |

Protected/permissive left displays use the through phase for the ball indications and the left phase for the arrow (see DM 1330 item 9; example 61/11 for phases 1 and 6 on SB).

## Cabinet standard plans

| File | Content |
|------|---------|
| [j80.10-01_e.pdf](WSDOT_Std_plans/j80.10-01_e.pdf) | Type 332 signal cabinet layout (2070, input/output files, PDA, conflict monitor) |
| [j80.12-00_e.pdf](WSDOT_Std_plans/j80.12-00_e.pdf) | Field output terminal panels (WSDOT FT numbers for phase R/Y/G + peds/overlaps) |
| [j80.15-00_e.pdf](WSDOT_Std_plans/j80.15-00_e.pdf) | Detector test panel (Type 332) |

Demo wiring in `data/wsdot_8phase.json` maps each phase indication to a placeholder
`OUT-xx` channel and the matching J-80.12 field terminal (for example phase 2 green
= FT 623 on Output File #1 LX / LXW).

### J-80.12 Output File #1 LXW -- vehicle phase field terminals

Pattern: phase `N` uses `6N1` red, `6N2` yellow, `6N3` green.

| Phase | Red | Yellow | Green | Terminal block |
|-------|-----|--------|-------|----------------|
| 1 | 611 | 612 | 613 | FT3 |
| 2 | 621 | 622 | 623 | FT3 |
| 3 | 631 | 632 | 633 | FT2 |
| 4 | 641 | 642 | 643 | FT1 |
| 5 | 651 | 652 | 653 | FT3 |
| 6 | 661 | 662 | 663 | FT3 |
| 7 | 671 | 672 | 673 | FT2 |
| 8 | 681 | 682 | 683 | FT1 |

OCR note on the scanned PDF: some glyphs read as `SR`/`SY`/`SPY` or repeat `6R`; corrected functions above match the `6N1/6N2/6N3` WSDOT numbering and Caltrans cross-ref columns.

### J-80.12 Output File #1 LXW -- pedestrian overlaps (even phases)

| Movement | Red | Yellow | Green |
|----------|-----|--------|-------|
| Phase 2 ped | 721 (2PR) | (no WSDOT label) 2PY | 722 (2PG) |
| Phase 4 ped | 741 (4PR) | (no WSDOT label) 4PY | 742 (4PG) |
| Phase 6 ped | 761 (6PR) | (no WSDOT label) 6PY | 762 (6PG) |
| Phase 8 ped | 781 (8PR) | (no WSDOT label) 8PY | 782 (8PG) |

Not yet modeled in the 8-phase vehicle demo; useful for a future walk/clearance teach layer.

### J-80.12 Output File #2 LXW (Model #420) -- optional overlaps

Present only when specified (see J-80.10 Note 5). WSDOT labels on FT4-FT6:

| Group | Red | Yellow | Green |
|-------|-----|--------|-------|
| OLD | 601 | 602 | 603 |
| OLA | 6A1 | 6A2 | 6A3 |
| OLB | 6B1 | 6B2 | 6B3 |
| OLC | 6C1 | 6C2 | 6C3 |

### J-80.15 Detector Test Panel -- teach hooks

Sits above the 2070 on the Type 332 rack (J-80.10 Note 3). Three-position test switches
(OFF spring-return to Normal; Test momentary) per Spec 9-29.13(10).

Observed DD50 / input-file channel highlights from the plan:

| Detector / call | Connect path (plan) | Teaching use |
|-----------------|---------------------|--------------|
| DET. 1, 3, 5 | I-1F, I-2F, I-3F | Odd-phase vehicle calls into Input File I |
| DET. 2 | I-1W | Even-side / paired call |
| DET. 9 | I-5F | Extended detector set |
| DET. 4, 6, 15, 16, 25, 26, 30, 33, 34 | listed on plan pins | Corridor-specific; keep as profile data |
| Ped Ø2 / Ø4 / Ø6 / Ø8 | dedicated pins | Pair with J-80.12 ped FT numbers above |

Connectors DT3S/DT3P/DT4S/DT4P are D-Sub DD50; `S` = socket, `P` = plug. Panel can be
wired in-line between Detector Termination Interface Panel and Input File(s), or bypassed.

## Corridor override

Match existing corridor phasing when it differs (DM 1330 item 5).
