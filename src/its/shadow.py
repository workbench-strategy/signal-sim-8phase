"""
Shadow bus -- append-only log of would-be actions.

Use this before granting any policy permission to call apply(dry_run=False).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from its.events import Recommendation

logger = logging.getLogger(__name__)


@dataclass
class ShadowBus:
    """In-memory (optionally file-backed) recommendation log."""

    records: List[Recommendation] = field(default_factory=list)
    persist_path: Optional[Path] = None

    def record(self, recommendation: Recommendation) -> Recommendation:
        self.records.append(recommendation)
        logger.info(
            "SHADOW intent=%s profile=%s policy=%s reason=%s",
            recommendation.intent,
            recommendation.profile_id,
            recommendation.policy_id,
            recommendation.reason,
        )
        if self.persist_path is not None:
            self._append_file(recommendation)
        return recommendation

    def record_many(
        self, recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        return [self.record(item) for item in recommendations]

    def clear(self) -> None:
        self.records.clear()

    def to_dicts(self) -> List[dict]:
        return [item.to_dict() for item in self.records]

    def _append_file(self, recommendation: Recommendation) -> None:
        assert self.persist_path is not None
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        with self.persist_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(recommendation.to_dict()) + "\n")
