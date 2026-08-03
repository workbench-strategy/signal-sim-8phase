# NTCIP MIB Modules

Place compiled or source SMI MIB modules here for the Object & MIB layer.

## Expected modules (scaffold)

| File | Standard | Purpose |
|------|----------|---------|
| `NEMA-MIB` / enterprise root | NTCIP 8004 | `1.3.6.1.4.1.1206` |
| `NTCIP1201-MIB` | NTCIP 1201 | Global objects (`unitID`, `unitLocation`, DateAndTime) |
| `NTCIP1202-MIB` | NTCIP 1202 | ASC phase / pattern / detector objects |

## Notes

- The Python registry under `src/ntcip/mib/objects/` ships a **minimal** subset for development.
- Production deployments should load vendor-certified MIB revisions that match the field firmware.
- Do not commit proprietary vendor MIB text if your license forbids redistribution.
