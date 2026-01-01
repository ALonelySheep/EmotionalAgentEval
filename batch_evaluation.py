"""
Batch evaluation script to compare all model pairs from the 1a_conversation_subset folder.

This script:
1. Discovers all models in baseline/ and ours/ folders
2. Generates all unique pairs (36 pairs from 9 models)
3. Runs evaluation for each pair
4. Aggregates results to calculate average scores per model
"""

import json
import argparse
import numpy as np
from pathlib import Path
from itertools import combinations
from datetime import datetime
from evaluator import LLMEvaluator
from typing import Dict, List, Tuple, Union, Optional


def discover_models(base_path: Union[str, Path]) -> List[Tuple[str, str]]:
    """
    Discover all available models in the 1a_conversation_subset folder.

    Args:
        base_path: Path to 1a_conversation_subset folder

    Returns:
        List of tuples (category, model_name, full_path)
    """
    base_path = Path(base_path)
    models = []

    # Check baseline models
    baseline_dir = base_path / "baseline"
    if baseline_dir.exists():
        for model_dir in baseline_dir.iterdir():
            if model_dir.is_dir():
                conv_file = model_dir / "conversations.json"
                if conv_file.exists():
                    models.append(("baseline", model_dir.name, str(conv_file)))

    # Check ours models
    ours_dir = base_path / "ours"
    if ours_dir.exists():
        for model_dir in ours_dir.iterdir():
            if model_dir.is_dir():
                conv_file = model_dir / "conversations.json"
                if conv_file.exists():
                    models.append(("ours", model_dir.name, str(conv_file)))

    return models


def check_conversation_counts(models: List[Tuple[str, str, str]]) -> Dict:
    """
    Check the number of conversations in each model file.

    Args:
        models: List of tuples (category, model_name, full_path)

    Returns:
        Dictionary with conversation counts and statistics
    """
    counts = {}
    all_counts = []

    for category, name, path in models:
        model_label = f"{category}/{name}"
        with open(path, "r", encoding="utf-8") as f:
            conversations = json.load(f)
            count = len(conversations)
            counts[model_label] = count
            all_counts.append(count)

    return {
        "counts": counts,
        "min": min(all_counts) if all_counts else 0,
        "max": max(all_counts) if all_counts else 0,
        "average": sum(all_counts) / len(all_counts) if all_counts else 0,
    }


