# RepoVerse - Architecture

RepoVerse is a tool that reads a code folder, understands it, answers questions
about it, finds real bugs, and explains/fixes them - always showing which files
its answers come from.

## The Flow

1. Reader finds all relevant files in a folder
2. Splitter breaks each file into small chunks
3. Number-maker turns each chunk into numbers (embeddings)
4. Storage saves those chunks and numbers to disk, one space per project
5. When a question is asked, Searcher turns the question into numbers too,
   and finds the closest matching chunks
6. Answerer sends the question and matching chunks to Groq, and returns a
   written answer with the source files
7. Separately, the Summarizer, Bug Finder, and Fix Explainer are agent-style
   components that read code directly (not through the search index) and
   run their own generate-check-improve loops

## Shared Foundations

### Config (`config.py`)
One place for every setting used across the project: the Groq API key
(read from environment variable or `.env` file), the Groq model name,
chunk size and overlap, the embedding model name, the max agent loop
iterations, the Chroma storage path, default file types, and the max
total characters allowed in one summarization prompt. Every other file
imports from here instead of repeating these values.

### Groq Client (`groq_client.py`)
The only place that actually talks to Groq. Creates the client once and
reuses it. Wraps every call with automatic retries (using a short delay)
if the connection fails, and checks that Groq actually returned a real,
non-empty answer before trusting it. Every agent component calls
`call_groq(prompt)` instead of creating its own client.

Note: Groq retired the models this project first used
(`llama-3.1-8b-instant`, `llama-3.3-70b-versatile`). The project now
defaults to `openai/gpt-oss-20b`, a current free-tier model.

## Core Pipeline Components

### Reader (`reader.py`)
Takes a folder path and a list of file types (like .py, .md, .json).
Walks through the folder and all folders inside it.
Skips junk folders: .git, venv, .venv, __pycache__, node_modules.
Returns a list of file paths that match the given file types.

### Splitter (`splitter.py`)
Takes a single file and reads its full text.
Breaks the text into chunks (size and overlap come from config.py).
Overlap between chunks avoids cutting meaning off at chunk edges.
Returns a list of text chunks.

### Number-maker / Embedder (`embedder.py`)
Uses a free local model (sentence-transformers, name set in
config.EMBEDDING_MODEL_NAME) to turn each text chunk into a list of
384 numbers representing meaning, not exact words. Runs fully locally,
no internet needed after first download, no cost.

### Storage (`storage.py`)
Each project gets its own separate storage space inside Chroma. The
folder path is turned into a short unique code (a hash), used as the
collection name. Two different projects can never mix data, even when
both are indexed on the same machine. Storage path comes from
config.CHROMA_DATA_PATH.

### Searcher (`searcher.py`)
Requires a folder_path, so it always searches inside the correct
project's storage. Turns a question into numbers using the same
embedder used for the code, then finds the closest matching chunks.

### Answerer (`answer.py`)
Checks if the Searcher found anything at all before calling Groq. If
nothing is found, returns an honest "not indexed yet" message instead
of letting the AI guess. Otherwise builds a prompt from the matching
chunks and the question, and calls Groq through groq_client.

### Indexer (`indexer.py`)
A standalone script that runs the full indexing chain (Reader, Splitter,
Number-maker, Storage) on any folder given as a command line argument.

Example: `python indexer.py "D:/path/to/any/project"`

### Front door / API (`main.py`)
A FastAPI endpoint (`/query`) that ties the flow together. User sends
a question and a folder_path, gets back an answer with source files.
Known issue: folder_path is not restricted to allowed folders - fine
for local single-user use, needs restricting before any public
deployment, since this is the one part of RepoVerse that accepts
input over the network rather than from a trusted local terminal.

## Agentic Components

These do not use the Reader/Splitter/Embedder/Storage/Searcher chain.
They read files directly and reason over them in a loop, deciding for
themselves whether their own output is good enough before returning it.

### Summarizer (`summarizer.py`)
Uses a map-reduce design:
1. Summarize each file separately, one small Groq call per file (full
   file content within a per-file limit, not the whole project at once)
2. Combine those per-file summaries into one text, capped at
   config.MAX_TOTAL_CONTEXT_CHARS total
3. Generate an overall project summary from the combined per-file summaries
4. Check the summary for completeness (covers what/components/tech)
5. Check the summary for accuracy (nothing claimed that isn't supported
   by the per-file summaries - including claims about documentation,
   comments, or "planned" features that aren't actually there)
6. If either check fails, regenerate using the feedback, try again
7. Stops after config.MAX_AGENT_ITERATIONS rounds maximum

This design replaced an earlier version that sent all files' raw code
in one single prompt. That approach broke down as the project grew
(hit Groq's per-request token limit), and even after shrinking each
file's content to fit, aggressive truncation caused the AI to falsely
claim things were "missing" or "not implemented" when they actually
existed further into a file than the truncation point allowed. The
map-reduce design fixes this by giving each file its own full-content
pass instead of a shared, truncated slice.

Known issue: per-file Groq calls fire back-to-back with no pause,
which triggers Groq's rate limit reactively (caught and retried
automatically, but slower and noisier than pacing the calls
proactively would be).

### Bug Finder (`bug_finder.py`)
Goes file by file, not all files at once. For each file:
1. Propose candidate bugs via one Groq call, asking specifically for
   real bugs (not style opinions), returned as JSON
2. Filter those candidates via a second, separate Groq call, keeping
   only bugs that pass three concrete checks: a specific trigger
   exists, the scenario is realistic for how this code is actually
   used (a local script run by its own owner is not an attacker
   scenario), and any security term used has a real, concrete attack
   path in this code (no database here, so SQL injection claims
   are rejected, for example)
3. Validates that every bug object returned has all three required
   fields (line_hint, issue, why) before using it - valid JSON is not
   the same as correctly-shaped JSON

Known issue: truncates file contents using its own hardcoded limit,
not config.MAX_TOTAL_CONTEXT_CHARS - should be unified with the rest
of the project's settings.

### Fix Explainer (`fix_explainer.py`)
Takes one bug (from the Bug Finder) and:
1. Explains it in plain English (what's wrong, why, what could go wrong)
2. Proposes a fix for that one specific issue only, instructed not to
   change unrelated code
3. Checks the fix with a separate Groq call against three rules: does
   it actually solve the issue, did it avoid touching unrelated code,
   is it still valid Python
4. If the check fails, regenerates the fix using the feedback, up to
   config.MAX_AGENT_ITERATIONS rounds

Does not write the fix back into the real file automatically - only
prints it, so a human reviews and applies it. This was a deliberate
choice: an agent editing real files without review is a bigger trust
step than the project is ready for yet.
