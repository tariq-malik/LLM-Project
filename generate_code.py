import ast
import graphviz

class ASTGraphGenerator(ast.NodeVisitor):
    def __init__(self):
        self.graph = graphviz.Digraph(comment='Abstract Syntax Tree')

    def visit(self, node):
        node_id = str(id(node))
        label = type(node).__name__
        self.graph.node(node_id, label)
        for child in ast.iter_child_nodes(node):
            child_id = str(id(child))
            self.graph.edge(node_id, child_id)
            self.visit(child)

def create_ast_graph_from_file(filepath):
    with open(filepath, 'r') as file:
        source_code = file.read()

    syntax_tree = ast.parse(source_code)
    graph_generator = ASTGraphGenerator()
    graph_generator.visit(syntax_tree)
    graph_generator.graph.render('ast_graph', format='png', cleanup=True)
    print("AST graph has been saved as ast_graph.png")

if __name__ == "__main__":
    create_ast_graph_from_file('calculator.py')
