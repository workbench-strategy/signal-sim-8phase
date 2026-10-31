# Playbook: 5-minute signal cycle teach tour

- **Domain:** signals
- **Profile:** `data/wsdot_8phase.json` (demo timing + Type 332 wiring)
- **Last field touch:** lab / classroom
- **Risk:** read-only

## Goal

Walk a learner from intersection heads to Type 332 cabinet outputs in one short
demo: rings, barriers, yellow clearance, all-red sync, and energized field
terminals from WSDOT J-80.12.

## Preconditions

- Repo checked out
- Python 3 with project deps (`pip install -r requirements.txt`)
- Browser available to open the exported HTML

## Steps

1. Export the teach-mode animation (lead/lead plan):

```bash
python src/cli/main.py animate2d --output /tmp/signal-teach.html --plan lead-lead
```

2. Open `/tmp/signal-teach.html` in a browser.

3. Narrate while it plays (about 5 minutes of wall clock with default presentation speed):
   - Intersection heads change color from the dual-ring timing plan.
   - Ped overlays show Walk / FDW / Don't Walk on even through phases (J-80.12 ped FTs).
   - Teach panel names the concept (protected lefts, throughs + Walk, yellow + FDW, all-red).
   - Type 332 rack highlights Controller, Output File #1 LX, Conflict Monitor, and Detector Test Panel.
   - Energized list shows `OUT-xx` / `PED-xx` plus J-80.12 field terminals (Ph2 green = FT 623; Ph2 Walk = FT 722).

4. Detector Test Panel (J-80.15) demo:
   - When major throughs are green (Ph2 + Ph6), flip **DET. 2** or **DET. 6** to Test.
   - Status should read extending green (presentation) and Input File / Detector Test light on the rack.
   - Flip a detector while its phase is red to show call latched / waiting.

5. When playback auto-pauses at all-red / barrier sync:
   - Ask the checkpoint question on screen.
   - Point at Conflict Monitor + Output File #1 LX on the rack diagram.
   - Click **Resume after checkpoint**.

6. Optional compare plan:

```bash
python src/cli/main.py animate2d --output /tmp/signal-teach-lag.html --plan lead-lag
```

Open both tabs and contrast lead/lead concurrent pairs vs lead/lag approach pairs.

7. Optional terminal companion (same controller truth):

```bash
python src/cli/main.py wiring-summary
python src/cli/main.py run --interval 0.5
```

## Expected result

- Learner can state: rings 1-4 / 5-8, barriers at 2|3 and 6|7, and that field wires
  are switched in Output File #1 LX (not inside the 2070 CPU board).
- Auto-pause occurs after yellow clearance when all-red begins.
- Presentation-speed sliders change on-screen tempo only; ASC step seconds in the
  exported frames stay fixed.

## Captures / tests

- `tests/display/test_teach.py`
- `tests/display/test_two_d.py`
- Standard plans: `docs/WSDOT_Std_plans/j80.10-01_e.pdf`, `j80.12-00_e.pdf`, `j80.15-00_e.pdf`

## Gotchas

- First frames may be red dwell before the first green; that is startup state, not a barrier crossing.
- `OUT-01..OUT-24` are demo channel ids; WSDOT field terminal numbers are the durable labels.
- Plan dropdown reloads `?plan=`; regenerate HTML if your static file host ignores query params.

## Next innovation idea (optional)

- Light a physical Type 332 mock (LEDs on a breadboard or Pi GPIO) from the same
  energized-output list the teach panel already emits.
