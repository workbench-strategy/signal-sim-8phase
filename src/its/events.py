"""Shared event / recommendation types for adapters, policies, and shadow mode."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Recommendation:
    """
    A would-be action produced by a policy or adapter.recommend().

    Shadow mode records these without executing field writes.
    """

    intent: str
    reason: str
    payload: Dict[str, Any] = field(default_factory=dict)
    profile_id: str = ""
    policy_id: str = ""
    confidence: Optional[float] = None
    created_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "reason": self.reason,
            "payload": dict(self.payload),
            "profile_id": self.profile_id,
            "policy_id": self.policy_id,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }
