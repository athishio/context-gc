# context_gc/override_engine.py
"""Override engine – identifies and prunes superseded ``set_var`` updates.

Retains only the latest set_var event for each key (by timestamp) among surviving 
nodes and marks all preceding writes as pruned.
"""

from __future__ import annotations

from collections import defaultdict
from typing import List

from .graph import StateGraph


def apply_overrides(graph: StateGraph) -> List[str]:
    """Detect and prune superseded ``set_var`` events, returning the pruned IDs."""
    # Group ``set_var`` events by their ``key``
    key_to_events: dict[str, List[dict]] = defaultdict(list)
    for node_id, event in graph.nodes.items():
        if node_id in graph.pruned:
            continue
        if event.get("type") == "set_var" and event.get("key") is not None:
            key_to_events[event["key"]].append(event)

    pruned_ids: List[str] = []
    for key, events in key_to_events.items():
        # Sort by timestamp ascending; newest is last
        events.sort(key=lambda e: e["timestamp"])
        newest = events[-1]
        newest_id = newest["id"]
        # Older events are superseded
        for older in events[:-1]:
            older_id = older["id"]
            # Add supersedes edge from newest -> older
            graph.add_edge(newest_id, older_id, "supersedes")
            # Mark older as pruned
            graph.mark_pruned(older_id)
            pruned_ids.append(older_id)
    return pruned_ids
