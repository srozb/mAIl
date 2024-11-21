import magic
import extract_msg
import eml_parser
from typing import Dict

def determine_file_type(file_path: str) -> str:
    """Determine the file type of the provided email file."""
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    if mime_type == "message/rfc822":
        return "eml"
    elif mime_type == "application/vnd.ms-outlook":
        return "msg"
    else:
        raise ValueError("Unsupported file type. Only .eml and .msg files are supported.")

def parse_eml_email(file_path: str) -> Dict:
    """Parses an .eml file and extracts relevant information."""
    with open(file_path, "rb") as f:
        ep = eml_parser.EmlParser(include_raw_body=True)
        parsed_eml = ep.decode_email_bytes(f.read())
    return {
        "subject": parsed_eml['header']['subject'],
        "from": parsed_eml['header']['from'],
        "to": parsed_eml['header']['to'],
        "body": parsed_eml['body'][0]['content'],
    }

def parse_msg_email(file_path: str) -> Dict:
    """Parses an Outlook .msg file and extracts relevant information."""
    msg = extract_msg.openMsg(file_path)
    return {
        "subject": msg.subject,
        "from": msg.sender,
        "to": msg.recipients,
        "body": msg.body,
    }

def parse_email(file_path: str) -> Dict:
    """Detects file type and parses email content accordingly."""
    file_type = determine_file_type(file_path)
    if file_type == "eml":
        return parse_eml_email(file_path)
    elif file_type == "msg":
        return parse_msg_email(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
