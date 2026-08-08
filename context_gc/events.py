# context_gc/events.py
"""Event schema definitions and validation utilities.

Each event is represented as a ``dict`` with at least the following keys:

- ``id`` (str): Unique identifier for the node.
- ``type`` (str): One of ``set_var``, ``tool_call``, ``tool_result``, ``abandon``, ``decision``.
- ``timestamp`` (int): Millisecond‑precision timestamp; lower values are earlier.
- ``parent_id`` (str | None): Identifier of the logical predecessor (used for sequence edges).
- ``content`` (str | None): Human‑readable content for ``decision`` events.
- ``ref_to`` (list[str] | None): For ``abandon`` events, a list of node IDs that are being abandoned.
- Additional fields depend on ``type``.

The library does **not** perform any I/O or external calls; it merely validates the
structure of events supplied by the caller.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Allowed enumeration values
# ---------------------------------------------------------------------------
EVENT_TYPES = {"set_var", "tool_call", "tool_result", "abandon", "decision"}
EVENT_STATUS = {"success", "error", None}

# ---------------------------------------------------------------------------
# Required fields per event type (excluding optional generic fields)
# ---------------------------------------------------------------------------
_REQUIRED_FIELDS = {
    "set_var": ["id", "type", "timestamp", "key", "value"],
    "tool_call": ["id", "type", "timestamp", "tool_name", "arguments"],
    "tool_result": ["id", "type", "timestamp", "call_id", "result"],
    "abandon": ["id", "type", "timestamp", "ref_to"],
    "decision": ["id", "type", "timestamp", "content"],
}


def _require(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError(msg)


def validate_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single event dictionary.

    Raises ``ValueError`` if required keys are missing or have the wrong type.
    """
    _require(isinstance(event, dict), "Event must be a dict")
    ev_type = event.get("type")
    _require(ev_type in EVENT_TYPES, f"Unsupported event type: {ev_type!r}")
    required = _REQUIRED_FIELDS[ev_type]
    missing = [k for k in required if k not in event]
    _require(not missing, f"Missing required fields for {ev_type}: {missing}")
    # Generic field checks
    _require(isinstance(event["id"], str) and event["id"], "'id' must be a non‑empty string")
    _require(isinstance(event["timestamp"], int) and event["timestamp"] >= 0, "'timestamp' must be a non‑negative integer")
    # Optional generic fields
    if "parent_id" in event:
        _require(event["parent_id"] is None or isinstance(event["parent_id"], str), "'parent_id' must be str or None")
    if "ref_to" in event:
        _require(isinstance(event["ref_to"], list) and all(isinstance(i, str) for i in event["ref_to"]), "'ref_to' must be a list of strings")
    if "content" in event:
        _require(event["content"] is None or isinstance(event["content"], str), "'content' must be str or None")
    
    # Validation for new Phase 1 event metadata
    if "importance" in event:
        _require(event["importance"] in {"critical", "task", "session", "temporary", "debug"}, "'importance' must be one of: critical, task, session, temporary, debug")
    if "tags" in event:
        _require(isinstance(event["tags"], list) and all(isinstance(t, str) for t in event["tags"]), "'tags' must be a list of strings")
    if "retain_until" in event:
        _require(event["retain_until"] in {"task_end", "session_end", None}, "'retain_until' must be one of: task_end, session_end, None")

    # No further validation for value/arguments/result – they can be any JSON‑serialisable type.
    return event


def load_events_from_json(path: str) -> List[Dict[str, Any]]:
    """Load a JSON array of events from *path* and validate each entry."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    _require(isinstance(raw, list), "Top‑level JSON must be a list of events")
    return [validate_event(ev) for ev in raw]
