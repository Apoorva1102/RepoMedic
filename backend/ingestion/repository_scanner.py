ignored_dirs = {
    'git',
    '.venv',
    'venv',
    '__pycache__',
    'mode_modules',
    '.idea',
    'dist',
    'build'
}

import os
from pathlib import Path 

def scan_python_files(repo_path: str | Path)->list[Path]:
    #Scan a python repository and return all relevant python file paths
    repo_path = Path(repo_path).resolve()
    if not repo_path.exists():
        raise FileNotFoundError(f"repository not found: {repo_path}")
    if not repo_path.is_dir():
        raise NotADirectoryError(f"expected a directory: {repo_path}")
    python_files = []

    for root,dirs,files in os.walk(repo_path):
        dirs[:] = [
            directory for directory in dirs if directory not in ignored_dirs
        ]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root)/file 
                relative_path = file_path.relative_to(repo_path)
                python_files.append(relative_path)
    return sorted(python_files)