def create_batch_session_folder() -> str:
    """Create a timestamped batch session folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = Path(__file__).parent / "results" / f"batch_eval_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)
    return str(session_dir)


def run_batch_evaluation(
    base_path: str,
    dimensions: Optional[List[str]] = None,
    num_conversations: Optional[int] = None,
    config_path: str = "bedrock_example/config.json",
    env_path: str = "bedrock_example/.env",
):
    """
    Run batch evaluation on all model pairs.

    Args:
        base_path: Path to 1a_conversation_subset folder
        dimensions: List of evaluation dimensions (None = all)
        num_conversations: Number of conversations to use per evaluation (None = use minimum available)
        config_path: Path to config.json
        env_path: Path to .env file
    """
    print("=" * 80)
    print("BATCH EVALUATION: All Model Pairs")
    print("=" * 80)
    print()

    # Step 1: Discover all models
    print("Step 1: Discovering models...")
    models = discover_models(base_path)

    print(models)

    print(f"Found {len(models)} models:")
    for category, name, path in models:
        print(f"  - {category}/{name}")
    print()

    # Check conversation counts
    print("Checking conversation counts...")
    conv_counts = check_conversation_counts(models)
    print(f"  Minimum conversations: {conv_counts['min']}")
    print(f"  Maximum conversations: {conv_counts['max']}")
    print(f"  Average conversations: {conv_counts['average']:.1f}")
    print()
    print("Per-model counts:")
    for model_label, count in sorted(conv_counts["counts"].items()):
        print(f"  {model_label:30s} {count} conversations")
    print()

    # Determine number of conversations to use
    if num_conversations is None:
        num_conversations = conv_counts["min"]
        print(f"Using minimum conversation count: {num_conversations}")
    else:
        if num_conversations > conv_counts["min"]:
            print(
                f"WARNING: Requested {num_conversations} conversations but minimum available is {conv_counts['min']}"
            )
            print(f"Using {conv_counts['min']} conversations instead")
            num_conversations = conv_counts["min"]
        else:
            print(f"Using specified conversation count: {num_conversations}")
    print()

    # Step 2: Generate all unique pairs
    print("Step 2: Generating model pairs...")
    all_pairs = list(combinations(models, 2))
    print(f"Total pairs to evaluate: {len(all_pairs)}")
    print()

    # Step 3: Create batch session folder
    print("Step 3: Creating batch session folder...")
    batch_session_dir = create_batch_session_folder()
    print(f"Batch session directory: {batch_session_dir}")
    print()

    # Step 4: Initialize evaluator
    print("Step 4: Initializing evaluator...")
    try:
        evaluator = LLMEvaluator(config_path=config_path, env_path=env_path)
        if dimensions:
            print(f"Using dimensions: {', '.join(dimensions)}")
        else:
            available_dims = evaluator.get_available_dimensions()
            print(f"Using all available dimensions: {', '.join(available_dims)}")
    except Exception as e:
        print(f"ERROR: Failed to initialize evaluator: {e}")
        return
    print()

    # Step 5: Run evaluations for all pairs
    print("Step 5: Running evaluations...")
    print("=" * 80)
    print()

    pair_results = []

    for idx, ((cat1, name1, path1), (cat2, name2, path2)) in enumerate(all_pairs, 1):
        model1_label = f"{cat1}/{name1}"
        model2_label = f"{cat2}/{name2}"

        print(f"[{idx}/{len(all_pairs)}] Evaluating: {model1_label} vs {model2_label}")
        print("-" * 80)

        try:
            # Run evaluation for this pair (store inside batch folder)
            session_dir = evaluator.run_evaluation(
                conv_path1=path1,
                conv_path2=path2,
                dimensions=dimensions,
                parent_dir=batch_session_dir,
                max_conversations=num_conversations,
            )

            # Load aggregated results
            agg_path = Path(session_dir) / "aggregated_results.json"
            with open(agg_path, "r") as f:
                aggregated = json.load(f)

            # Store pair results
            pair_result = {
                "pair_index": idx,
                "model1": model1_label,
                "model2": model2_label,
                "model1_path": path1,
                "model2_path": path2,
                "session_dir": session_dir,
                "results": aggregated["dimensions"],
            }
            pair_results.append(pair_result)

            print()
            print(f"✓ Pair {idx} completed")
            print()

        except Exception as e:
            print(f"✗ ERROR evaluating pair {idx}: {e}")
            import traceback

            traceback.print_exc()
            print()
            continue

    print("=" * 80)
    print(f"All {len(pair_results)} pair evaluations completed!")
    print("=" * 80)
    print()

    # Step 6: Aggregate results across all pairs
    print("Step 6: Aggregating results across all model pairs...")
    model_aggregate = aggregate_model_scores(pair_results, models)

    # Save batch results
    batch_results = {
        "timestamp": datetime.now().isoformat(),
        "base_path": base_path,
        "num_models": len(models),
        "num_pairs": len(all_pairs),
        "num_conversations_per_pair": num_conversations,
        "conversation_counts": conv_counts,
        "dimensions": dimensions
        if dimensions
        else evaluator.get_available_dimensions(),
        "models": [
            {"category": cat, "name": name, "path": path} for cat, name, path in models
        ],
        "pair_results": pair_results,
        "model_aggregate": model_aggregate,
    }

    # Save to JSON
    batch_results_path = Path(batch_session_dir) / "batch_results.json"
    with open(batch_results_path, "w", encoding="utf-8") as f:
        json.dump(batch_results, f, indent=2)
    print(f"  Batch results saved to: batch_results.json")

    # Save model aggregates to CSV
    import csv

    csv_path = Path(batch_session_dir) / "model_average_scores.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        if model_aggregate:
            dimensions_list = list(
                next(iter(model_aggregate.values()))["dimensions"].keys()
            )
            writer = csv.writer(f)

            # Header
            header = (
                ["Model", "Category", "Num_Comparisons"]
                + dimensions_list
                + ["Overall_Average"]
            )
            writer.writerow(header)

            # Sort by overall average (descending)
            sorted_models = sorted(
                model_aggregate.items(),
                key=lambda x: x[1]["overall_average"],
                reverse=True,
            )

            # Rows
            for model_label, data in sorted_models:
                category = data["category"]
                num_comparisons = data["num_comparisons"]
                dim_scores = [
                    f"{data['dimensions'][dim]:.2f}" for dim in dimensions_list
                ]
                overall = f"{data['overall_average']:.2f}"

                row = [model_label, category, num_comparisons] + dim_scores + [overall]
                writer.writerow(row)

    print("  Model average scores saved to: model_average_scores.csv")

    # Generate aggregated results similar to individual sessions
    generate_batch_aggregated_results(
        batch_session_dir,
        model_aggregate,
        dimensions if dimensions else evaluator.get_available_dimensions(),
    )
    print("  Aggregated results saved to: aggregated_results.json")
    print("  Aggregated results saved to: aggregated_results.csv")
    print("  Chart saved to: evaluation_chart.png")
    print()

    # Step 7: Display summary
    print("Step 7: Summary of Results")
    print("=" * 80)
    print()
    print(f"Model Rankings (by overall average score):")
    print()

    sorted_models = sorted(
        model_aggregate.items(), key=lambda x: x[1]["overall_average"], reverse=True
    )

    for rank, (model_label, data) in enumerate(sorted_models, 1):
        category = data["category"]
        avg_score = data["overall_average"]
        num_comp = data["num_comparisons"]
        print(f"  {rank}. {model_label:30s} [{category}]")
        print(f"     Average Score: {avg_score:.2f} (across {num_comp} comparisons)")

        # Show per-dimension scores
        for dim, score in data["dimensions"].items():
            print(f"       - {dim}: {score:.2f}")
        print()

    print("=" * 80)
    print(f"Batch evaluation complete!")
    print(f"Results saved to: {batch_session_dir}")
    print("=" * 80)


def aggregate_model_scores(pair_results: List[Dict], models: List[Tuple]) -> Dict:
    """
    Aggregate scores for each model across all comparisons.

    Args:
        pair_results: List of pair evaluation results
        models: List of all models

    Returns:
        Dictionary mapping model labels to their aggregate scores
    """
    model_scores = {}

    # Initialize structure for each model
    for category, name, path in models:
        model_label = f"{category}/{name}"
        model_scores[model_label] = {
            "category": category,
            "name": name,
            "path": path,
            "dimensions": {},
            "num_comparisons": 0,
        }

    # Collect scores from all pair evaluations
    for pair_result in pair_results:
        model1 = pair_result["model1"]
        model2 = pair_result["model2"]
        results = pair_result["results"]

        # Add scores for model1 (path_1_average)
        for dimension, data in results.items():
            if dimension not in model_scores[model1]["dimensions"]:
                model_scores[model1]["dimensions"][dimension] = []
            model_scores[model1]["dimensions"][dimension].append(data["path_1_average"])
        model_scores[model1]["num_comparisons"] += 1

        # Add scores for model2 (path_2_average)
        for dimension, data in results.items():
            if dimension not in model_scores[model2]["dimensions"]:
                model_scores[model2]["dimensions"][dimension] = []
            model_scores[model2]["dimensions"][dimension].append(data["path_2_average"])
        model_scores[model2]["num_comparisons"] += 1

    # Calculate averages
    for model_label, data in model_scores.items():
        dimension_averages = {}
        all_scores = []

        for dimension, scores in data["dimensions"].items():
            avg = sum(scores) / len(scores) if scores else 0
            dimension_averages[dimension] = avg
            all_scores.extend(scores)

        data["dimensions"] = dimension_averages
        data["overall_average"] = sum(all_scores) / len(all_scores) if all_scores else 0

    return model_scores


def generate_batch_aggregated_results(
    batch_session_dir: str, model_aggregate: Dict, dimensions: List[str]
):
    """
    Generate aggregated results files similar to individual evaluation sessions.

    Args:
        batch_session_dir: Path to batch session directory
        model_aggregate: Dictionary with aggregated model scores
        dimensions: List of evaluation dimensions
    """
    import matplotlib.pyplot as plt
    import csv

    # Prepare aggregated data structure
    aggregated = {"dimensions": {}}

    # For each dimension, collect all model scores
    for dimension in dimensions:
        model_scores = {}
        for model_label, data in model_aggregate.items():
            if dimension in data["dimensions"]:
                model_scores[model_label] = data["dimensions"][dimension]

        aggregated["dimensions"][dimension] = {
            "model_scores": model_scores,
            "average": sum(model_scores.values()) / len(model_scores)
            if model_scores
            else 0,
        }

    # Save aggregated_results.json
    agg_json_path = Path(batch_session_dir) / "aggregated_results.json"
    with open(agg_json_path, "w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=2)

    # Save aggregated_results.csv
    agg_csv_path = Path(batch_session_dir) / "aggregated_results.csv"
    with open(agg_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        header = ["Model"] + dimensions
        writer.writerow(header)

        # Sort models by overall average (descending)
        sorted_models = sorted(
            model_aggregate.items(), key=lambda x: x[1]["overall_average"], reverse=True
        )

        # Rows
        for model_label, data in sorted_models:
            row = [model_label]
            for dim in dimensions:
                score = data["dimensions"].get(dim, 0)
                row.append(f"{score:.2f}")
            writer.writerow(row)

    # Generate bar chart
    plot_batch_results(batch_session_dir, model_aggregate, dimensions)


def plot_batch_results(
    batch_session_dir: str, model_aggregate: Dict, dimensions: List[str]
):
    """
    Generate bar chart visualization for batch evaluation results.

    Args:
        batch_session_dir: Path to batch session directory
        model_aggregate: Dictionary with aggregated model scores
        dimensions: List of evaluation dimensions
    """
    import matplotlib.pyplot as plt
    import numpy as np

    # Sort models by overall average (descending)
    sorted_models = sorted(
        model_aggregate.items(), key=lambda x: x[1]["overall_average"], reverse=True
    )

    model_labels = [label for label, _ in sorted_models]

    # Prepare data for each dimension
    dimension_data = {}
    for dimension in dimensions:
        dimension_data[dimension] = [
            data["dimensions"].get(dimension, 0) for _, data in sorted_models
        ]

    # Create grouped bar chart
    x = np.arange(len(model_labels))
    width = 0.8 / len(dimensions) if dimensions else 0.8

    fig, ax = plt.subplots(figsize=(14, 8))

    colors = plt.cm.Set3(np.linspace(0, 1, len(dimensions)))

    for idx, (dimension, scores) in enumerate(dimension_data.items()):
        offset = (idx - len(dimensions) / 2 + 0.5) * width
        bars = ax.bar(x + offset, scores, width, label=dimension, color=colors[idx])

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{height:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

    # Customize chart
    ax.set_xlabel("Models", fontsize=12, fontweight="bold")
    ax.set_ylabel("Average Score", fontsize=12, fontweight="bold")
    ax.set_title(
        "Batch Evaluation Results - All Models", fontsize=14, fontweight="bold"
    )
    ax.set_xticks(x)
    ax.set_xticklabels(model_labels, rotation=45, ha="right")
    ax.legend(title="Dimensions", loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, 10.5)

    plt.tight_layout()

    # Save chart
    chart_path = Path(batch_session_dir) / "evaluation_chart.png"
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    """Main function with command line arguments."""
    parser = argparse.ArgumentParser(
        description="Batch evaluation of all model pairs from 1a_conversation_subset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--base-path",
        default="../results/1a_conversation_subset",
        help="Path to 1a_conversation_subset folder (default: ../results/1a_conversation_subset)",
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
        help="Number of conversations to use per evaluation (default: use minimum available across all models)",
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

    # Run batch evaluation
    run_batch_evaluation(
        base_path=args.base_path,
        dimensions=args.dimensions,
        num_conversations=args.num_conversations,
        config_path=args.config,
        env_path=args.env,
    )


if __name__ == "__main__":
    main()
