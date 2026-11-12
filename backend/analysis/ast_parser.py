import ast
from pathlib import Path
from backend.ingestion.repository_scanner import scan_python_files

def get_call_name(node):
    if isinstance(node,ast.Name):
        return node.id 
    if isinstance(node,ast.Attribute):
        parent = get_call_name(node.value)
        return f"{parent}.{node.attr}"if parent else node.attr 
    return '<dynamic>'

def parse_python_file(file_path: str | Path) -> dict:
    file_path = Path(file_path).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"file not found: {file_path}")
    if not file_path.is_file():
        raise IsADirectoryError(f"expected a file: {file_path}")
    source_code = file_path.read_text(encoding='utf-8' , errors='replace')
    try:
        tree = ast.parse(source_code,filename=str(file_path))
    except SyntaxError as error:
        return {
            "file_path": str(file_path),
            "parse_success": False,
            "imports": [],
            "functions": [],
            "classes": [],
            "function_calls": [],
            "error": {
                "message": error.msg,
                "line": error.lineno,
                "offset": error.offset,
                "source_line": error.text
            }
        }