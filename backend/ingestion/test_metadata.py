import json
from backend.ingestion.metadata_extractor import extract_repository_metadata

repo_path = r'D:\Repomedic'
try:
    metadata = extract_repository_metadata(repo_path)
    print("\n=========REPOMEDIC REPOSITORY REPORT===========\n")
    print(json.dumps(metadata,indent=4))
    print("\n===============================================\n")
except(FileNotFoundError,NotADirectoryError) as error:
    print(f"error: {error}")