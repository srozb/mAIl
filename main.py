"""
Main script for email classification.

This script processes and classifies the content of multiple email files,
utilizing a specified machine learning model. It extracts metadata, body content,
and attachment details from each email file, passes the data to a classification
function, and outputs the results as JSON.

Features:
- Supports classification of email files using various machine learning models.
- Extracts email metadata (e.g., subject, sender, recipients) and attachments.
- Measures inference time for each email classification.
- Handles errors gracefully, logging issues for unsupported or problematic files.

Command-Line Arguments:
- `-m` or `--model`: Specify the name of the model to use for classification
  (default: "gemma2:27b").
- `-H` or `--host`: Set the `OLLAMA_HOST` environment variable for model communication.
- `email_files`: Paths to the email files to be classified. Accepts multiple files.

Dependencies:
- Requires `email_parser` for extracting email content and metadata.
- Requires `classifier` for performing classification using a machine learning model.

Functions:
- `process_emails(email_files, model_name)`: Processes a list of email files, 
    classifies their content, and returns the results as a list of dictionaries.

Example Usage:
    python main.py -m gemma2:27b data/email1.eml data/email2.msg
"""

import os
import argparse
import json
import time
from src.email_parser import parse_email
from src.classifier import classify_email


def process_emails(email_files, model_name):
    """Process multiple email files and classify their content."""
    results = []
    for email_file in email_files:
        try:
            parsed_email = parse_email(email_file)
            content = (
                f"Subject: {parsed_email['subject']}\n"
                f"From: {parsed_email['from']}\n"
                f"To: {parsed_email['to']}\n\n{parsed_email['body']}"
            )
            start_time = time.time()
            classification_result = classify_email(
                content,
                attachments=parsed_email.get("attachments", []),
                model_name=model_name,
            )
            inference_time = time.time() - start_time
            results.append(
                {
                    "file": email_file,
                    "email_metadata": {
                        "subject": parsed_email["subject"],
                        "from": parsed_email["from"],
                        "to": parsed_email["to"],
                    },
                    "classification": classification_result.get("Classification"),
                    "certainty_level": classification_result.get("Certainty Level"),
                    "tags": classification_result.get("Tags"),
                    "reason": classification_result.get("Reason"),
                    "inference_time": inference_time,
                }
            )
        except IndexError as e:
            results.append({"file": email_file, "error": str(e)})
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Classify content from multiple email files."
    )

    # Add the argument for the model name
    parser.add_argument(
        "-m",
        "--model",
        required=False,
        default="gemma2:27b",
        help="Specify the model to use for classification.",
    )

    # Add the OLLAMA_HOST environment variable flag
    parser.add_argument(
        "-H", "--host", required=False, help="Set the OLLAMA_HOST environment variable."
    )

    parser.add_argument(
        "email_files", nargs="+", help="Paths to the email files (.eml or .msg)."
    )
    args = parser.parse_args()

    if args.host:
        os.environ["OLLAMA_HOST"] = args.host

    processed = process_emails(args.email_files, args.model)
    print(json.dumps(processed))
