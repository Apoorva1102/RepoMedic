from repository_scanner import scan_python_files

REPO_PATH = r'D:\Repomedic'

try:
    files = scan_python_files(REPO_PATH)
    print(f'total files found: {len(files)}')
    print('\ndiscovered files:')
    for file in files:
        print(file)
except (FileNotFoundError , NotADirectoryError) as error:
    print(f"error: {error}")