import os

EXCLUDED_DIRS = {".git", "node_modules", "venv", ".env", ".gitignore", "package-lock.json", "package.json", "img", "env" }

def list_source_files(path, extensions=[".py", ".js", ".java", ".jsx", ".cjs"]):
    try:
        files = []
    
        for root, dirs, filenames in os.walk(path):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS] # Excluir carpetas específicas para mejorar el rendimiento
            for filename in filenames:
                if filename.endswith(tuple(extensions)):
                    files.append(os.path.join(root, filename))
        return files
    except Exception as e:
        print(f"⚠️ Failed to list source files: {path}: {e}")
        return None

def read_file_content(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
        
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"⚠️ Failed to read content {path}: {e}")
        return None
    
def extract_code(path, extensions=[".py", ".js", ".java", ".jsx", ".cjs"]):
    try:
        files = list_source_files(path, extensions)
        code = {}
        
        for file in files:
            content = read_file_content(file)
            if content:
                code[file] = content
        return code
    
    except Exception as e:
        print(f"⚠️ Failed to extract code: {path}: {e}")
        return None