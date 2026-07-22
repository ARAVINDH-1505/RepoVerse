# RepoVerse - Roadmap

## Phase 1: Core Backend (No frontend yet)

Goal: Point at a folder, ask a question, get an answer with the source file shown.

- [x] Reader - finds code files in a folder, skips junk folders
- [x] Splitter - breaks each file into small overlapping chunks
- [x] Number-maker (Embedder) - turns each chunk into numbers using sentence-transformers
- [x] Storage - saves chunks and their numbers using Chroma, so we don't redo work
- [x] Searcher - takes a question, finds the closest matching chunks
- [x] Answerer - sends the question and matching chunks to Groq, gets a real answer
- [x] Front door (API) - a FastAPI endpoint that ties everything together

## Phase 2: Fixes and Improvements

- [x] Fix: storage mixing data across different projects
- [x] Fix: AI making up answers when no matching code is found
- [x] Add: indexer script to index any folder from the terminal, no code editing needed
- [ ] Support more file types (.js, .ts, .java, etc.)
- [ ] Docker setup for easy running
- [ ] GitHub integration (point at a repo URL, not just a local folder)
- [ ] Frontend (simple UI to ask questions and see answers)

## Phase 3: Agentic Features

- [x] Repo Summarizer - reads project code, writes a summary, checks its own
      work for completeness and accuracy, improves itself in a loop
- [ ] Bug Finder - finds real issues in code, filters out false positives
- [ ] Fix Explainer - explains a bug and proposes a fix, checks the fix before showing it
- [ ] Decide: GitHub repo support (URL-based, not just local folder)
