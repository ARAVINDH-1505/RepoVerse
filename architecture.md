# RepoVerse - Architecture

RepoVerse is a tool that reads a code folder, understands it, and answers questions
about it, showing which files the answer came from.

## The Flow

1. Reader finds all relevant files in a folder
2. Splitter breaks each file into small chunks
3. Number-maker turns each chunk into numbers (embeddings)
4. Storage saves those chunks and numbers to disk
5. When a question is asked, Searcher turns the question into numbers too,
   and finds the closest matching chunks
6. Answerer (not built yet) sends the question and matching chunks to an AI model,
   and returns a written answer

## Components

### Reader (`reader.py`)
Takes a folder path and a list of file types (like .py, .md, .json).
Walks through the folder and all folders inside it.
Skips junk folders: .git, venv, .venv, __pycache__, node_modules.
Returns a list of file paths that match the given file types.

### Splitter (`splitter.py`)
Takes a single file and reads its full text.
Breaks the text into chunks of about 500 characters each.
Each chunk overlaps the previous one by 50 characters, so meaning
does not get cut off at the edges.
Returns a list of text chunks.

### Number-maker / Embedder (`embedder.py`)
Uses a free local model (sentence-transformers, "all-MiniLM-L6-v2") to turn
each text chunk into a list of 384 numbers.
These numbers represent the meaning of the text, not the exact words.
Runs fully on the local machine, no internet needed after first download, no cost.

### Storage (`storage.py`) - updated
Each project now gets its own separate storage space inside Chroma.
The folder path is turned into a short unique code (using a hash), and used
as the collection name. This means two different projects can never mix data,
even if both are indexed on the same machine.

### Searcher (`searcher.py`) - updated
Now requires a folder_path, so it always searches inside the correct
project's storage, never a shared one.

### Answerer (`answerer.py`) - updated
Now checks if the Searcher found anything at all before calling Groq.
If nothing is found, it returns an honest "not indexed yet" message instead
of letting the AI guess or make something up.

### Indexer (`indexer.py`) - new
A standalone script that runs the full indexing chain (Reader, Splitter,
Number-maker, Storage) on any folder, given as a command line argument.
This replaces manually editing storage.py every time a new folder needs indexing.

Example:
python indexer.py "D:/path/to/any/project"

### Front door / API (not built yet)
A FastAPI endpoint, likely `/query`, that ties the whole flow together.
User sends a question, gets back an answer with source files.