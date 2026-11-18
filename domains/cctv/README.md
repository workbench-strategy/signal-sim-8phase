# Domain: CCTV

- **Standards:** NTCIP 1205 and/or ONVIF / RTSP (vendor-specific)
- **Adapter:** `its.domains.cctv_adapter.CctvStubAdapter` (stub)
- **Demo profile:** `profiles/examples/cctv_demo.json`

## Intents

| Intent | Mode |
|--------|------|
| get_status | read |
| goto_preset | write (dry-run default) |

## Expand next

- ONVIF client behind the adapter
- Tunnel verify playbook (preset + incident note)
- Do not store real RTSP credentials in git
