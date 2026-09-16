# Changelog

## v1.6.0 - Summarizer redesigned as map-reduce, two hallucination fixes
- Redesigned Summarizer: now summarizes each file separately first, then combines
  those into one project summary, instead of sending all raw code in one prompt
- Fixed: original design hit Groq's per-request token limit as the project grew
  (413 Payload Too Large)
- Fixed: after shrinking file content to fit, aggressive truncation caused the
  summary to falsely claim real code was "missing" or "not shown"
- Fixed: a worse case of the same problem - the summary invented a fake claim
  that "the README explicitly notes" a feature was only planned, when the
  feature was fully built and no such README text exists
- Tightened the accuracy checker to reject any claim not directly supported by
  the per-file summaries, including claims about documentation or future plans

## v1.5.0 - Shared config and Groq client, model migration
- Added config.py: single source for API key, model name, chunk size, overlap,
  embedding model, max loop iterations, storage path, default file types
- Added groq_client.py: single shared function for all Groq calls, with
  automatic retries and empty-response checking
- Updated answer.py, summarizer.py, bug_finder.py, fix_explainer.py, splitter.py,
  embedder.py, storage.py to use the shared config and client instead of
  duplicated logic
- Fixed: Groq retired llama-3.1-8b-instant and llama-3.3-70b-versatile;
  switched default model to openai/gpt-oss-20b
- Removed a leftover hardcoded test path from an unrelated project in
  splitter.py and embedder.py

## v1.4.0 - Fix Explainer agent
- Added fix_explainer.py: explains a bug in plain English, proposes a fix,
  checks the fix against three rules before returning it, loops if the
  check fails
- Fix is only printed, never auto-applied to the real file

## v1.3.0 - Bug Finder agent, output validation
- Added bug_finder.py: propose-then-filter loop for finding real code issues
- Fixed: false security alarms (SQL injection, directory traversal on local scripts)
  by making the filter check for concrete, real attack scenarios
- Fixed: crash from AI returning a bug entry missing a required field, now validated

## v1.2.0 - First agentic component: Repo Summarizer
- Added summarizer.py with a self-checking loop (completeness + accuracy)
- Caught and fixed a real hallucination: summary claimed a UI existed when it did not

## v1.1.0 - Storage isolation, indexer script, hallucination fix
- Fixed: each project now has its own separate storage, no more mixed results
- Added: indexer.py, a proper script to index any folder from the terminal
- Fixed: system no longer lets the AI make up answers when no code is found

## v1.0.0 - Phase 1 complete: full question-answering loop working end to end

## v0.2.0 - Storage and Searcher
- Added Storage: saves chunks and embeddings to disk using Chroma
- Added Searcher: takes a question, finds closest matching chunks from storage

## v0.1.0 - Reader, Splitter, Number-maker
- Added Reader: finds files by type, skips junk folders
- Added Splitter: breaks file text into overlapping chunks
- Added Number-maker (Embedder): turns chunks into embeddings using sentence-transformers
