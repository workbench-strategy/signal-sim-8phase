# Playbook: VMS message in shadow mode

- **Domain:** vms
- **Profile:** `profiles/examples/vms_demo.json`
- **Risk:** shadow / dry-run

## Goal

Practice traveler-information messaging without touching a sign.

## Steps (Python sketch)

```python
import asyncio
from pathlib import Path
from its.profile import load_device_profile
from its.domains.vms_adapter import VmsStubAdapter
from its.shadow import ShadowBus

async def main():
    profile = load_device_profile(Path("profiles/examples/vms_demo.json"))
    adapter = VmsStubAdapter()
    shadow = ShadowBus()
    status = await adapter.get_status(profile)
    print(status.summary)
    rec = await adapter.recommend(profile, "post_message", message="ICE AHEAD")
    shadow.record(rec)
    result = await adapter.apply(profile, "post_message", message="ICE AHEAD", dry_run=True)
    print(result)

asyncio.run(main())
```

## Expected result

Dry-run apply succeeds; stub message unchanged unless `dry_run=False` (still in-memory only).

## Gotchas

- Real DMS needs NTCIP 1203 MULTI encoding and often font/graphics checks
- Never commit real message libraries that contain sensitive detour details if agency policy forbids it
