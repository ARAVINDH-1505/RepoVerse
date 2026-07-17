# Daily Log

## Day 1 - July 1, 2026
- Built Reader: finds files by type, skips junk folders like venv and .git
- Built Splitter: breaks file text into overlapping chunks
- Learned: rglob runs once per file type, so we loop over a list of types to search multiple extensions
- Learned: overlap between chunks helps avoid cutting meaning off at chunk edges

## Day 2 - July 3, 2026
- Built Number-maker (Embedder): turns text chunks into 384-number embeddings using sentence-transformers, running locally, no cost
- Tested it on my own MCP project files, got correct chunk and embedding counts
- Built Storage: saves chunks and embeddings to disk using Chroma, data persists between runs
- Built Searcher: turns a question into numbers, finds closest matching chunks from storage
- Learned: question and code must use the same embedding tool, or comparing them makes no sense
- Tested Searcher on my own MCP project files, got relevant chunks back with correct source files
- Next: build the Answerer, using Groq to turn matching chunks into a real written answer

## Day 3 - July 8, 2026
- Built Answerer: sends question and matching code chunks to Groq, gets a real written answer
- Built Front door: FastAPI endpoint /query that ties the whole system together
- Tested full flow end to end - asked real questions about my own code, got correct answers with source files
- Found a bug: storage mixes data from different projects since it's one shared collection - needs fixing
- Phase 1 is functionally complete
- Next: fix storage isolation, then decide on Phase 2 priorities

## Day 4 - July 15, 2026
- Fixed the storage isolation bug: each project folder now gets its own separate
  storage space in Chroma, using a hash of the folder path as the collection name
- Updated Searcher, Answerer, and the API to all require a folder_path, so the
  right project's data is always used
- Found a new bug while testing: when a folder wasn't indexed yet, the AI still
  answered with made-up information instead of saying it didn't know
- Learned: this is called hallucination - AI making up an answer when it has
  no real information. Fixed by checking for empty results before ever calling
  the AI, so it's not even given the chance to guess
- Built indexer.py: a proper script to index any folder from the terminal,
  instead of editing storage.py by hand each time
- Learned: JSON needs double backslashes or forward slashes for Windows paths,
  single backslashes break JSON parsing
- Next: index RepoVerse's own codebase and test the full fixed flow end to end