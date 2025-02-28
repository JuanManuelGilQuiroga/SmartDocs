import os
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_java as tsjava

# cargar lengujaes
PYTHON = Language(tspython.language())
JAVASCRIPT = Language(tsjavascript.language())
JAVA = Language(tsjava.language())

LANGUAGE_MAP = {
    ".py": PYTHON,
    ".js": JAVASCRIPT,
    ".java": JAVA,
    ".jsx": JAVASCRIPT,
    ".cjs": JAVASCRIPT
}

# Crea un parser de tree-sitter dependiendo del lenguaje.
def get_parser(extension):
    if extension in LANGUAGE_MAP:
        parser = Parser(LANGUAGE_MAP[extension])
        return parser
    return None

def analyze_tree(tree, extension):
    parsed_data = {"classes": {}, "functions": {}, "imports": []}

    try:
        def traverse(node, parent_class=None):
            if extension == ".py":
                if node.type == "function_definition":
                    # child_by_field_name("name") es un método de los nodos en Tree-sitter. 
                    # Se está obteniendo el nombre de un método o clase dentro de un nodo
                    # En Tree-sitter, text devuelve un objeto en formato bytes, text.decode() Convierte los bytes en una cadena (str).

                    func_name = node.child_by_field_name("name").text.decode()
                    if parent_class:
                        # Si estamos dentro de una clase, guardamos el método en ella
                        parsed_data["classes"][parent_class]["methods"][func_name] = "No docstring"
                    else:
                        # Si no hay clase padre, es una función global
                        parsed_data["functions"][func_name] = "No docstring"
                
                elif node.type == "class_definition":
                    class_name = node.child_by_field_name("name").text.decode()
                    parsed_data["classes"][class_name] = {"docstring": "No docstring", "methods": {}}
                
                    # Recorrer los hijos de la clase y detectar métodos
                    for child in node.children:
                        traverse(child, parent_class=class_name)
                        
                elif node.type in ["import_statement", "import_from_statement"]:
                    parsed_data["imports"].append(node.text.decode())

            elif extension in [".js", ".jsx", ".cjs"]:
                if node.type == "function_declaration":
                    func_name = node.child_by_field_name("name").text.decode()
                    parsed_data["functions"][func_name] = "No docstring"
                
                elif node.type == "class_declaration":
                    class_name = node.child_by_field_name("name").text.decode()
                    parsed_data["classes"][class_name] = {"docstring": "No docstring", "methods": {}}
                
                elif node.type == "method_definition" and parent_class:
                    method_name = node.child_by_field_name("name").text.decode()
                    if parent_class not in parsed_data["classes"]:
                        parsed_data["classes"][parent_class] = {"docstring": "No docstring", "methods": {}}
                    parsed_data["classes"][parent_class]["methods"][method_name] = "No docstring"
                
                elif node.type == "import_statement":
                                parsed_data["imports"].append(node.text.decode())

            elif extension == ".java":
                if node.type == "class_declaration":
                    class_name = node.child_by_field_name("name").text.decode()
                    parsed_data["classes"][class_name] = {"docstring": "No docstring", "methods": {}}
                
                elif node.type == "method_declaration" and parent_class:
                    method_name = node.child_by_field_name("name").text.decode()
                    if parent_class not in parsed_data["classes"]:
                        parsed_data["classes"][parent_class] = {"docstring": "No docstring", "methods": {}}
                    parsed_data["classes"][parent_class]["methods"][method_name] = "No docstring"
                
                elif node.type == "import_declaration":
                    parsed_data["imports"].append(node.text.decode())

            for child in node.children:
                traverse(child, parent_class if node.type not in ["class_declaration", "class_definition"] else node.child_by_field_name("name").text.decode())

        traverse(tree.root_node)
        return parsed_data

    except Exception as e:
        print(f"⚠️  Failed to analyze tree: {e}")
        return None

    
    
# Recorre cada archivo, detecta el lenguaje, genera un parser y analiza el AST.
def ast_analysis(dic):
    results = {}
    
    try:
        for file, code in dic.items():
            extension = os.path.splitext(file)[1].lower()
            parser = get_parser(extension)
            if not parser:
                results[file] = "❌ Lenguaje no soportado"
                continue
            
            tree = parser.parse(code.encode())
            results[file] = analyze_tree(tree, extension)
        return results
    except Exception as e:
        print(f"⚠️  Failed to parse AST: {e}")
        return None
