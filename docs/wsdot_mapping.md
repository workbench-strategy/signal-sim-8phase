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
| [j80.12-00_e.pdf](WSDOT_Std_plans/j80.12-00_e.pdf) | Field output terminal panels (WSDOT FT numbers for phase R/Y/G) |
| [j80.15-00_e.pdf](WSDOT_Std_plans/j80.15-00_e.pdf) | Detector test panel |

Demo wiring in `data/wsdot_8phase.json` maps each phase indication to a placeholder
`OUT-xx` channel and the matching J-80.12 field terminal (for example phase 2 green
= FT 623 on Output File #1 LX).

## Corridor override

Match existing corridor phasing when it differs (DM 1330 item 5).
