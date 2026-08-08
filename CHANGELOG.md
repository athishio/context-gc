# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-08-08

### Added
- **Retention Policy & Safety primitives**:
  - Optional event schema attributes: `importance` (`critical`, `task`, `session`, `temporary`, `debug`), `tags`, and `retain_until` (`task_end`, `session_end`, `None`).
  - Added `is_protected(event)` check inside override, dead-branch sweeper, and deduplication engines to prevent pruning of critical events.
  - Added `protected` tracking inside `StateGraph` along with audit/reason logs for compaction (`prune_reasons`, `protected_reasons`).
- **CLI Management Tool**:
  - `context-gc compact [--dry-run] <trace>`: Compacts events; dry-run mode displays prune/protect actions and token savings without outputting the prompt.
  - `context-gc explain <trace> <node_id>`: Displays full event data, status (pruned/protected/kept), and details of what would/did override or abandon the node.
  - `context-gc restore <trace> <node_id>`: Recovers and prints the original event payload of a pruned node.
  - `context-gc diff <trace>`: Displays a unified diff showing original vs compacted prompt.

## [0.1.1] - 2026-08-06

### Changed
- **Docs**: Added methodology caveat for the decision probe's exact-substring-matching limitation; corrected average latency figure for `ai_summarize_recursive` on long traces to exclude a rate-limit retry wait.

## [0.1.0] - 2026-07-31

### Added
- **Core Compaction Pipeline (Week 1)**:
  - `StateGraph` core graph model with optimized forward adjacency cache mapping and reverse lookup.
  - **Dead-Branch Sweeper (DFS)**: Prunes unsuccessful branches starting from `abandon` events.
  - **Override Engine**: Prunes overridden variable updates (`set_var` events) among surviving nodes.
  - **Deduplication Engine**: Deduplicates exact-duplicate tool call results.
  - **Topological Sampler**: Detects cycles and strongly connected components (SCCs) via Tarjan's algorithm and collapses them.
  - **Receipts**: Preserves original events of pruned nodes for recovery.
- **Packaging and PEP 621 Standard (Week 2 - In Progress)**:
  - Added `pyproject.toml` using PEP 621 format.
  - Core library remains completely dependency-free, with testing libraries configured as optional dependencies.
  - Added MIT `LICENSE` and initial packaging configurations.
