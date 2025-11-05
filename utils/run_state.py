"""Helpers for tracking daily TLDR dispatch state."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class RunStateStore:
    """Lightweight JSON-backed store for recording completed runs."""

    path: Path

    def has_run_for(self, target_date: date) -> bool:
        """Return True if a successful run already occurred for ``target_date``."""
        state = self._read_state()
        return bool(state.get("dates", {}).get(target_date.isoformat()))

    def mark_run(self, target_date: date) -> None:
        """Persist that a run for ``target_date`` completed successfully."""
        state = self._read_state()
        dates: Dict[str, bool] = state.setdefault("dates", {})
        dates[target_date.isoformat()] = True
        self._write_state(state)

    # Internal helpers -------------------------------------------------
    def _read_state(self) -> Dict[str, Dict[str, bool]]:
        if not self.path.exists():
            return {}

        try:
            with self.path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            # Corrupted or unreadable state – treat as empty to avoid crashes.
            return {}

    def _write_state(self, state: Dict[str, Dict[str, bool]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")

        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)

        tmp_path.replace(self.path)
