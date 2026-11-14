import json
from backend.analysis.ast_parser import parse_repository
REPO_PATH = r"D:\Repomedic"
result = parse_repository(REPO_PATH)
print("\n=======REPOMEDIC AST ANALYSIS==========\n")
print(json.dumps(result, indent=4))
print('\n=======================================')