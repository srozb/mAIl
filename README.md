# mAIl: Email Classification Tool for Spam, Phishing, and Malicious Content

**mAIl** is a Python-based tool designed to classify email messages (in `.eml` and `.msg` formats) into categories like **Spam**, **Phishing**, **Malicious**, or **Safe**. It uses large language models (LLMs) for classification and provides a detailed output that includes content keywords, reasoning, and a certainty level (0-100%).

## Features

* Classify `.eml` and `.msg` email formats.
* Uses **Ollama** and **LangChain** to process emails and classify content.
* Outputs classifications, content keywords, reasoning, and a certainty level.
* Supports multiple email files passed as command-line arguments.
* Prints the results as structured JSON.

## Installation

1. **Clone the repository**:

  ```bash
  git clone https://github.com/srozb/mAIl.git
  cd mAIl
  ```

Create a virtual environment using pipenv:

```bash
pipenv install
```

Make sure you have access to an Ollama daemon.

```bash
ollama run <model_name> 'Why is the sky blue?'
```

## Usage

### Classifying Multiple Emails

You can classify multiple `.eml` or `.msg` files by running the following command:

```bash
python main.py email1.eml email2.msg email3.eml
```

The tool will process all the files and print a structured JSON output with classification results, content keywords, and reasoning for each email.

Sample Command:

```bash
python main.py ./data/sample_emails/test_email.eml ./data/sample_emails/test_email.msg
```

Sample Output:

```json
[
    {
        "file": "test_email.eml",
        "email_metadata": {
            "subject": "Invoice for last month",
            "from": "billing@example.com",
            "to": "user@example.com"
        },
        "classification": "Safe",
        "certainty_level": 97,
        "content_keywords": ["invoice", "billing"],
        "reason": "The email appears to be a legitimate billing communication."
    },
    {
        "file": "test_email.msg",
        "email_metadata": {
            "subject": "Your account has been compromised",
            "from": "phisher@example.com",
            "to": "victim@example.com"
        },
        "classification": "Phishing",
        "certainty_level": 95,
        "content_keywords": ["account", "compromised", "reset password"],
        "reason": "The email contains language indicative of phishing attempts."
    }
]
```

### Example: Specify a Custom Model

```bash
python main.py -m gemma2:35b email1.eml email2.msg
```

### Example: Specify a Custom Host

```bash
python main.py -H http://your-ollama-host:11435 email1.eml email2.msg
```

### Environment Variable OLLAMA_HOST

You can also set the `OLLAMA_HOST` environment variable directly before running the script. If not provided, the default behavior is used.

## Project Structure

* src/
  * email_parser.py: Contains logic for parsing .eml and .msg email files.
  * classifier.py: Contains logic for classifying email content using an LLM model.
  * utils.py: Contains utility functions like saving the classification results.
* data/: Example email files to test the tool.
* main.py: Main script to classify emails passed as arguments.
* README.md: Project documentation.

## Dependencies

* `Python 3.x`
* `pipenv` for managing dependencies
* `python-magic` for file type detection
* `eml-parser` for parsing .eml files
* `extract-msg` for parsing .msg files
* LangChain and Ollama for email classification using large language models (LLMs)

## License

This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## Acknowledgments

LangChain and Ollama for their amazing LLM-powered solutions.
Python community for creating useful libraries like python-magic and eml-parser.