# Roadmap -- Next Steps

Ordered for a working ITS engineer: maximize learning per hour, keep field risk low.

## Now (foundation -- largely in place)

- [x] NTCIP layered Manager scaffold (`src/ntcip/`)
- [x] ASC phase status demo + DateAndTime codec
- [x] Shared ITS platform seams (`src/its/`)
- [x] Strategy docs (`START_HERE.md`, this roadmap)
- [x] Example profile + playbooks + domain stubs

## Next (high value)

1. **Second NTCIP domain (pick one you touch most): VMS or RWIS**
   - Stub adapter + demo profile
   - One real read playbook from your work
   - Optional: snmpsim fixture

2. **Wire `PysnmpBackend`**
   - Real GET/SET against snmpsim, then staging
   - Config via env: host, community/USM, timeout

3. **Shadow workflow end-to-end**
   - One policy that reads ASC (or VMS) status and logs a recommendation
   - CLI: `python -m its.shadow_demo`

4. **CCTV adapter seam**
   - ONVIF or vendor stub: list presets / get status
   - Enables tunnel verify + future airport video learning

## Then (replicate at scale)

5. Profile pack for a real corridor (sanitized)
6. Capture library + replay tests
7. Conformance flags on profiles (RO/RW object lists)
8. Timing / VMS message transactional SET path (NTCIP DB transactions where required)

## Later (innovate + crossover)

9. Hook GIS / layout CLI to live or stub adapter snapshots
10. Tunnel scenario playbooks (CCTV + VMS + data station)
11. Agent SIL for signal sim
12. `airport_lab` mock access-control + video workflow (synthetic only)

## Explicit non-goals (for now)

- Building a full ATMS UI
- Supporting every vendor MIB on day one
- Autonomous field writes
- Production airport security integration
