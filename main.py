import ast
import os
import logging
import json
import subprocess
from dotenv import load_dotenv
from mistralai import Mistral
from flask import Flask, send_file
import os

# Use local AST analysis instead of LLM-based graph generation
USE_LOCAL_AST = True

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("MISTRAL_KEY")

# Initialize Mistral client if the API key is available
mistral_client = None
if API_KEY:
    try:
        mistral_client = Mistral(api_key=API_KEY)
        logger.info("Mistral client initialized.")
    except Exception as e:
        logger.exception("Failed to initialize Mistral client.")
else:
    logger.warning("Mistral API key not found. LLM-based Dockerfile generation will not work.")

# Constants used in LLM communication
MODEL_NAME = "open-mistral-7b"
SYSTEM_MESSAGE = (
    "You are a Python developer. Return only the code or JSON without markdown or explanations."
)
MAX_ATTEMPTS = 5

DOCKERFILE_SYSTEM_MESSAGE = (
    "You are a Docker expert. Generate a Dockerfile for a Python application. "
    "The application uses `python-dotenv` and `graphviz` (Python library). "
    "It also requires the system-level `graphviz` utility (which provides the `dot` executable) for image generation. "
    "Output ONLY the Dockerfile content, without any markdown or explanations."
)

def build_graph_extraction_prompt(source_code: str) -> str:
    # Not used when USE_LOCAL_AST is True
    raise NotImplementedError("LLM functionality for graph extraction is disabled when USE_LOCAL_AST is True.")

def chat_with_model(system_message: str, user_message: str) -> str:
    # Sends a prompt to the Mistral LLM and returns the response content
    if not mistral_client:
        raise RuntimeError("Mistral client not initialized. Check MISTRAL_KEY.")
    try:
        response = mistral_client.chat.complete(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.exception("LLM chat completion failed.")
        raise

def generate_graph_json(base_code: str) -> str | None:
    # Not used when using local AST analysis
    raise NotImplementedError("LLM functionality for graph extraction is disabled when USE_LOCAL_AST is True.")

def convert_llm_json_to_mermaid(llm_output_json_str: str) -> str:
    # Not used when using local AST analysis
    raise NotImplementedError("LLM functionality for graph extraction is disabled when USE_LOCAL_AST is True.")

def save_code_to_file(code: str, filename: str):
    # Writes given code to a file
    try:
        with open(filename, "w") as f:
            f.write(code)
        logger.info(f"Saved file: {filename}")
    except Exception as e:
        logger.exception(f"Failed to save file {filename}")
        raise

def generate_dockerfile():
    # Uses the Mistral LLM to generate a Dockerfile for the current Python project
    if not mistral_client:
        logger.error("Mistral client not available. Cannot generate Dockerfile via LLM. Please set MISTRAL_KEY.")
        return

    logger.info("Attempting to generate Dockerfile via Mistral LLM...")

    user_prompt = (
        "Generate a Dockerfile. "
        "Use the `python:3.10-slim-buster` base image. "
        "Set the working directory to `/app`. "
        "Copy `requirements.txt` first and install Python dependencies using `pip install --no-cache-dir -r requirements.txt`. "
        "Install the system-level `graphviz` package using `apt-get` and then, in the *same RUN instruction*, "
        "add a command to check for the `dot` executable: `which dot || (echo \"ERROR: 'dot' executable not found after installation!\" && exit 1)`. "
        "Ensure these commands are chained with `&&`. "
        "Then, copy all other application files. "
        "And the EXPOSE should be 5000"
        "The application's main entry point is `main.py` and it should be run with `CMD [\"python\", \"main.py\"]`. "
        "Output ONLY the raw Dockerfile content, without any markdown code blocks or explanations. "
        "Ensure the Dockerfile is clean and only includes necessary steps for these requirements."
    )

    try:
        dockerfile_content = chat_with_model(DOCKERFILE_SYSTEM_MESSAGE, user_prompt)
        dockerfile_content = dockerfile_content.strip()

        # Strip out any markdown-style formatting just in case
        if dockerfile_content.startswith("```dockerfile"):
            dockerfile_content = dockerfile_content[len("```dockerfile"):].strip()
        elif dockerfile_content.startswith("```Dockerfile"):
            dockerfile_content = dockerfile_content[len("```Dockerfile"):].strip()
        elif dockerfile_content.startswith("```"):
            dockerfile_content = dockerfile_content[len("```"):].strip()
        if dockerfile_content.endswith("```"):
            dockerfile_content = dockerfile_content[:-len("```")].strip()

        # Basic sanity check before saving
        if "FROM" in dockerfile_content and "COPY" in dockerfile_content and "RUN" in dockerfile_content and "CMD" in dockerfile_content:
            save_code_to_file(dockerfile_content, "Dockerfile")
            logger.info("Dockerfile generated successfully via LLM.")
        else:
            logger.error("LLM generated content does not look like a valid Dockerfile.")
            logger.debug(f"Invalid Dockerfile content: \n{dockerfile_content}")

    except Exception as e:
        logger.error(f"Failed to generate Dockerfile via LLM: {e}")

def main():
    # Main entry point for the script
    generate_dockerfile()

    if USE_LOCAL_AST:
        logger.info("Running local AST graph generator.")

        target_python_file = 'calculator.py'

        if not os.path.exists(target_python_file):
            logger.error(f"Target Python file '{target_python_file}' not found.")
            return

        try:
            subprocess.run(
                ["python", "generate_code.py", target_python_file],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"generate_code.py executed successfully for {target_python_file}.")

            if os.path.exists("ast_graph.png"):
                logger.info("AST graph generated: ast_graph.png")
            else:
                logger.error("ast_graph.png was not created by generate_code.py.")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running generate_code.py: {e}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            raise

        except FileNotFoundError:
            logger.error("generate_code.py not found.")
            raise

    else:
        logger.info("Running LLM-based graph generator (disabled for this AST setup).")

app = Flask(__name__)
@app.route('/image')
def serve_image():
    image_path = 'ast_graph.png'
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    else:
        return "Image not found", 404
if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=5000, debug=True)
    
