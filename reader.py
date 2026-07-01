from pathlib import Path

def find_files(folder_path: str, file_types: list[str]) -> list[Path]:
    folder = Path(folder_path)

    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder_path}")

    ignore_folders = {".git", "venv", "__pycache__", ".venv", "node_modules"}

    found_files = []

    for extension in file_types:
        for file_path in folder.rglob(f"*{extension}"):
            if any(part in ignore_folders for part in file_path.parts):
                continue
            found_files.append(file_path)

    return found_files


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Please give a folder path. Example: python reader.py ./my_project")
        sys.exit(1)

    target_folder = sys.argv[1]
    files = find_files(target_folder, file_types=[".py", ".md", ".json"])

    print(f"Found {len(files)} files:")
    for f in files:
        print(f)