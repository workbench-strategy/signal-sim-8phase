"""
Device profile model -- sanitized packs that replicate field reality.

Profiles are data, not code. Store YAML/JSON under ``profiles/`` with no
secrets (no communities, passwords, badge data, or prod API keys).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


@dataclass(frozen=True)
class DeviceProfile:
    """Sanitized description of a field (or lab) device / site asset."""

    profile_id: str
    domain: str
    display_name: str
    protocol: str
    endpoint: str
    identity: str = ""
    capabilities: tuple = ()
    mib_or_api_revision: str = ""
    notes: str = ""
    quirks: tuple = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities


def device_profile_from_dict(data: Mapping[str, Any]) -> DeviceProfile:
    """Build a :class:`DeviceProfile` from a mapping (YAML/JSON object)."""
    required = ("profile_id", "domain", "display_name", "protocol", "endpoint")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"profile missing required fields: {missing}")

    capabilities = tuple(data.get("capabilities") or ())
    quirks = tuple(data.get("quirks") or ())
    metadata = dict(data.get("metadata") or {})
    return DeviceProfile(
        profile_id=str(data["profile_id"]),
        domain=str(data["domain"]).lower(),
        display_name=str(data["display_name"]),
        protocol=str(data["protocol"]).lower(),
        endpoint=str(data["endpoint"]),
        identity=str(data.get("identity") or ""),
        capabilities=capabilities,
        mib_or_api_revision=str(data.get("mib_or_api_revision") or ""),
        notes=str(data.get("notes") or ""),
        quirks=quirks,
        metadata=metadata,
    )


def load_device_profile(path: Path) -> DeviceProfile:
    """
    Load a profile from JSON or YAML.

    YAML requires PyYAML; JSON always works with the stdlib.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(text)
    elif suffix in (".yaml", ".yml"):
        data = _load_yaml(text, path)
    else:
        # Prefer JSON; attempt YAML as fallback for extensionless files.
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = _load_yaml(text, path)
    if not isinstance(data, dict):
        raise ValueError(f"profile root must be a mapping: {path}")
    return device_profile_from_dict(data)


def _load_yaml(text: str, path: Path) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            f"PyYAML is required to load {path}. Use .json or pip install pyyaml."
        ) from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"YAML profile root must be a mapping: {path}")
    return data


def list_profile_paths(root: Path) -> List[Path]:
    """Return profile file paths under ``root`` (json/yaml)."""
    root = Path(root)
    if not root.exists():
        return []
    paths: List[Path] = []
    for pattern in ("*.json", "*.yaml", "*.yml"):
        paths.extend(sorted(root.rglob(pattern)))
    return paths
