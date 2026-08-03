"""In-process registry of domain adapters keyed by domain name."""

from __future__ import annotations

from typing import Dict, Optional

from its.adapters import DomainAdapter


class AdapterRegistry:
    """Simple composition helper for playbooks and demos."""

    def __init__(self) -> None:
        self._adapters: Dict[str, DomainAdapter] = {}

    def register(self, adapter: DomainAdapter) -> None:
        domain = adapter.domain.lower()
        self._adapters[domain] = adapter

    def get(self, domain: str) -> DomainAdapter:
        key = domain.lower()
        try:
            return self._adapters[key]
        except KeyError as exc:
            known = ", ".join(sorted(self._adapters)) or "(none)"
            raise KeyError(
                f"no adapter registered for domain={domain!r}; known={known}"
            ) from exc

    def get_optional(self, domain: str) -> Optional[DomainAdapter]:
        return self._adapters.get(domain.lower())

    def domains(self) -> tuple:
        return tuple(sorted(self._adapters))
