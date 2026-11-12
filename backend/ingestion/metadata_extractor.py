import os
from pathlib import Path
from collections import Counter
from backend.ingestion.repository_scanner import scan_python_files

ignored_dirs = {
    '.git',
    '.venv',
    'venv',
    '__pycache__',
    'node_modules',
    '.idea',
    'dist',
    'build'
}

config_files = {
    'requirements.txt',
    'pyproject.toml',
    'setup.cfg',
    'setup.py',
    'Pipfile',
    "poetry.lock",
    "environment.yml",
    "pytest.ini",
    "tox.ini",
    "Dockerfile"
}

def extract_repository_metadata(repo_path: str | Path) -> dict:
    repo_path = Path(repo_path).resolve()
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository not found: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Expected a directory: {repo_path}")

    total_files = 0
    total_directories = 0
    extension_counts = Counter()
    configuration_files = []
    directory_structure = []

    for root,dirs,files in os.walk(repo_path):
        dirs[:] = [
            directory for directory in dirs if directory not in ignored_dirs
        ]
        total_directories+=len(dirs)
        current_dir = Path(root)
        if current_dir!=repo_path:
            directory_structure.append(str(current_dir.relative_to(repo_path)))

        for file in files:
            total_files+=1
            file_path = Path(file)
            extension = file_path.suffix.lower()
            if extension:
                extension_counts[extension]+=1
            else:
                extension_counts['[no extension]']+=1
            if file in config_files:
                configuration_files.append(str((current_dir/file).relative_to(repo_path)))
    python_files = scan_python_files(repo_path)
    metadata = {
        "repository_path": str(repo_path),
        "total_files": total_files,
        "total_directories": total_directories,
        "python_files": len(python_files),
        "configuration_files": sorted(configuration_files),
        "configuration_files_count": len(configuration_files),
        "extension_counts": dict(extension_counts),
        "directory_structure": sorted(directory_structure)
    }
    return metadata