"""
LLM-as-Judge Evaluation System for Multi-Agent Social Simulations.

This module implements an evaluation pipeline that uses LLMs to compare
conversation quality across different systems (baseline vs. improved).
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
import boto3
import matplotlib.pyplot as plt
import csv
import prompts


class LLMEvaluator:
    """
    Main evaluation class for comparing multi-agent conversations using LLM-as-judge.

    Features:
    - Loads conversations from two arbitrary paths
    - Evaluates conversation pairs using multiple dimensions
    - Saves individual evaluation logs and aggregated results
    - Generates CSV reports and visualization charts
    """

    def __init__(self, config_path: str, env_path: str):
        """
        Initialize the LLM evaluator.

        Args:
            config_path: Path to config.json with LLM settings
            env_path: Path to .env file with AWS credentials
        """
        self.config = self._load_config(config_path)
        self.env_path = env_path
        self._load_environment()
        self.client = self._create_bedrock_client()
        self._load_prompt_templates()

    def _load_config(self, config_path: str) -> Dict:
        """Load LLM configuration from config.json."""
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("llm", {})

    def _load_environment(self):
        """Load environment variables from .env file."""
        load_dotenv(self.env_path, override=True)
        api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        if not api_key:
            raise ValueError(
                "AWS_BEARER_TOKEN_BEDROCK environment variable not set.\n"
                "Please create a .env file with your AWS Bedrock token."
            )

    def _create_bedrock_client(self):
        """Create and return a Bedrock runtime client."""
        region = self.config.get("region", "us-east-1")
        client = boto3.client(service_name="bedrock-runtime", region_name=region)
        return client

    def _load_prompt_templates(self):
        """Load all prompt templates from prompts module."""
        self.prompt_templates = {}

        # Get all prompt variables from prompts module
        for attr_name in dir(prompts):
            if attr_name.endswith("_PROMPT") and not attr_name.startswith("_"):
                # Convert BELIEVABILITY_PROMPT -> believability
                dimension_name = attr_name.replace("_PROMPT", "").lower()
                self.prompt_templates[dimension_name] = getattr(prompts, attr_name)

    def get_available_dimensions(self) -> List[str]:
        """Get list of all available evaluation dimensions."""
        return list(self.prompt_templates.keys())

    def load_conversations(
        self, path1: str, path2: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Load conversations from two JSON files.

        Args:
            path1: Path to first conversation file
            path2: Path to second conversation file

        Returns:
            Tuple of two conversation lists
        """
        with open(path1, "r", encoding="utf-8") as f:
            conversations_a = json.load(f)

        with open(path2, "r", encoding="utf-8") as f:
            conversations_b = json.load(f)

        return conversations_a, conversations_b

    def create_session_folder(
        self,
        parent_dir: Optional[str] = None,
        conv_path1: Optional[str] = None,
        conv_path2: Optional[str] = None,
    ) -> str:
        """
        Create a timestamped session folder for storing evaluation results.

        Args:
            parent_dir: Optional parent directory to create session folder in.
                       If None, uses default results/ directory.
            conv_path1: Optional path to first conversation file (for extracting model name)
            conv_path2: Optional path to second conversation file (for extracting model name)

        Returns:
            Path to the created session folder
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Extract model names from paths if provided
        model_suffix = ""
        if conv_path1 and conv_path2:
            model1 = self._extract_model_name(conv_path1)
            model2 = self._extract_model_name(conv_path2)
            # Replace slashes with dashes for filesystem compatibility
            model1_safe = model1.replace("/", "-")
            model2_safe = model2.replace("/", "-")
            model_suffix = f"_{model1_safe}_vs_{model2_safe}"

        if parent_dir:
            session_dir = Path(parent_dir) / f"eval_{timestamp}{model_suffix}"
        else:
            session_dir = (
                Path(__file__).parent / "results" / f"eval_{timestamp}{model_suffix}"
            )

        session_dir.mkdir(parents=True, exist_ok=True)

        return str(session_dir)

    def _extract_model_name(self, conv_path: str) -> str:
        """
        Extract model name from conversation file path.

        Args:
            conv_path: Path to conversation file

        Returns:
            Model name in format "category/model" (e.g., "baseline/gpt4omini" or "ours/kimi-k2-0905")
        """
        path = Path(conv_path)
        # Assume structure: .../category/model_name/conversations.json
        # Get the parent directory (model name) and its parent (category)
        model_name = path.parent.name
        category = path.parent.parent.name
        return f"{category}/{model_name}"

    def save_metadata(self, session_dir: str, metadata: Dict):
        """
        Save session metadata to metadata.json.

        Args:
            session_dir: Path to session folder
            metadata: Metadata dictionary to save
        """
        metadata_path = Path(session_dir) / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def save_all_logs(self, session_dir: str, all_logs: List[Dict]):
        """
        Save all evaluation logs to a single JSON file.

        Args:
            session_dir: Path to session folder
            all_logs: List of all evaluation log data
        """
        log_path = Path(session_dir) / "evaluation_logs.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(all_logs, f, indent=2)

    def call_llm(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        """
        Make a completion call to Bedrock Claude API.

        Args:
            prompt: The evaluation prompt with conversation pairs
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens in the response

        Returns:
            The LLM response text
        """
        model_id = self.config.get(
            "model_id", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
        )

        # Prepare the request body for Claude via Bedrock
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        # Make the API call
        response = self.client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        # Parse the response
        response_body = json.loads(response["body"].read())

        # Extract text from response content blocks
        response_text = ""
        for block in response_body.get("content", []):
            if block.get("type") == "text":
                response_text += block.get("text", "")

        return response_text

    def _parse_llm_response(self, response_text: str) -> Dict:
        """
        Parse JSON response from LLM.

        Args:
            response_text: Raw LLM response text

        Returns:
            Parsed JSON dictionary
        """
        # Try to extract JSON from the response
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # If parsing fails, return raw response
        return {"raw_response": response_text, "parsing_error": True}

    def _format_conversation_text(self, conversation: Dict) -> str:
        """
        Format a conversation dictionary into readable text.

        Args:
            conversation: Conversation dictionary with participants, timestamp, location, conversation

        Returns:
            Formatted conversation string
        """
        participants = ", ".join(conversation.get("participant", []))
        timestamp = conversation.get("timestamp", "N/A")
        location = conversation.get("location", "N/A")
        conv_text = conversation.get("conversation", "")

        formatted = f"""
