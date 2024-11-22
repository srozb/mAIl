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
                model_name=model_name
            )
            inference_time = time.time() - start_time
            results.append({
                "file": email_file,
                "email_metadata": {
                    "subject": parsed_email['subject'],
                    "from": parsed_email['from'],
                    "to": parsed_email['to']
                },
                "classification": classification_result.get("Classification"),
                "certainty_level": classification_result.get("Certainty Level"),
                "tags": classification_result.get("Tags"),
                "reason": classification_result.get("Reason"),
                "inference_time": inference_time
            })
        except Exception as e:
            results.append({
                "file": email_file,
                "error": str(e)
            })
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify content from multiple email files.")
    
    # Add the argument for the model name
    parser.add_argument("-m", "--model", required=False, default="gemma2:27b", help="Specify the model to use for classification.")
    
    # Add the OLLAMA_HOST environment variable flag
    parser.add_argument("-H", "--host", required=False, help="Set the OLLAMA_HOST environment variable.")
    
    parser.add_argument("email_files", nargs="+", help="Paths to the email files (.eml or .msg).")
    args = parser.parse_args()

    if args.host:
        os.environ["OLLAMA_HOST"] = args.host

    results = process_emails(args.email_files, args.model)
    print(json.dumps(results))
