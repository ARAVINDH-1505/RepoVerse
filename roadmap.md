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
- [x] Add: shared config.py for all settings (API key, model, chunk size, iteration limits)
- [x] Add: shared groq_client.py with retries and empty-response checks, used by every module
- [x] Fix: switched from retired Groq models (llama-3.1-8b-instant, llama-3.3-70b-versatile)
      to openai/gpt-oss-20b, which is currently active on the free tier
- [ ] Known issue: main.py's folder_path is not restricted - fine for local use,
      needs restricting before any public deployment
- [ ] Known issue: bug_finder.py truncates files with its own hardcoded limit,
      not config.py's MAX_TOTAL_CONTEXT_CHARS - should be unified
- [ ] Improvement: add a small pause between per-file Groq calls in the summarizer
      to avoid triggering rate limits reactively
- [ ] Support more file types (.js, .ts, .java, etc.)
- [ ] Docker setup for easy running
- [ ] GitHub integration (point at a repo URL, not just a local folder)
- [ ] Frontend (simple UI to ask questions and see answers)

## Phase 3: Agentic Features

- [x] Repo Summarizer - map-reduce design: summarizes each file separately first,
      then combines those into one project summary, checked for completeness and
      accuracy in a loop
- [x] Bug Finder - finds real issues in code, filters out false positives
- [x] Fix Explainer - explains a bug and proposes a fix, checks the fix before showing it
- [ ] Decide: GitHub repo support (URL-based, not just local folder)
