import os
from groq import Groq
from searcher import search

client = Groq(api_key=os.environ["GROQ_API_KEY"])


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


def get_answer(question: str, folder_path: str) -> dict:
    results = search(question, folder_path)

    chunks = results["documents"][0]
    sources = [meta["source"] for meta in results["metadatas"][0]]

    if not chunks:
        return {
            "answer": "I could not find any indexed code for this folder. Please index it first.",
            "sources": []
        }

    prompt = build_prompt(question, chunks, sources)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    answer_text = response.choices[0].message.content

    return {
        "answer": answer_text,
        "sources": list(set(sources))
    }