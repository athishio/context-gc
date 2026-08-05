import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
DEFAULT_FIXTURE = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "sample_trace.json")

from context_gc.events import load_events_from_json
from context_gc.compactor import compact_events

def main():
    parser = argparse.ArgumentParser(description="Deterministic context compaction middleware demo.")
    parser.add_argument(
        "--fixture",
        type=str,
        default=DEFAULT_FIXTURE,
        help="Path to the event trace JSON fixture file (default: sample_trace.json)"
    )
    args = parser.parse_args()

    events = load_events_from_json(args.fixture)
    result = compact_events(events)

    print("=" * 60)
    print(f"Total events in:     {len(events)}")
    print(f"Events pruned:       {len(result['pruned_ids'])}")
    print(f"Events surviving:    {len(result['compact_events'])}")
    print(f"Tokens before:       {result['tokens_before']}")
    print(f"Tokens after:        {result['tokens_after']}")
    reduction = (1 - result['tokens_after'] / result['tokens_before']) * 100
    print(f"Reduction:           {reduction:.1f}%")
    print("=" * 60)

    print("\n--- COMPACTED PROMPT ---\n")
    print(result["prompt"])

    print("\n--- RECEIPTS ---\n")
    for r in result["receipts"]:
        print(r)

    from context_gc.receipts import get_receipt
    print("\n--- RECEIPT RECOVERY ---")
    for node_id in result['pruned_ids'][:2]:
        print(f"Recovered {node_id}: {get_receipt(result['graph'], node_id)}")

if __name__ == "__main__":
    main()