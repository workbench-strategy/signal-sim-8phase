# Playbook: RWIS weather check

- **Domain:** rwis
- **Profile:** `profiles/examples/rwis_demo.json`
- **Risk:** read-only

## Goal

Pull ESS-style observations through the stub adapter as a template for
weather-responsive ops playbooks.

## Steps (Python sketch)

```python
import asyncio
from pathlib import Path
from its.profile import load_device_profile
from its.domains.rwis_adapter import RwisStubAdapter

async def main():
    profile = load_device_profile(Path("profiles/examples/rwis_demo.json"))
    status = await RwisStubAdapter().get_status(profile)
    print(status.summary, status.data)

asyncio.run(main())
```

## Next innovation idea

- Policy: if `surface_temp_c` below threshold, shadow-recommend a VMS message
  via the VMS adapter (cross-domain orchestration)
