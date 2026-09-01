from pathlib import Path

def split_file_into_chunks(file_path: Path, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


if __name__ == "__main__":
    import sys
    from reader import find_files
    import config

    if len(sys.argv) < 2:
        print("Please give a folder path. Example: python splitter.py ./my_project")
        sys.exit(1)

    target_folder = sys.argv[1]
    files = find_files(target_folder, file_types=config.DEFAULT_FILE_TYPES)

    for file in files:
        chunks = split_file_into_chunks(file, chunk_size=config.CHUNK_SIZE, overlap=config.CHUNK_OVERLAP)
        print(f"{file} -> {len(chunks)} chunks")
