"""Structural ticket-tree layout detectors (no Store I/O)."""

from __future__ import annotations

import tomllib
from pathlib import Path

_INVALID_MODE_MARKERS = frozenset(
    {
        "stories.yaml",
        "sprint-status.yaml",
        "epics.md",
    }
)

_INITIATIVE_PREFIX = "initiative-"


def detect_invalid_mode(root: Path) -> bool:
    """True if root's top level has any sprint/stories.yaml-mode marker."""
    return any((root / name).is_file() for name in _INVALID_MODE_MARKERS)


def is_in_floor(root: Path) -> bool:
    """True if at least one top-level initiative-<slug>/ meets the Method floor."""
    try:
        entries = list(root.iterdir())
    except OSError:
        return False

    for entry in entries:
        if not entry.is_dir():
            continue
        name = entry.name
        if not name.startswith(_INITIATIVE_PREFIX):
            continue
        slug = name[len(_INITIATIVE_PREFIX) :]
        if not slug or not _initiative_is_in_floor(entry, slug):
            continue
        return True
    return False


def _initiative_is_in_floor(initiative_dir: Path, slug: str) -> bool:
    """Require initiative-<slug>.md and a valid tickets/tickets.toml + epic dirs."""
    if not (initiative_dir / f"initiative-{slug}.md").is_file():
        return False

    tickets_toml = initiative_dir / "tickets" / "tickets.toml"
    if not tickets_toml.is_file():
        return False

    try:
        raw = tickets_toml.read_bytes()
        data = tomllib.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return False

    epics = data.get("epic")
    if not isinstance(epics, list) or not epics:
        return False

    for epic in epics:
        if not isinstance(epic, dict):
            return False
        epic_slug = epic.get("slug")
        if not isinstance(epic_slug, str) or not epic_slug.strip():
            return False
        # Single path segment only — reject ., .., separators, absolute paths.
        if epic_slug in {".", ".."} or Path(epic_slug).name != epic_slug:
            return False
        epic_dir = initiative_dir / "tickets" / epic_slug
        if not epic_dir.is_dir() or epic_dir.name != epic_slug:
            return False
    return True
