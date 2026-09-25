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
- [x] Fix: main.py's folder_path now restricted to config.ALLOWED_PROJECT_ROOT (and its
      subfolders), enforced on every endpoint via validate_folder_path/validate_file_path
- [x] Fix: bug_finder.py now uses config.MAX_CHARS_PER_FILE, unified with the rest of the project
- [x] Fix: rate limiting solved properly - groq_client.py tracks real token usage in a rolling
      60s window and paces requests to stay under Groq's tokens-per-minute limit; replaced the
      earlier fixed per-file delay approach entirely
- [x] Add: requirements.txt for reproducible installs
- [x] Add: multi-language file support (.js, .ts, .java, .go, .rs, .cpp, .html, .css, etc.)
      for indexing/QA/Summarizer via config.DEFAULT_FILE_TYPES. Bug Finder intentionally stays
      .py-only, since its syntax check uses Python's own ast.parse
- [x] Add: /summarize, /bugs, /fix API endpoints - Summarizer, Bug Finder, and Fix Explainer
      are no longer CLI-only
- [ ] Docker setup for easy running
- [ ] GitHub integration (point at a repo URL, not just a local folder)
- [ ] Frontend (simple UI to ask questions and see answers)

## Phase 3: Agentic Features

- [x] Repo Summarizer - map-reduce design: summarizes each file separately first,
      then combines those into one project summary, checked for completeness and
      accuracy in a loop
- [x] Bug Finder - finds real issues in code, filters out false positives, verifies
      syntax claims deterministically via ast.parse instead of trusting the AI
- [x] Fix Explainer - explains a bug and proposes a fix, checks the fix before showing it
- [ ] Decide: GitHub repo support (URL-based, not just local folder)

## Phase 4: Full Product (in progress)

Goal: complete, working end to end in real time - GitHub URL support, Docker, and a
simple frontend, all built on the now-complete API surface (/query, /summarize, /bugs, /fix).

- [ ] GitHub URL support: clone + index a remote repo via a new endpoint
- [ ] Docker: one-command run for the whole API
- [ ] Frontend: single page hitting all four endpoints
- [ ] README rewrite for a recruiter-facing first impression
- [ ] Full end-to-end verification pass (query, summarize, bugs, fix - all tested together)
