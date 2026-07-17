from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(chunks: list[str]) -> list[list[float]]:
    embeddings = model.encode(chunks)
    return embeddings.tolist()


if __name__ == "__main__":
    from reader import find_files
    from splitter import split_file_into_chunks

    files = find_files(r"D:\data conquest\rework\AMF brain rework", file_types=[".py", ".md", ".json",".docx"])

    for file in files:
        chunks = split_file_into_chunks(file)
        embeddings = create_embeddings(chunks)
        print(f"{file} -> {len(chunks)} chunks -> {len(embeddings)} embeddings")
        print(f"Each embedding has {len(embeddings[0])} numbers")