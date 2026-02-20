"""
Run evaluation: ablation vs ours/kimi-k2-0905
Judge: Claude Sonnet via AWS Bedrock API

Usage:
    python run_ablation_eval.py                                    # ablation-no-coupling
    python run_ablation_eval.py --ablation ablation_no_openvocab
    python run_ablation_eval.py --ablation ablation_no_decay
    python run_ablation_eval.py --ablation ablation-no-coupling -d empathy appropriateness
"""
import argparse
from pathlib import Path
from evaluator import LLMEvaluator
from convert_ablation import convert

KIMI_PATH = "../results/1_conversations/ours/kimi-k2-0905/conversations.json"
CONFIG_PATH = "bedrock_example/config_bedrock_sonnet.json"
ENV_PATH = "bedrock_example/.env"

ALL_DIMENSIONS = [
    "believability",
    "empathy",
    "appropriateness",
    "continuity",
    "communication",
    "social_rules",
]


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate ablation vs ours/kimi-k2-0905 using Claude Sonnet on Bedrock"
    )
    parser.add_argument(
        "--ablation",
        default="ablation-no-coupling",
        help="Ablation directory name under results/ (default: ablation-no-coupling)",
    )
    parser.add_argument(
        "-d", "--dimensions",
        nargs="+",
        default=ALL_DIMENSIONS,
        help="Dimensions to evaluate (default: all 6)",
    )
    parser.add_argument(
        "-n", "--max-conversations",
        type=int,
        default=None,
        help="Max number of conversation pairs to evaluate (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to save results (default: EmotionalAgentEval/results/)",
    )
    args = parser.parse_args()

    ablation_dir = Path("../results") / args.ablation
    conv_path = ablation_dir / "conversations.json"

    # Auto-convert if conversations.json doesn't exist yet
    if not conv_path.exists():
        print(f"conversations.json not found, converting {ablation_dir} ...")
        convert(ablation_dir)

    evaluator = LLMEvaluator(config_path=CONFIG_PATH, env_path=ENV_PATH)

    print(f"Ablation    : {args.ablation}")
    print(f"Judge model : {evaluator.config.get('deployment_name')}")
    print(f"Dimensions  : {args.dimensions}")
    print(f"Max pairs   : {args.max_conversations or 'all'}")
    print()

    session_dir = evaluator.run_evaluation(
        conv_path1=str(conv_path),
        conv_path2=KIMI_PATH,
        dimensions=args.dimensions,
        parent_dir=args.output_dir,
        max_conversations=args.max_conversations,
    )

    print(f"\nDone. Results: {session_dir}")


if __name__ == "__main__":
    main()
