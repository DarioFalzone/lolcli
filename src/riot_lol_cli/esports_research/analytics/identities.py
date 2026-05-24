"""Stable identity helpers for cross-source esports records."""

from __future__ import annotations

import hashlib
import re

_NON_SLUG = re.compile(r"[^a-z0-9]+")


def normalize_token(value: object) -> str:
    text = str(value or "").strip().lower()
    text = _NON_SLUG.sub("-", text)
    return text.strip("-") or "unknown"


def make_stable_id(namespace: str, *parts: object) -> str:
    normalized_parts = [normalize_token(part) for part in parts if str(part or "").strip()]
    base = "-".join(normalized_parts) or "unknown"
    digest = hashlib.sha1(f"{namespace}:{base}".encode()).hexdigest()[:10]
    return f"{normalize_token(namespace)}-{base}-{digest}"
