#!/usr/bin/env python
"""
Classifier Evaluation Management Tool
Manage, label, and analyze classifier evaluations.

Usage:
    python eval_manager.py --show-unlabeled          # Show unlabeled responses
    python eval_manager.py --label <id> <label>      # Label a response
    python eval_manager.py --metrics                  # Show accuracy metrics
    python eval_manager.py --export                   # Export for analysis
    python eval_manager.py --misclassifications       # Show errors
"""

import argparse
import sys
from preflight.evaluation import EvaluationLogger
from preflight.core.behavior import Behavior


def show_unlabeled(logger, limit=5):
    """Show unlabeled responses for manual review."""
    responses = logger.get_unlabeled_responses(limit=limit)
    
    if not responses:
        print("No unlabeled responses! All caught up.")
        return
    
    print(f"\n{'='*80}")
    print(f"UNLABELED RESPONSES ({len(responses)} shown)")
    print(f"{'='*80}\n")
    
    for resp in responses:
        print(f"ID: {resp['id']}")
        print(f"Invariant: {resp['invariant_name']}")
        print(f"Classified as: {resp['classified_as'].upper()}")
        print(f"Timestamp: {resp['timestamp']}")
        
        if resp['prompt_text']:
            print(f"\nPrompt:\n{resp['prompt_text'][:200]}...")
        
        print(f"\nResponse:\n{resp['response_text'][:300]}...")
        
        print(f"\n[ID {resp['id']}] Label this as: refuse | deflect | partial_compliance | full_compliance")
        print("-" * 80)
        print()


def label_response(logger, response_id, label_text):
    """Label a response with ground truth."""
    try:
        label = Behavior[label_text.upper()]
    except KeyError:
        print(f"Invalid label: {label_text}")
        print("Valid labels: refuse, deflect, partial_compliance, full_compliance")
        return False
    
    logger.label_response(response_id, label)
    print(f"✓ Labeled response {response_id} as {label.value}")
    return True


def show_metrics(logger):
    """Show current accuracy metrics."""
    logger.print_summary()
    
    misclassifications = logger.get_misclassifications()
    if misclassifications:
        print(f"\nFound {len(misclassifications)} misclassifications:")
        print("(These are where classifier was wrong)\n")
        
        for i, mis in enumerate(misclassifications[:5], 1):
            print(f"{i}. ID {mis['id']}: Classified as {mis['classified_as'].upper()}, "
                  f"should be {mis['human_label'].upper()}")
            print(f"   Invariant: {mis['invariant_name']}")
            print()


def show_misclassifications(logger):
    """Show all misclassifications for analysis."""
    misclassifications = logger.get_misclassifications()
    
    if not misclassifications:
        print("No misclassifications! Classifier is performing well.")
        return
    
    print(f"\n{'='*80}")
    print(f"MISCLASSIFICATIONS ({len(misclassifications)} total)")
    print(f"{'='*80}\n")
    
    # Group by type
    by_type = {}
    for mis in misclassifications:
        key = f"{mis['classified_as']} → {mis['human_label']}"
        if key not in by_type:
            by_type[key] = []
        by_type[key].append(mis)
    
    for error_type, examples in sorted(by_type.items()):
        print(f"\n{error_type}: {len(examples)} cases")
        print("-" * 80)
        
        for mis in examples[:2]:  # Show first 2 of each type
            print(f"\nID {mis['id']}:")
            print(f"Response: {mis['response_text'][:250]}...")
            if mis['prompt_text']:
                print(f"Prompt: {mis['prompt_text'][:150]}...")
            print()


def export_data(logger):
    """Export evaluation data."""
    output_file = logger.export_for_analysis()
    print(f"✓ Exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage classifier evaluations for accuracy tracking"
    )
    
    parser.add_argument(
        "--show-unlabeled",
        action="store_true",
        help="Show unlabeled responses for review"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Limit number of responses to show (default: 5)"
    )
    
    parser.add_argument(
        "--label",
        nargs=2,
        metavar=("ID", "LABEL"),
        help="Label a response: --label <id> <refuse|deflect|partial_compliance|full_compliance>"
    )
    
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Show accuracy metrics"
    )
    
    parser.add_argument(
        "--misclassifications",
        action="store_true",
        help="Show all misclassifications"
    )
    
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export evaluation data as JSON"
    )
    
    args = parser.parse_args()
    
    logger = EvaluationLogger()
    
    if args.show_unlabeled:
        show_unlabeled(logger, limit=args.limit)
    
    elif args.label:
        response_id, label_text = args.label
        label_response(logger, int(response_id), label_text)
    
    elif args.metrics:
        show_metrics(logger)
    
    elif args.misclassifications:
        show_misclassifications(logger)
    
    elif args.export:
        export_data(logger)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
