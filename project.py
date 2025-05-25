import ast
import os
import logging
import json
from dotenv import load_dotenv

# Optional: switch between local AST or LLM graph generation
USE_LOCAL_AST = True  # Set to False to use Mistral LLM flow

# Only needed for LLM-based graph generation
from mistralai import Mistral

# Local AST graph module
import generate_code  # assuming generate_code.py is in the same directory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key
load_dotenv()
API_KEY = os.getenv("MISTRAL_KEY")
if not API_KEY and not USE_LOCAL_AST:
    logger.error("MISTRAL_KEY not found in environment variables.")
    raise EnvironmentError("Missing MISTRAL_KEY")

# Initialize Mistral client if needed
mistral_client = None
if not USE_LOCAL_AST:
    try:
        mistral_client = Mistral(api_key=API_KEY)
    except Exception as e:
        logger.exception("Failed to initialize Mistral client.")
        raise

# Constants
MODEL_NAME = "open-mistral-7b"
SYSTEM_MESSAGE = (
    "You are a Python developer. Return only the code or JSON without markdown or explanations."
)
MAX_ATTEMPTS = 5


def build_graph_extraction_prompt(source_code: str) -> str:
    return (
        "Analyze the following Python code. Nodes and edges are annotated with comments:\n"
        "- Nodes: lines starting with '# NODE: <name>'\n"
        "- Edges: lines starting with '# EDGES: <source> -> <target>, ...'\n\n"
        "Extract the graph elements as JSON with two arrays: 'nodes' and 'edges'.\n"
        "Each edge should be an object with 'source' and 'target' fields.\n"
        "Output ONLY the JSON object, nothing else.\n\n"
        "Here is the code:\n\n"
        f"{source_code}\n"
    )


def chat_with_model(system_message: str, user_message: str) -> str:
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
    prompt = build_graph_extraction_prompt(base_code)
    for attempt in range(MAX_ATTEMPTS):
        logger.info(f"Attempt {attempt + 1} to generate graph JSON.")
        try:
            raw_output = chat_with_model(SYSTEM_MESSAGE, prompt)
            stripped = raw_output.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                json.loads(stripped)  # Validate
                return stripped
            else:
                logger.warning("LLM output not valid JSON format.")
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
    return None


def convert_llm_json_to_mermaid(llm_output_json_str: str) -> str:
    graph = json.loads(llm_output_json_str)
    mermaid = "graph TD\n"
    for node in graph.get("nodes", []):
        node_name = node if isinstance(node, str) else node.get("name", "unknown")
        mermaid += f"    {node_name}[{node_name}]\n"
    for edge in graph.get("edges", []):
        mermaid += f"    {edge['source']} --> {edge['target']}\n"
    return mermaid


def save_code_to_file(code: str, filename: str):
    try:
        with open(filename, "w") as f:
            f.write(code)
        logger.info(f"Saved file: {filename}")
    except Exception as e:
        logger.exception(f"Failed to save file {filename}")
        raise


def main():
    if USE_LOCAL_AST:
        logger.info("Running local AST graph generator.")
        import subprocess
        subprocess.run(["python", "generate_code.py"], check=True)

        logger.info("AST graph generated: ast_graph.png")
        return

    # LLM-based flow
    base_code_path = "sort.py"
    mermaid_output_path = "diagram.mmd"

    if not os.path.exists(base_code_path):
        logger.error(f"{base_code_path} not found.")
        return

    with open(base_code_path, "r") as f:
        base_code = f.read()

    graph_json_str = generate_graph_json(base_code)
    if not graph_json_str:
        logger.error("Failed to generate graph JSON after multiple attempts.")
        return

    mermaid_code = convert_llm_json_to_mermaid(graph_json_str)
    save_code_to_file(mermaid_code, mermaid_output_path)
    logger.info(f"Mermaid diagram code saved to {mermaid_output_path}")


if __name__ == "__main__":
    main()
