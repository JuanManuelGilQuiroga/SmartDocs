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
                    func_name = node.child_by_field_name("name").text.decode()
                    body_node = node.child_by_field_name("body")
                    func_body = body_node.text.decode() if body_node else "No body"

                    if parent_class:
                        parsed_data["classes"][parent_class]["methods"][func_name] = func_body
                    else:
                        parsed_data["functions"][func_name] = func_body

                elif node.type == "class_definition":
                    class_name = node.child_by_field_name("name").text.decode()
                    parsed_data["classes"][class_name] = {"docstring": "No docstring", "methods": {}}

                    for child in node.children:
                        traverse(child, parent_class=class_name)

                elif node.type in ["import_statement", "import_from_statement"]:
                    parsed_data["imports"].append(node.text.decode())

            elif extension in [".js", ".cjs"]:
                if node.type == "function_declaration":
                    func_name = node.child_by_field_name("name").text.decode()
                    body_node = node.child_by_field_name("body")
                    func_body = body_node.text.decode() if body_node else "No body"
                    parsed_data["functions"][func_name] = func_body

                elif node.type == "class_declaration":
                    class_name = node.child_by_field_name("name").text.decode()
                    parsed_data["classes"][class_name] = {"docstring": "No docstring", "methods": {}}
                    
                # validacion para clases que comienzan con modele.exports
                elif node.type == "assignment_expression":
                    left_node = node.child_by_field_name("left")
                    right_node = node.child_by_field_name("right")
                    if left_node and left_node.type == "member_expression":
                        object_node = left_node.child_by_field_name("object")
                        property_node = left_node.child_by_field_name("property")

                        if object_node.text.decode() == "module" and property_node.text.decode() == "exports":
                            
                            class_name_node = right_node.child_by_field_name("name")
                            class_name = class_name_node.text.decode() if class_name_node else ""
                            
                            parsed_data["classes"][class_name] = {"docstring": "No docstring", "methods": {}}

                            # Buscar métodos dentro de la clase
                            class_body = right_node.child_by_field_name("body")
                            if class_body:
                                for child in class_body.children:
                                    if child.type == "method_definition":
                                        method_name_node = child.child_by_field_name("name")
                                        method_name = method_name_node.text.decode() if method_name_node else ""

                                        body_node = child.child_by_field_name("body")
                                        method_body = body_node.text.decode() if body_node else ""

                                        # Guardamos el método en la estructura
                                        parsed_data["classes"][class_name]["methods"][method_name] = method_body

                elif node.type == "method_definition" and parent_class:
                    method_name = node.child_by_field_name("name").text.decode()
                    body_node = node.child_by_field_name("body")
                    method_body = body_node.text.decode() if body_node else "No body"

                    if parent_class not in parsed_data["classes"]:
                        parsed_data["classes"][parent_class] = {"docstring": "No docstring", "methods": {}}

                    parsed_data["classes"][parent_class]["methods"][method_name] = method_body

                elif node.type == "import_statement":
                    parsed_data["imports"].append(node.text.decode())
            
            elif extension in [".jsx"]:
                if node.type == "function_declaration":
                    func_name = node.child_by_field_name("name").text.decode()
                    parsed_data["functions"][func_name] = ''

                elif node.type == "class_declaration":
                    class_name = node.child_by_field_name("name").text.decode()
                    parsed_data["classes"][class_name] = {"docstring": "No docstring", "methods": {}}

                elif node.type == "method_definition" and parent_class:
                    method_name = node.child_by_field_name("name").text.decode()

                    if parent_class not in parsed_data["classes"]:
                        parsed_data["classes"][parent_class] = {"docstring": "No docstring", "methods": {}}

                    parsed_data["classes"][parent_class]["methods"][method_name] = ''

                elif node.type == "import_statement":
                    parsed_data["imports"].append(node.text.decode())


            elif extension == ".java":
                if node.type == "class_declaration":
                    class_name = node.child_by_field_name("name").text.decode()
                    parsed_data["classes"][class_name] = {"docstring": "No docstring", "methods": {}}

                elif node.type == "method_declaration" and parent_class:
                    method_name = node.child_by_field_name("name").text.decode()
                    body_node = node.child_by_field_name("body")
                    method_body = body_node.text.decode() if body_node else "No body"

                    if parent_class not in parsed_data["classes"]:
                        parsed_data["classes"][parent_class] = {"docstring": "No docstring", "methods": {}}

                    parsed_data["classes"][parent_class]["methods"][method_name] = method_body

                elif node.type == "import_declaration":
                    parsed_data["imports"].append(node.text.decode())

            for child in node.children:
                traverse(child, parent_class if node.type not in ["class_declaration", "class_definition"] else node.child_by_field_name("name").text.decode())

        traverse(tree.root_node)
        
        # Validar que el archivo contenga clases o funciones antes de retornarlo
        if not parsed_data["classes"] and not parsed_data["functions"]:
            return None
        
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
            parsed_data = analyze_tree(tree, extension)

            if parsed_data:
                results[file] = parsed_data

        return results
    except Exception as e:
        print(f"⚠️  Failed to parse AST: {e}")
        return None
