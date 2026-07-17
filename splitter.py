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
    from reader import find_files

    files = find_files(r"D:\data conquest\rework\AMF brain rework", file_types=[".py", ".md", ".json",".docx"])

    for file in files:
        chunks = split_file_into_chunks(file)
        print(f"{file} -> {len(chunks)} chunks")