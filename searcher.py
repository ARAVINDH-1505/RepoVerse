from embedder import create_embeddings
from storage import get_collection


def search(query: str, folder_path: str, top_k: int = 5) -> dict:
    collection = get_collection(folder_path)
    query_embedding = create_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


if __name__ == "__main__":
    question = "how does the database connection work"
    results = search(question, folder_path="./my_project")

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print("Source:", meta["source"])
        print("Chunk:", doc[:200])
        print("---")