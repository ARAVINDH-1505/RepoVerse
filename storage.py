import chromadb
import hashlib
from pathlib import Path

client = chromadb.PersistentClient(path="./chroma_data")


def get_collection_name(folder_path: str) -> str:
    absolute_path = str(Path(folder_path).resolve())
    hash_value = hashlib.md5(absolute_path.encode()).hexdigest()[:10]
    return f"project_{hash_value}"


def get_collection(folder_path: str):
    name = get_collection_name(folder_path)
    return client.get_or_create_collection(name=name)


def store_chunks(chunks: list[str], embeddings: list[list[float]], file_path: str, folder_path: str) -> None:
    collection = get_collection(folder_path)
    ids = [f"{file_path}_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"source": file_path} for _ in chunks]
    )


if __name__ == "__main__":
    from reader import find_files
    from splitter import split_file_into_chunks
    from embedder import create_embeddings

    target_folder = "./my_project"
    files = find_files(target_folder, file_types=[".py", ".md", ".json"])

    for file in files:
        chunks = split_file_into_chunks(file)
        embeddings = create_embeddings(chunks)
        store_chunks(chunks, embeddings, str(file), target_folder)
        print(f"Stored {len(chunks)} chunks from {file}")