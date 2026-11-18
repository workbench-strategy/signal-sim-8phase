# Domain: Data stations

- **Typical interfaces:** TMDD, agency archive APIs, sometimes NTCIP
- **Adapter:** not scaffolded yet -- add `DataStationStubAdapter` when you
  have a feed you can sanitize

## Intents (planned)

| Intent | Mode |
|--------|------|
| get_volume_speed | read |
| get_station_metadata | read |

## Expand next

- One JSON capture of a station metadata response
- Performance-measure notebook under `notebooks/` linked from a playbook
