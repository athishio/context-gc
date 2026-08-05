# context_gc/dead_branch_sweeper.py
"""Dead‑branch sweeper – prunes abandoned execution paths.

Walks sequence edges starting from abandon event targets to prune entire abandoned sub-branches.
"""

from __future__ import annotations

from typing import List, Set

from .graph import StateGraph


def sweep_dead_branches(graph: StateGraph) -> List[str]:
    """Prune nodes and their descendants targeted by abandon events, returning pruned IDs."""
    to_prune: Set[str] = set()
    # Identify all abandon events and collect their target IDs (list).
    abandon_targets: List[str] = []
    for ev in graph.nodes.values():
        if ev.get("type") == "abandon":
            # ``ref_to`` is a list of node IDs to abandon
            for tgt in ev.get("ref_to", []):
                abandon_targets.append(tgt)

    # Depth‑first walk following *sequence* edges only.
    def dfs(start_id: str) -> None:
        stack = [start_id]
        while stack:
            cur = stack.pop()
            if cur in to_prune:
                continue
            to_prune.add(cur)
            for child in graph.get_children(cur, edge_types=["sequence"]):
                stack.append(child)

    for tgt in abandon_targets:
        if tgt in graph.nodes:
            dfs(tgt)

    for node_id in to_prune:
        graph.mark_pruned(node_id)
    return list(to_prune)
