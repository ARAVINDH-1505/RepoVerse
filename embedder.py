from sentence_transformers import SentenceTransformer
import config

model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)

def create_embeddings(chunks: list[str]) -> list[list[float]]:
    embeddings = model.encode(chunks)
    return embeddings.tolist()


if __name__ == "__main__":
    import sys
    from reader import find_files
    from splitter import split_file_into_chunks

    if len(sys.argv) < 2:
        print("Please give a folder path. Example: python embedder.py ./my_project")
        sys.exit(1)

    target_folder = sys.argv[1]
    files = find_files(target_folder, file_types=config.DEFAULT_FILE_TYPES)

    for file in files:
        chunks = split_file_into_chunks(file, chunk_size=config.CHUNK_SIZE, overlap=config.CHUNK_OVERLAP)
        embeddings = create_embeddings(chunks)
        print(f"{file} -> {len(chunks)} chunks -> {len(embeddings)} embeddings")
        print(f"Each embedding has {len(embeddings[0])} numbers")
