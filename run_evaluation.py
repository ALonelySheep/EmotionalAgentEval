"""
Command-line script to run LLM-as-Judge evaluation.

Usage:
    # Evaluate all dimensions
    python run_evaluation.py path/to/conv1.json path/to/conv2.json

    # Evaluate specific dimensions
    python run_evaluation.py path/to/conv1.json path/to/conv2.json --dimensions believability coherence
    # Limit number of conversations
    python run_evaluation.py path/to/conv1.json path/to/conv2.json --num-conversations 50
    # List available dimensions
    python run_evaluation.py --list-dimensions
"""

import argparse
import sys
from pathlib import Path
from evaluator import LLMEvaluator


def list_dimensions():
    """List all available evaluation dimensions."""
    try:
        evaluator = LLMEvaluator(
            config_path="bedrock_example/config.json", env_path="bedrock_example/.env"
        )
        dimensions = evaluator.get_available_dimensions()

        print("Available evaluation dimensions:")
        for dim in dimensions:
            print(f"  - {dim}")
        print()
        print(f"Total: {len(dimensions)} dimension(s)")

    except Exception as e:
        print(f"ERROR: Failed to list dimensions: {e}")
        sys.exit(1)


def main():
    """Run evaluation with command line arguments."""
    parser = argparse.ArgumentParser(
        description="LLM-as-Judge Evaluation System for Multi-Agent Conversations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate all dimensions
  python run_evaluation.py baseline/conv.json ours/conv.json
  
  # Evaluate specific dimensions
  python run_evaluation.py baseline/conv.json ours/conv.json --dimensions believability
  
  # Limit number of conversations
  python run_evaluation.py baseline/conv.json ours/conv.json --num-conversations 50
  
  # List available dimensions
  python run_evaluation.py --list-dimensions
        """,
    )

    parser.add_argument(
        "conv_path1", nargs="?", help="Path to first conversation JSON file"
    )

    parser.add_argument(
        "conv_path2", nargs="?", help="Path to second conversation JSON file"
    )

    parser.add_argument(
        "--dimensions",
        "-d",
        nargs="+",
        help="Evaluation dimensions to use (default: all available dimensions)",
    )

    parser.add_argument(
        "--num-conversations",
        "-n",
        type=int,
        help="Maximum number of conversations to evaluate (default: use minimum available from both files)",
    )

    parser.add_argument(
        "--list-dimensions",
        "-l",
        action="store_true",
        help="List all available evaluation dimensions and exit",
    )

    parser.add_argument(
        "--config",
        default="bedrock_example/config.json",
        help="Path to config.json (default: bedrock_example/config.json)",
    )

    parser.add_argument(
        "--env",
        default="bedrock_example/.env",
        help="Path to .env file (default: bedrock_example/.env)",
    )

    args = parser.parse_args()

    # Handle list dimensions request
    if args.list_dimensions:
        list_dimensions()
        return

    # Validate required arguments
    if not args.conv_path1 or not args.conv_path2:
        parser.error(
            "Both conv_path1 and conv_path2 are required unless using --list-dimensions"
        )

    # Validate file paths exist
    if not Path(args.conv_path1).exists():
        print(f"ERROR: File not found: {args.conv_path1}")
        sys.exit(1)

    if not Path(args.conv_path2).exists():
        print(f"ERROR: File not found: {args.conv_path2}")
        sys.exit(1)

    print("Starting LLM-as-Judge Evaluation System...")
    print()
    print("Configuration:")
    print(f"  Config: {args.config}")
    print(f"  Env: {args.env}")
    print(f"  Path 1: {args.conv_path1}")
    print(f"  Path 2: {args.conv_path2}")
    if args.dimensions:
        print(f"  Dimensions: {', '.join(args.dimensions)}")
    else:
        print("  Dimensions: all available")
    if args.num_conversations:
        print(f"  Max conversations: {args.num_conversations}")
    print()

    # Initialize evaluator
    try:
        evaluator = LLMEvaluator(config_path=args.config, env_path=args.env)
    except Exception as e:
        print(f"ERROR: Failed to initialize evaluator: {e}")
        sys.exit(1)

    # Run evaluation
    try:
        session_dir = evaluator.run_evaluation(
            conv_path1=args.conv_path1,
            conv_path2=args.conv_path2,
            dimensions=args.dimensions,  # None if not specified, which uses all
            max_conversations=args.num_conversations,  # None if not specified
        )

        print()
        print("✓ Evaluation completed successfully!")
        print(f"✓ Results saved to: {session_dir}")

    except Exception as e:
        print(f"ERROR: Evaluation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
