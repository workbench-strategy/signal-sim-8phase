# Device Profiles

Sanitized packs that describe real (or lab) assets so you can **replicate**
field reality without committing secrets.

## Rules

- No community strings, passwords, USM keys, badge IDs, or prod API tokens
- Prefer site codes and RFC 5737 documentation IPs (`192.0.2.0/24`)
- Pin `mib_or_api_revision` when known
- One file per device or logical site asset

## Layout

```
profiles/
  examples/           # committed demos
  <corridor_or_agency>/   # your sanitized packs (local or committed)
```

## Schema (JSON or YAML)

See `examples/signals_demo.json` for the canonical fields consumed by
`its.profile.DeviceProfile`.
