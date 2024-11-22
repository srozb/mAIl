import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

def filterMarkdown(content: str) -> str:
    content = content.strip()
    if content.startswith('```') and content.endswith('```'):
        content = "\n".join(content.splitlines()[1:-1])
    return content

def classify_email(content: str, attachments: list, model_name: str) -> dict:
    template=(
        "You are an expert in email security. Analyze the following email content including attachment metadata if available:\n"
        "{email_content}\n\n"
        "Attachments: {attachments}\n\n"
        "Provide the following as JSON output:\n"
        "1. Classification: Is this email Spam, Phishing, Malicious, or Safe?\n"
        "2. Tags: List a few key tags reflecting the content.\n"
        "3. Reason: Explain the reasoning behind the classification in one or two sentences.\n"
        "4. Certainty Level: Provide a certainty score for your classification between 0-100%.\n\n"
        "Factors to consider include suspicious sender, url, file names, file types (e.g., '.exe', '.js', '.gz'), double extensions (e.g. '.pdf.js'), rare mime types, and other techniques employed by threat actors."
        "Do not include percentage signs in the Certainty Level, and ensure all strings are JSON-safe. Return only json, without additional remarks so I can parse it easily."
    )

    attachment_descriptions = "\n".join(
        [f"Name: {a['name']}, Type: {a['type']}, Size: {a['size']} bytes" for a in attachments]
    )

    ollama_host = os.getenv("OLLAMA_HOST")
    base_url = "http://" + ollama_host if ollama_host else None  # Use None if OLLAMA_HOST is not defined

    model = OllamaLLM(model=model_name, base_url=base_url, temperature=0)
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    result = chain.invoke({
        "email_content":content,
        "attachments":attachment_descriptions or "No attachments"
    })
    result = filterMarkdown(result)

    try:
        import json
        return json.loads(result)
    except json.JSONDecodeError:
        raise ValueError("The LLM response could not be parsed as JSON. Check the prompt or input content.")
