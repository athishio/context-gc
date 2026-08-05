# context_gc/dedup_engine.py
"""Deduplication engine – prunes duplicate tool calls."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import List, Dict, Any

from .graph import StateGraph


def deduplicate_tool_calls(graph: StateGraph) -> List[str]:
    """Detect and prune duplicate tool calls.

    A tool-call is a duplicate if it has the same tool name, same arguments,
    and same result as an earlier surviving tool-call.
    
    Returns
    -------
    List[str]
        IDs of nodes (both tool_calls and tool_results) that were pruned.
    """
    # 1. Map call_id to tool_result nodes (only surviving/not pruned results)
    tool_results: Dict[str, Dict[str, Any]] = {}
    for node_id, node in graph.nodes.items():
        if node_id in graph.pruned:
            continue
        if node.get("type") == "tool_result" and "call_id" in node:
            tool_results[node["call_id"]] = node

    # 2. Group active tool_call nodes by (tool_name, arguments, result)
    groups: Dict[tuple, List[Dict[str, Any]]] = defaultdict(list)
    for node_id, node in graph.nodes.items():
        if node_id in graph.pruned:
            continue
        if node.get("type") == "tool_call":
            # Must have an associated surviving tool_result to be deduplicated
            res_node = tool_results.get(node_id)
            if res_node is None:
                continue
            
            # Serialize arguments and result to make them hashable
            try:
                args_str = json.dumps(node.get("arguments"), sort_keys=True)
                res_str = json.dumps(res_node.get("result"), sort_keys=True)
            except (TypeError, ValueError):
                # Fallback to string representation if not json serializable
                args_str = str(node.get("arguments"))
                res_str = str(res_node.get("result"))

            key = (node.get("tool_name"), args_str, res_str)
            groups[key].append(node)

    pruned_ids: List[str] = []
    for key, tcs in groups.items():
        if len(tcs) <= 1:
            continue
        # Sort by timestamp ascending
        tcs.sort(key=lambda x: x["timestamp"])
        surviving_tc = tcs[0]
        surviving_tc_id = surviving_tc["id"]
        surviving_tr_id = tool_results[surviving_tc_id]["id"]

        for dup_tc in tcs[1:]:
            dup_tc_id = dup_tc["id"]
            dup_tr_id = tool_results[dup_tc_id]["id"]

            # Add supersedes edges
            graph.add_edge(surviving_tc_id, dup_tc_id, "supersedes")
            graph.add_edge(surviving_tr_id, dup_tr_id, "supersedes")

            # Mark duplicate nodes as pruned
            graph.mark_pruned(dup_tc_id)
            graph.mark_pruned(dup_tr_id)

            pruned_ids.append(dup_tc_id)
            pruned_ids.append(dup_tr_id)

    return pruned_ids
