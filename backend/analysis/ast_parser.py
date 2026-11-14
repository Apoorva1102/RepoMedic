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
    imports=[]
    functions=[]
    classes=[]
    function_calls=[]

    #for imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "module": alias.name,
                    "alias": alias.name,
                    "line": node.lineno          
                        })
        elif isinstance(node,ast.ImportFrom):
            imports.append({
                "module":node.module,
                "imported_names":[
                    {
                        "name": alias.name,
                        "alias": alias.asname 
                    }
                    for alias in node.names 
                ],
                "line": node.lineno
            })
        #functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            arguments = [
                arg.arg 
                for arg in (
                    node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                )
            ]
            if node.args.vararg:
                arguments.append("*" + node.args.vararg.arg)
            if node.args.kwarg:
                arguments.append("*" + node.args.kwargs.arg)
            functions.append({
                "name": node.name,
                "arguments":arguments,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "line": node.lineno,
                "end_line": node.end_lineno
            })
        #classes
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "bases": [
                    ast.unparse(base) for base in node.bases 
                ],
                "line": node.lineno,
                "end_line" : node.end_lineno
            })
        #function calls
        elif isinstance(node, ast.Call):
            function_calls.append({
                "name" : get_call_name(node.func),
                "line": node.lineno 
            })
    # sort results by their line numbers
    imports.sort(key=lambda item: item['line'])
    functions.sort(key=lambda item: item['line'])
    classes.sort(key=lambda item: item['line'])
    function_calls.sort(key=lambda item: item['line'])

    return {
        "file_path" : str(file_path),
        "parse_success": True,
        "imports": imports,
        "functions": functions,
        "classes": classes,
        "function_calls": function_calls,
        "error" : None 
    }

def parse_repository(repo_path: str | Path) -> dict:
    repo_path = Path(repo_path).resolve()
    python_files = scan_python_files(repo_path)
    parsed_files=[]

    for relative_path in python_files:
        file_path = repo_path/relative_path
        result = parse_python_file(file_path)
        result['relative_path'] = str(relative_path)
        parsed_files.append(result)
    successful = sum(
        1 for file in parsed_files if file['parse_success']
    )
    failed = len(parsed_files)-successful

    return {
        "repository_path": str(repo_path),
        "total_python_files": len(python_files),
        "successfully_parsed": successful,
        "failed_to_parse": failed,
        "files": parsed_files
    }