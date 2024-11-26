"""
Module for classifying email content and attachments using a Large Language Model (LLM).

This module defines functions to:
- Filter and sanitize Markdown content from LLM responses.
- Use an LLM to classify emails based on their content and attachments.
- Provide detailed classification output, including classification type,
  reasoning, tags, and certainty level.

Dependencies:
    - os: For environment variable management.
    - langchain_core.prompts.ChatPromptTemplate: For creating LLM prompts.
    - langchain_ollama.llms.OllamaLLM: For interacting with the Ollama LLM.
"""

import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


def filter_markdown(content: str) -> str:
    """
    Removes Markdown formatting (e.g., triple backticks) from the content.

    Args:
        content (str): The input string potentially containing Markdown formatting.

    Returns:
        str: The sanitized string with Markdown formatting removed.
    """

    content = content.strip()
    if content.startswith("```") and content.endswith("```"):
        content = "\n".join(content.splitlines()[1:-1])
    return content


def classify_email(content: str, attachments: list, model_name: str) -> dict:
    """
    Classifies an email's content and attachments using a specified LLM.

    This function analyzes the email content and metadata for attachments,
    then uses a Large Language Model to determine whether the email is Spam,
    Phishing, Malicious, or Safe. It returns a JSON-compatible dictionary
    with classification details.

    Args:
        content (str): The body of the email to classify.
        attachments (list): A list of dictionaries representing attachment metadata.
            Each dictionary should include:
            - 'name' (str): The name of the attachment.
            - 'type' (str): The MIME type of the attachment.
            - 'size' (int): The size of the attachment in bytes.
        model_name (str): The name of the LLM model to use for classification.

    Returns:
        dict: A dictionary containing the following keys:
            - "Classification" (str): The determined classification (e.g., "Safe", "Malicious").
            - "Tags" (list): Key tags reflecting the email's content.
            - "Reason" (str): The reasoning behind the classification.
            - "Certainty Level" (int): A certainty score (0-100).

    Raises:
        ValueError: If the LLM response cannot be parsed as JSON.
    """

    template = (
        "You are an expert in email security."
        "Analyze the following email content including attachment metadata if "
        "available:\n"
        "{email_content}\n\n"
        "Attachments: {attachments}\n\n"
        "Provide the following as JSON output:\n"
        "1. Classification: Is this email Spam, Phishing, Malicious, or Safe?\n"
        "2. Tags: List a few key tags reflecting the content.\n"
        "3. Reason: Explain the reasoning behind the classification in one or "
        "two sentences.\n"
        "4. Certainty Level: Provide a certainty score for your classification "
        "between 0-100%.\n\n"
        "Factors to consider include suspicious sender, url, "
        "file names, file types (e.g., '.exe', '.js', '.gz'), "
        "double extensions (e.g. '.pdf.js'), rare mime types, "
        "and other techniques employed by threat actors.\n"
        "Do not include percentage signs in the Certainty Level, "
        "and ensure all strings are JSON-safe. Return only json, "
        "without additional remarks so I can parse it easily.\n"
    )

    attachment_descriptions = "\n".join(
        [
            f"Name: {a['name']}, Type: {a['type']}, Size: {a['size']} bytes"
            for a in attachments
        ]
    )

    ollama_host = os.getenv("OLLAMA_HOST")
    base_url = (
        "http://" + ollama_host if ollama_host else None
    )  # Use None if OLLAMA_HOST is not defined

    model = OllamaLLM(model=model_name, base_url=base_url, temperature=0)
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model  # pylint: disable=E1131
    result = chain.invoke(
        {
            "email_content": content,
            "attachments": attachment_descriptions or "No attachments",
        }
    )
    result = filter_markdown(result)

    try:
        return json.loads(result)
    except json.JSONDecodeError as e:
        raise ValueError("The LLM response could not be parsed as JSON.") from e
