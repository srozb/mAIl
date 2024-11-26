"""
Module for summarizing and benchmarking email classification results.

This module provides functionality to:
- Parse log files containing JSON-formatted classification results.
- Summarize the results by calculating accuracy, inference time, and error rates
  for different models and categories (safe and malicious emails).
- Generate a Markdown table comparing the performance of models across categories.
- Save the benchmarking results to a `benchmark.md` file.

Usage:
    Run this script directly to process log files in the specified directory
    and generate a Markdown summary of the results.

Functions:
    parse_log_file(log_file): Parses a log file and extracts JSON-formatted results.
    summarize_results(log_dir, category): Summarizes accuracy and inference time
                                           for a given category of emails.
    generate_markdown_table(safe_summary, malicious_summary): Creates a Markdown table
                                                              comparing model performance.
    main(): Main function to generate benchmarking results and save them to a file.

Dependencies:
    - Python standard library: os, json, glob, statistics
"""

import os
import json
import glob
import statistics


def parse_log_file(log_file):
    """Parse a log file containing one JSON line per result."""
    results = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                json_line = json.loads(line.strip())
                if isinstance(json_line, list) and len(json_line) == 1:
                    results.append(json_line[0])
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {log_file}: {e}")
    return results


def summarize_results(log_dir, category):
    """Summarize results from log files for a given category (safe or malicious)."""
    summary = {}
    for log_file in glob.glob(f"{log_dir}/test_{category}_*.log"):
        model_name = (
            os.path.basename(log_file)
            .replace(f"test_{category}_", "")
            .replace(".log", "")
            .replace("_", ":")
        )
        results = parse_log_file(log_file)

        correct = 0
        total = len(results)
        inference_times = []

        for result in results:
            if "error" in result:
                # Count any error as a mistake
                continue

            if "classification" in result and "inference_time" in result:
                if result["classification"] is None:
                    # Count uncertain response as mistake
                    continue
                is_correct = (
                    category == "safe" and result["classification"].lower() == "safe"
                ) or (
                    category == "malicious"
                    and result["classification"].lower() != "safe"
                )
                if is_correct:
                    correct += 1
                inference_times.append(result["inference_time"])

        accuracy = correct / total * 100 if total > 0 else 0
        avg_inference_time = (
            statistics.mean(inference_times) if inference_times else float("nan")
        )

        summary[model_name] = {
            "accuracy": accuracy,
            "avg_inference_time": avg_inference_time,
            "total": total,
        }

    return summary


def generate_markdown_table(safe_summary, malicious_summary):
    """Generate a markdown table comparing models across categories."""
    table = "| Model          | Safe Accuracy (%) | Malicious Accuracy (%) "
    table += "| Avg Inference Time (s) |\n"
    table += "|----------------|-------------------|-------------------------"
    table += "|-------------------------|\n"

    all_models = set(safe_summary.keys()).union(malicious_summary.keys())

    for model in sorted(all_models):
        safe_acc = safe_summary.get(model, {}).get("accuracy", "N/A")
        mal_acc = malicious_summary.get(model, {}).get("accuracy", "N/A")
        avg_time_safe = safe_summary.get(model, {}).get("avg_inference_time", "N/A")
        avg_time_mal = malicious_summary.get(model, {}).get("avg_inference_time", "N/A")

        avg_time = (
            statistics.mean(
                [
                    t
                    for t in [avg_time_safe, avg_time_mal]
                    if isinstance(t, (int, float))
                ]
            )
            if avg_time_safe != "N/A" and avg_time_mal != "N/A"
            else "N/A"
        )

        table += f"| {model:<14} | {safe_acc:<17.2f} | {mal_acc:<23.2f} | {avg_time:<23.2f} |\n"

    return table


def main():
    """
    Main function to summarize benchmarking results and generate a Markdown table.

    This function performs the following steps:
    1. Summarizes results for both "safe" and "malicious" email classifications
       by analyzing log files in the specified directory.
    2. Generates a Markdown table comparing model performance metrics such as
       accuracy, inference time, and error rates.
    3. Writes the generated Markdown table to a `benchmark.md` file.
    4. Prints a confirmation message indicating the location of the results.

    Returns:
        None
    """

    log_dir = "."  # Directory containing the log files
    safe_summary = summarize_results(log_dir, "safe")
    malicious_summary = summarize_results(log_dir, "malicious")

    markdown_table = generate_markdown_table(safe_summary, malicious_summary)

    # Write the markdown table to a file
    with open("benchmark.md", "w", encoding="utf-8") as f:
        f.write("# Benchmark Results\n\n")
        f.write(markdown_table)

    print("✅ Benchmark results saved to benchmark.md")


if __name__ == "__main__":
    main()
