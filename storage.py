import chromadb

client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(name="repoverse")


def store_chunks(chunks: list[str], embeddings: list[list[float]], file_path: str) -> None:
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

    files = find_files("D:\VELAI THEDUM PADALAM\MCP", file_types=[".py", ".md", ".json"])

    for file in files:
        chunks = split_file_into_chunks(file)
        embeddings = create_embeddings(chunks)
        store_chunks(chunks, embeddings, str(file))
        print(f"Stored {len(chunks)} chunks from {file}")

    print("Total chunks in storage:", collection.count())