"""Storage-layout validator for Capability 3 (Reference Pack) -- spec AC3.2.

Asserts that no exemplar record with ``license_category == "all-rights-
reserved"`` (nor, more generally, any license category outside
``schema.LOCAL_MEDIA_PERMITTED_LICENSES``) has an associated locally-stored
media file, either via its own ``local_media_path`` field or via a stray file
sitting under the pack's ``media/`` directory with a matching filename stem.

This module never downloads, scans the network, or writes media files -- it
only inspects JSON records already on disk plus the (normally near-empty)
``media/`` directory's file listing, per the spec's explicit "no automated
scraping or bulk downloading" scope constraint.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from drone_video_ai.reference_pack.schema import check_local_media_storage_rule

# Files that are expected/allowed to sit in media/ without being a real
# media asset for any exemplar (e.g. the placeholder that keeps an otherwise
# empty, gitignored directory tracked in git).
_IGNORED_MEDIA_FILENAMES = {".gitkeep", ".DS_Store"}


class StorageLayoutError(ValueError):
    """Raised when one or more exemplar records violate the storage-layout
    rule. ``violations`` holds every individual failure message found."""

    def __init__(self, violations: List[str]):
        self.violations = violations
        super().__init__("; ".join(violations))


def _load_exemplar_records(exemplars_dir: Path) -> List[tuple]:
    """Return ``(exemplar_id, doc)`` pairs for every ``*.json`` file in
    ``exemplars_dir``. ``exemplar_id`` is the file's stem, used as the
    canonical identifier a locally-stored media file would be named after."""
    records = []
    if not exemplars_dir.exists():
        return records
    for path in sorted(exemplars_dir.glob("*.json")):
        doc = json.loads(path.read_text())
        records.append((path.stem, doc))
    return records


def _media_filenames(media_dir: Path) -> List[str]:
    if not media_dir.exists():
        return []
    return [p.name for p in media_dir.iterdir() if p.is_file() and p.name not in _IGNORED_MEDIA_FILENAMES]


def find_storage_layout_violations(exemplars_dir: Path, media_dir: Path) -> List[str]:
    """Return a list of human-readable violation messages (empty list ==
    layout is clean). Pure/read-only: does not raise, does not modify
    anything on disk."""
    violations: List[str] = []
    media_files = _media_filenames(media_dir)
    media_stems = {Path(name).stem for name in media_files}

    for exemplar_id, doc in _load_exemplar_records(exemplars_dir):
        field_violation = check_local_media_storage_rule(doc)
        if field_violation is not None:
            violations.append(f"{exemplar_id}.json: {field_violation}")

        license_category = doc.get("license_category")
        if license_category == "all-rights-reserved" and exemplar_id in media_stems:
            violations.append(
                f"{exemplar_id}.json: license_category='all-rights-reserved' but a "
                f"matching file exists under {media_dir} (stray media for an "
                f"all-rights-reserved exemplar)"
            )

    return violations


def validate_storage_layout(exemplars_dir: Path, media_dir: Path) -> None:
    """Raise :class:`StorageLayoutError` if any exemplar under
    ``exemplars_dir`` violates the storage-layout rule against ``media_dir``;
    otherwise return ``None``."""
    violations = find_storage_layout_violations(Path(exemplars_dir), Path(media_dir))
    if violations:
        raise StorageLayoutError(violations)
