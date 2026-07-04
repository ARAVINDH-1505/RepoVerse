import chromadb
from embedder import create_embeddings

client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(name="repoverse")


def search(query: str, top_k: int = 5) -> dict:
    query_embedding = create_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


if __name__ == "__main__":
    question = "what is MCP"
    results = search(question)

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print("Source:", meta["source"])
        print("Chunk:", doc[:200])
        print("---")