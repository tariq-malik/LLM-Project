import ast
import graphviz
import logging
import os
import sys

# Configure basic logging for essential messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ASTGraphGenerator(ast.NodeVisitor):
    def __init__(self):
        # Initialize a new directed graph
        self.graph = graphviz.Digraph(comment='Abstract Syntax Tree')

    def visit(self, node):
        # Use the object's ID as a unique identifier for the node in the graph
        node_id = str(id(node))
        # The label for the node will simply be its type name
        label = type(node).__name__
        self.graph.node(node_id, label)

        # Iterate over direct child nodes of the current AST node
        for child in ast.iter_child_nodes(node):
            # Recursively visit the child node to add it and its children to the graph
            self.visit(child)
            # Create an edge from the current node to its child
            self.graph.edge(node_id, str(id(child)))


def create_ast_graph_from_file(filepath):
    """
    Reads a Python file, parses its AST, and generates a graph image.
    Args:
        filepath (str): The path to the Python file to analyze.
    """
    if not os.path.exists(filepath):
        logger.error(f"File not found: '{filepath}'")
        sys.exit(1) # Exit if file doesn't exist

    # Read the source code from the specified file
    with open(filepath, 'r') as file:
        source_code = file.read()

    # Parse the source code into an Abstract Syntax Tree
    syntax_tree = ast.parse(source_code)
    # Initialize the graph generator
    graph_generator = ASTGraphGenerator()
    # Traverse the AST to build the graph
    graph_generator.visit(syntax_tree)

    output_filename_base = 'ast_graph'
    output_format = 'png'

    try:
        # Render the graph to a PNG file
        graph_generator.graph.render(output_filename_base, format=output_format, cleanup=True)
        logger.info(f"AST graph saved as '{output_filename_base}.{output_format}'")
    except Exception as e:
        logger.error(f"Failed to render AST graph. Ensure Graphviz is installed and in PATH. Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if a file path argument is provided
    if len(sys.argv) < 2:
        logger.error("Usage: python generate_code.py <path_to_python_file>")
        sys.exit(1)

    # Get the target file path from command-line arguments
    target_file = sys.argv[1]
    # Create the AST graph
    create_ast_graph_from_file(target_file)
