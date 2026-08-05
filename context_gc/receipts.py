# context_gc/receipts.py
"""Receipt handling utilities.

The :func:`collect_receipts` function extracts all receipt stubs that were
generated during pruning (by :meth:`StateGraph.mark_pruned`).  The receipts are
stored on the graph in ``graph.receipts`` as a mapping ``node_id -> receipt``.

The :func:`get_receipt` function returns the original event dict for a pruned
node, allowing callers to recover the full event information.
"""

from __future__ import annotations

from typing import List, Dict

from .graph import StateGraph


def collect_receipts(graph: StateGraph) -> List[Dict]:
    """Return a list of receipt dictionaries generated during pruning.

    The order is deterministic – receipts are sorted by their ``timestamp``.
    """
    receipts = list(graph.receipts.values())
    receipts.sort(key=lambda r: r.get("timestamp", 0))
    return receipts


def get_receipt(graph: StateGraph, node_id: str) -> dict:
    """Return the original event dict for a pruned node.

    Raises ``KeyError`` if the node ID does not exist in ``graph.nodes``.
    """
    if node_id not in graph.nodes:
        raise KeyError(f"Unknown node id: {node_id}")
    return graph.nodes[node_id]