Participants: {participants}
Timestamp: {timestamp}
Location: {location}

Conversation:
{conv_text}
"""
        return formatted.strip()

    def _evaluate_dimension(
        self, conv_a: Dict, conv_b: Dict, dimension: str, prompt_template: str
    ) -> Dict:
        """
        Evaluate a specific dimension for a conversation pair.

        Args:
            conv_a: Conversation from first file
            conv_b: Conversation from second file
            dimension: Name of the evaluation dimension
            prompt_template: Prompt template with {conversations_a} and {conversations_b} placeholders

        Returns:
            Parsed LLM response dictionary
        """
        # Format conversations
        conv_a_text = self._format_conversation_text(conv_a)
        conv_b_text = self._format_conversation_text(conv_b)

        # Fill in the prompt template
        prompt = prompt_template.format(
            conversations_a=conv_a_text, conversations_b=conv_b_text
        )

        # Call LLM
        response_text = self.call_llm(prompt)

        # Parse response
        parsed_response = self._parse_llm_response(response_text)

        return parsed_response

    def run_evaluation(
        self,
        conv_path1: str,
        conv_path2: str,
        dimensions: Optional[List[str]] = None,
        parent_dir: Optional[str] = None,
        max_conversations: Optional[int] = None,
    ) -> str:
        """
        Run complete evaluation pipeline.

        Args:
            conv_path1: Path to first conversation file
            conv_path2: Path to second conversation file
            dimensions: List of evaluation dimensions (e.g., ["believability"]).
                       If None, evaluates all available dimensions.
            parent_dir: Optional parent directory for session folder.
            max_conversations: Maximum number of conversations to evaluate.
                              If None, uses minimum of both files.

        Returns:
            Path to session directory with results
        """
        # Use all available dimensions if none specified
        if dimensions is None:
            dimensions = self.get_available_dimensions()
            print("No dimensions specified, using all available dimensions")

        print("=" * 70)
        print("LLM-as-Judge Evaluation System")
        print("=" * 70)
        print()

        # Step 1: Load conversations
        print("Step 1: Loading conversations...")
        print(f"  Path 1: {conv_path1}")
        print(f"  Path 2: {conv_path2}")
        conversations_a, conversations_b = self.load_conversations(
            conv_path1, conv_path2
        )
        print(f"  Loaded {len(conversations_a)} conversations from Path 1")
        print(f"  Loaded {len(conversations_b)} conversations from Path 2")

        # Use minimum length for 1-to-1 pairing
        num_pairs = min(len(conversations_a), len(conversations_b))

        # Apply max_conversations limit if specified
        if max_conversations is not None:
            if max_conversations > num_pairs:
                print(
                    f"  WARNING: Requested {max_conversations} conversations but only {num_pairs} available"
                )
            num_pairs = min(num_pairs, max_conversations)

        print(f"  Will evaluate {num_pairs} conversation pairs (1-to-1 mapping)")
        print()

        # Step 2: Create session folder
        print("Step 2: Creating session folder...")
        session_dir = self.create_session_folder(
            parent_dir=parent_dir, conv_path1=conv_path1, conv_path2=conv_path2
        )
        print(f"  Session directory: {session_dir}")
        print()

        # Step 3: Prepare metadata
        print("Step 3: Preparing metadata...")
        metadata = {
            "session_id": Path(session_dir).name,
            "timestamp": datetime.now().isoformat(),
            "input_files": {
                "conversation_path_1": conv_path1,
                "conversation_path_2": conv_path2,
            },
            "evaluation_dimensions": dimensions,
            "num_conversations_path1": len(conversations_a),
            "num_conversations_path2": len(conversations_b),
            "num_evaluations": num_pairs * len(dimensions),
            "llm_config": {
                "provider": self.config.get("provider", "bedrock"),
                "model_id": self.config.get("model_id", "unknown"),
                "region": self.config.get("region", "us-east-1"),
            },
            "status": "in_progress",
        }
        self.save_metadata(session_dir, metadata)
        print("  Metadata saved")
        print()

        # Step 4: Run evaluations
        print("Step 4: Running evaluations...")
        print(f"  Total evaluations: {num_pairs * len(dimensions)}")
        print()

        all_results = []
        eval_counter = 0

        for pair_idx in range(num_pairs):
            conv_a = conversations_a[pair_idx]
            conv_b = conversations_b[pair_idx]

            print(f"  Evaluating pair {pair_idx + 1}/{num_pairs}...")

            for dimension in dimensions:
                eval_counter += 1
                eval_id = f"eval_{eval_counter:03d}"

                print(f"    - Dimension: {dimension} ({eval_id})")

                # Get prompt template for this dimension≥
                if dimension not in self.prompt_templates:
                    print(
                        f"      WARNING: No prompt template found for dimension '{dimension}', skipping"
                    )
                    continue

                prompt_template = self.prompt_templates[dimension]

                # Evaluate using the dimension's prompt template
                llm_response = self._evaluate_dimension(
                    conv_a, conv_b, dimension, prompt_template
                )

                # Prepare log data
                log_data = {
                    "eval_id": eval_id,
                    "pair_index": pair_idx,
                    "dimension": dimension,
                    "conversation_a": {
                        "source": conv_path1,
                        "participants": conv_a.get("participant", []),
                        "timestamp": conv_a.get("timestamp", "N/A"),
                        "location": conv_a.get("location", "N/A"),
                    },
                    "conversation_b": {
                        "source": conv_path2,
                        "participants": conv_b.get("participant", []),
                        "timestamp": conv_b.get("timestamp", "N/A"),
                        "location": conv_b.get("location", "N/A"),
                    },
                    "llm_response": llm_response,
                    "evaluation_timestamp": datetime.now().isoformat(),
                }

                all_results.append(log_data)

                # Print scores for tracking
                score_a = llm_response.get("version_a_score", "N/A")
                score_b = llm_response.get("version_b_score", "N/A")
                print(f"      ✓ Completed - Scores: Path1={score_a}, Path2={score_b}")

        print()
        print("  All evaluations completed!")
        print()

        # Step 5: Save all evaluation logs
        print("Step 5: Saving evaluation logs...")
        self.save_all_logs(session_dir, all_results)
        print("  Evaluation logs saved to: evaluation_logs.json")
        print()

        # Step 6: Aggregate results
        print("Step 6: Aggregating results...")
        aggregated = self.aggregate_results(all_results, conv_path1, conv_path2)

        # Save aggregated results
        agg_path = Path(session_dir) / "aggregated_results.json"
        with open(agg_path, "w", encoding="utf-8") as f:
            json.dump(aggregated, f, indent=2)
        print("  Aggregated results saved to: aggregated_results.json")
        print()

        # Step 7: Generate CSV report
        print("Step 7: Generating CSV report...")
        self.generate_csv_report(session_dir, aggregated)
        print("  CSV report saved to: aggregated_results.csv")
        print()

        # Step 8: Plot results
        print("Step 8: Generating visualization...")
        self.plot_results(session_dir, aggregated)
        print("  Chart saved to: evaluation_chart.png")
        print()

        # Step 9: Update metadata status
        metadata["status"] = "completed"
        metadata["completion_time"] = datetime.now().isoformat()
        self.save_metadata(session_dir, metadata)

        print("=" * 70)
        print("Evaluation Complete!")
        print(f"Results saved to: {session_dir}")
        print("=" * 70)

        return session_dir

    def aggregate_results(
        self, all_results: List[Dict], path1: str, path2: str
    ) -> Dict:
        """
        Aggregate evaluation results across all conversation pairs.

        Args:
            all_results: List of all individual evaluation logs
            path1: Path to first conversation file (for labeling)
            path2: Path to second conversation file (for labeling)

        Returns:
            Dictionary with aggregated scores per dimension
        """
        # Group results by dimension
        dimension_results = {}

        for result in all_results:
            dimension = result["dimension"]
            llm_response = result["llm_response"]

            if dimension not in dimension_results:
                dimension_results[dimension] = {"scores_a": [], "scores_b": []}

            # Extract scores (handle different response formats)
            score_a = llm_response.get("version_a_score")
            score_b = llm_response.get("version_b_score")

            if score_a is not None:
                dimension_results[dimension]["scores_a"].append(score_a)
            if score_b is not None:
                dimension_results[dimension]["scores_b"].append(score_b)

        # Calculate averages
        aggregated = {"path_1": path1, "path_2": path2, "dimensions": {}}

        for dimension, scores in dimension_results.items():
            scores_a = scores["scores_a"]
            scores_b = scores["scores_b"]

            aggregated["dimensions"][dimension] = {
                "path_1_average": sum(scores_a) / len(scores_a) if scores_a else 0,
                "path_2_average": sum(scores_b) / len(scores_b) if scores_b else 0,
                "num_evaluations": len(scores_a),
            }

        return aggregated

    def generate_csv_report(self, session_dir: str, aggregated: Dict):
        """
        Generate CSV report from aggregated results.

        Args:
            session_dir: Path to session folder
            aggregated: Aggregated results dictionary
        """
        csv_path = Path(session_dir) / "aggregated_results.csv"

        dimensions = list(aggregated["dimensions"].keys())

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            header = ["Model"] + dimensions
            writer.writerow(header)

            # Write row for path 1
            row1 = [aggregated["path_1"]]
            for dim in dimensions:
                row1.append(f"{aggregated['dimensions'][dim]['path_1_average']:.2f}")
            writer.writerow(row1)

            # Write row for path 2
            row2 = [aggregated["path_2"]]
            for dim in dimensions:
                row2.append(f"{aggregated['dimensions'][dim]['path_2_average']:.2f}")
            writer.writerow(row2)

    def plot_results(self, session_dir: str, aggregated: Dict):
        """
        Generate bar chart visualization of evaluation results.

        Args:
            session_dir: Path to session folder
            aggregated: Aggregated results dictionary
        """
        dimensions = list(aggregated["dimensions"].keys())
        path1_scores = [
            aggregated["dimensions"][dim]["path_1_average"] for dim in dimensions
        ]
        path2_scores = [
            aggregated["dimensions"][dim]["path_2_average"] for dim in dimensions
        ]

        # Create bar chart
        x = range(len(dimensions))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        bars1 = ax.bar(
            [i - width / 2 for i in x], path1_scores, width, label=aggregated["path_1"]
        )
        bars2 = ax.bar(
            [i + width / 2 for i in x], path2_scores, width, label=aggregated["path_2"]
        )

        # Customize chart
        ax.set_xlabel("Evaluation Dimensions", fontsize=12)
        ax.set_ylabel("Average Score", fontsize=12)
        ax.set_title("LLM-as-Judge Evaluation Results", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(dimensions)
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{height:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

        plt.tight_layout()

        # Save chart
        chart_path = Path(session_dir) / "evaluation_chart.png"
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()


def main():
    """Example usage of the LLMEvaluator."""
    # Initialize evaluator
    evaluator = LLMEvaluator(
        config_path="bedrock_example/config.json", env_path="bedrock_example/.env"
    )

    # Define evaluation parameters
    conv_path1 = (
        "../results/1a_conversation_subset/baseline/gpt4omini/conversations.json"
    )
    conv_path2 = "../results/1a_conversation_subset/ours/gpt4omini/conversations.json"

    # Run evaluation with all dimensions (or specify: dimensions=["believability"])
    session_dir = evaluator.run_evaluation(
        conv_path1=conv_path1,
        conv_path2=conv_path2,
    )

    print("\n✓ Evaluation completed successfully!")
    print(f"Results saved to: {session_dir}")


if __name__ == "__main__":
    main()
