import os
import ast

def parse_source_code(source_code: str, filename="<string>") -> list:
    """
    Parses raw source code string and returns function metadata.
    Used for testing and dynamic analysis.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []

    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node)
            
            args = []
            # Handle args safely (Python 3.8+ compatible)
            all_args = node.args.args + getattr(node.args, 'kwonlyargs', [])
            
            for arg in all_args:
                annotation = None
                if arg.annotation:
                    try:
                        annotation = ast.unparse(arg.annotation)
                    except:
                        annotation = "complex"
                args.append({"name": arg.arg, "annotation": annotation})

            functions.append({
                "name": node.name,
                "args": args,
                "returns": ast.unparse(node.returns) if node.returns else None,
                "has_docstring": bool(docstring),
                "docstring": docstring,
                "start_line": node.lineno,
                "indent": node.col_offset
            })
            
    return functions

def parse_file(file_path: str) -> dict:
    """
    Parses a single Python file and returns file metadata including functions.
    """
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            source = f.read()
        except UnicodeDecodeError:
            return {}

    functions = parse_source_code(source, filename=file_path)

    return {
        "file_path": file_path,
        "functions": functions
    }

def parse_path(path: str) -> list:
    """
    Recursively scans a directory (or single file) for Python files and parses them.
    REQUIRED BY main_app.py
    """
    results = []
    
    # 1. Handle Single File
    if os.path.isfile(path):
        if path.endswith(".py"):
            data = parse_file(path)
            if data and data.get("functions"):
                results.append(data)
        return results

    # 2. Handle Directory
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                
                # Skip virtual environment folders
                if "venv" in full_path or "site-packages" in full_path:
                    continue
                    
                data = parse_file(full_path)
                if data and data.get("functions"):
                    results.append(data)
    
    return results