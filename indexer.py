import sys
from reader import find_files
from splitter import split_file_into_chunks
from embedder import create_embeddings
from storage import store_chunks


def index_folder(folder_path: str, file_types: list[str] = [".py", ".md", ".json"]) -> None:
    files = find_files(folder_path, file_types=file_types)

    if not files:
        print("No matching files found.")
        return

    for file in files:
        chunks = split_file_into_chunks(file)
        embeddings = create_embeddings(chunks)
        store_chunks(chunks, embeddings, str(file), folder_path)
        print(f"Indexed {len(chunks)} chunks from {file}")

    print(f"Done. Indexed {len(files)} files from {folder_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please give a folder path. Example: python indexer.py ./my_project")
        sys.exit(1)

    target_folder = sys.argv[1]
    index_folder(target_folder)