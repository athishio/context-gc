# Changelog

All notable changes to this project will be documented in this file.

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
