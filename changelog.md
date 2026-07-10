# Changelog

## v0.2.0 - Storage and Searcher
- Added Storage: saves chunks and embeddings to disk using Chroma
- Added Searcher: takes a question, finds closest matching chunks from storage

## v0.1.0 - Reader, Splitter, Number-maker
- Added Reader: finds files by type, skips junk folders
- Added Splitter: breaks file text into overlapping chunks
- Added Number-maker (Embedder): turns chunks into embeddings using sentence-transformers

## v1.0.0 - Phase 1 complete: full question-answering loop working end to end