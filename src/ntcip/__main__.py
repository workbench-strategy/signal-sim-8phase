"""
Usage example: NTCIP Manager asynchronously GETs ASC phase status.

Run::

    python -m ntcip
    # or
    python src/ntcip/__main__.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Allow `python src/ntcip/__main__.py` without installing the package.
_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ntcip.exceptions import (  # noqa: E402
    NtcipError,
    OidMismatchError,
    SnmpAuthenticationError,
    SnmpTimeoutError,
)
from ntcip.factory import create_ntcip_manager  # noqa: E402
from ntcip.protocol.models import SnmpCredentials  # noqa: E402


async def run_phase_status_demo(host: str = "192.0.2.10") -> int:
    """
    Business-layer demo: async GET of phase status from a field controller.

    Uses the stub SNMP backend with seeded NTCIP 1202 values so the example
    runs offline. Swap ``use_pysnmp=True`` (and implement the backend) to
    talk to a real cabinet.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    log = logging.getLogger("ntcip.demo")

    credentials = SnmpCredentials(community="public")
    manager = create_ntcip_manager(credentials=credentials, demo_data=True)

    try:
        log.info("Requesting phase status from controller %s ...", host)
        snapshot = await manager.get_phase_status(
            host,
            timeout_seconds=2.0,
        )
        summary = snapshot.summary()
        log.info("Typed response received from %s", snapshot.host)
        log.info("Green phases : %s", snapshot.green_phases())
        log.info("Phase map    : %s", summary)

        identity = await manager.get_unit_identity(host)
        log.info(
            "Unit identity : id=%s location=%s",
            identity.unit_id,
            identity.unit_location,
        )
        return 0
    except SnmpTimeoutError as exc:
        log.error("Network timeout: %s", exc)
        return 2
    except SnmpAuthenticationError as exc:
        log.error("SNMP authentication failure: %s", exc)
        return 3
    except OidMismatchError as exc:
        log.error("OID / ASN.1 mismatch: %s", exc)
        return 4
    except NtcipError as exc:
        log.error("NTCIP error: %s", exc)
        return 1
    finally:
        await manager.close()


def main() -> None:
    raise SystemExit(asyncio.run(run_phase_status_demo()))


if __name__ == "__main__":
    main()
