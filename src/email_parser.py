import magic
import extract_msg
import eml_parser
from typing import Dict, List


def determine_file_type(file_path: str) -> str:
    """Determine the file type of the provided email file."""
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    if mime_type == "message/rfc822":
        return "eml"
    elif mime_type == "application/vnd.ms-outlook":
        return "msg"
    else:
        raise ValueError(
            "Unsupported file type. Only .eml and .msg files are supported."
        )


def extract_eml_attachments(eml_parsed_data: dict) -> List[Dict]:
    """Extracts attachments from a parsed .eml file."""
    attachments = []
    if "attachment" not in eml_parsed_data:
        return attachments
    for attachment in eml_parsed_data["attachment"]:
        attachments.append(
            {
                "name": attachment["filename"],
                "type": attachment["mime_type"],
                "size": attachment["size"],
            }
        )
    return attachments


def parse_eml_email(file_path: str) -> Dict:
    """Parses an .eml file and extracts relevant information."""
    with open(file_path, "rb") as f:
        ep = eml_parser.EmlParser(include_raw_body=True)
        parsed_eml = ep.decode_email_bytes(f.read())
    return {
        "subject": parsed_eml["header"]["subject"],
        "from": parsed_eml["header"]["from"],
        "to": parsed_eml["header"]["to"],
        "body": parsed_eml["body"][0]["content"],
        "attachments": extract_eml_attachments(parsed_eml),
    }


def extract_msg_attachments(
    msg: extract_msg.Message,
) -> List[Dict]:
    """Extracts attachments from a parsed .msg file."""
    attachments = []
    for attachment in msg.attachments:
        attachments.append(
            {
                "name": attachment.longFilename or attachment.shortFilename,
                "type": magic.from_buffer(attachment.data, mime=True),
                "size": len(attachment.data),
            }
        )
    return attachments


def parse_msg_email(file_path: str) -> Dict:
    """Parses an Outlook .msg file and extracts relevant information."""
    msg = extract_msg.openMsg(file_path)
    return {
        "subject": msg.subject,
        "from": msg.sender,
        "to": ", ".join([x.formatted for x in msg.recipients]),
        "body": msg.body,
        "attachments": extract_msg_attachments(msg),
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
