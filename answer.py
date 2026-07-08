import os
from pathlib import Path


def get_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key

    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("GROQ_API_KEY="):
                _, value = line.split("=", 1)
                value = value.strip().strip('"').strip("'")
                if value:
                    os.environ["GROQ_API_KEY"] = value
                    return value

    raise RuntimeError(
        "Missing GROQ_API_KEY. Set it in your environment or create a .env file in the project root."
    )


def get_client():
    from groq import Groq

    return Groq(api_key=get_api_key())


def build_prompt(question: str, chunks: list[str], sources: list[str]) -> str:
    context_parts = []
    for chunk, source in zip(chunks, sources):
        context_parts.append(f"File: {source}\nCode:\n{chunk}")

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are a helpful code assistant. Answer the question using only the code below.
If the answer is not in the code, say you don't know.

{context}

Question: {question}
Answer:"""

    return prompt


def get_answer(question: str) -> dict:
    from searcher import search

    results = search(question)

    chunks = results["documents"][0]
    sources = [meta["source"] for meta in results["metadatas"][0]]

    prompt = build_prompt(question, chunks, sources)

    client = get_client()

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    answer_text = response.choices[0].message.content

    return {
        "answer": answer_text,
        "sources": list(set(sources))
    }


if __name__ == "__main__":
    result = get_answer("how does the database connection work")
    print("Answer:", result["answer"])
    print("Sources:", result["sources"])