"""
Domain adapter contract.

Each asset class (signals, VMS, RWIS, CCTV, ...) implements this shape.
Protocol drivers (NTCIP, ONVIF, HTTP) stay behind the adapter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from its.events import Recommendation
from its.profile import DeviceProfile


@dataclass(frozen=True)
class DomainHealth:
    ok: bool
    detail: str = ""
    latency_ms: Optional[float] = None


@dataclass(frozen=True)
class DomainStatus:
    """Opaque-but-typed status bag returned by get_status()."""

    domain: str
    profile_id: str
    summary: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ApplyResult:
    success: bool
    dry_run: bool
    detail: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class DomainAdapter(Protocol):
    """
    Per-domain facade used by playbooks and policies.

    ``apply`` defaults to dry-run semantics at the call site; implementations
    must refuse live writes unless ``dry_run=False`` and credentials exist.
    """

    domain: str

    async def probe(self, profile: DeviceProfile) -> DomainHealth:
        """Cheap connectivity / identity check."""

    async def get_status(self, profile: DeviceProfile) -> DomainStatus:
        """Read current operational status (no side effects)."""

    async def recommend(
        self, profile: DeviceProfile, intent: str, **params: Any
    ) -> Recommendation:
        """Build a recommendation for ``intent`` without executing it."""

    async def apply(
        self,
        profile: DeviceProfile,
        intent: str,
        *,
        dry_run: bool = True,
        **params: Any,
    ) -> ApplyResult:
        """
        Execute or simulate an intent.

        Production callers must pass dry_run=True unless ops approved a write.
        """
