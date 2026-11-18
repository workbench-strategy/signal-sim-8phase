# Domain: VMS / DMS

- **Standards:** NTCIP 1203, MULTI markup
- **Adapter:** `its.domains.vms_adapter.VmsStubAdapter` (stub)
- **Demo profile:** `profiles/examples/vms_demo.json`

## Intents

| Intent | Mode |
|--------|------|
| get_status | read |
| post_message | write (dry-run default) |

## Expand next

- MULTI validate + font table awareness
- NTCIP 1203 object module under `src/ntcip/mib/objects/`
- Message library as data (agency-approved)
