# Changelog

## v0.2.0 - Storage and Searcher
- Added Storage: saves chunks and embeddings to disk using Chroma
- Added Searcher: takes a question, finds closest matching chunks from storage

## v0.1.0 - Reader, Splitter, Number-maker
- Added Reader: finds files by type, skips junk folders
- Added Splitter: breaks file text into overlapping chunks
- Added Number-maker (Embedder): turns chunks into embeddings using sentence-transformers

## v1.0.0 - Phase 1 complete: full question-answering loop working end to end

## v1.1.0 - Storage isolation, indexer script, hallucination fix
- Fixed: each project now has its own separate storage, no more mixed results
- Added: indexer.py, a proper script to index any folder from the terminal
- Fixed: system no longer lets the AI make up answers when no code is found

## v1.2.0 - First agentic component: Repo Summarizer
- Added summarizer.py with a self-checking loop (completeness + accuracy)
- Caught and fixed a real hallucination: summary claimed a UI existed when it did not