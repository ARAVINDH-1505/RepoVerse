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

## Day 5 - July 21, 2026
- Built the first real agentic feature: Repo Summarizer, using a generate-check-improve loop
- First version only checked completeness, and passed in 1 round despite containing a
  hallucination (claimed the project has a UI, which it does not)
- Learned: a self-check step is only as good as what it actually checks for - completeness
  and accuracy are different questions and need separate checks
- Added a second checker for accuracy, comparing the summary against the real code
- Reran the summarizer: took 3 rounds this time, and the hallucination was gone
- Learned: more self-checking means better output but more API calls - real trade-off,
  need a hard iteration cap so the agent can never loop forever
- Next: build the Bug Finder agent

## Day 6 - July 22, 2026
- Built Bug Finder: propose-then-filter agent loop, file by file
- First version let through fake security warnings (SQL injection, directory
  traversal) on a local script with no database and no network-facing input
- Learned: generic security terms need a real, concrete attack path to be valid -
  tightened the filter prompt to require this explicitly
- Also found a real distinction: main.py IS a network-facing API, so folder_path
  there is a genuine future risk, just not urgent while only I call it locally
- Fixed a crash from an AI response missing a required field - valid JSON isn't
  the same as correctly-shaped JSON, added shape validation before using bug data
- Next: build the Fix Explainer, the last piece of the agent loop

## Day 7 - August 2026
- Built Fix Explainer: explains a bug in plain English, proposes a fix, checks
  the fix against three rules (solves the issue, doesn't touch unrelated code,
  still valid Python) before returning it
- Decided fixes are only printed, not auto-applied to real files - didn't trust
  the loop enough yet to let it edit code directly
- Learned the limits of the filesystem connector: it can read/write files on my
  laptop, but cannot run terminal commands like git - pushing to GitHub still
  has to be a manual step, and I decided that's actually fine since I want to
  review my own commits anyway

## Day 8 - September 1, 2026
- Noticed the project had grown into repeated logic: Groq client creation and
  API key loading were copy-pasted across answer.py, summarizer.py, and bug_finder.py
- Built config.py: one shared place for API key, model name, chunk size, overlap,
  embedding model name, max loop iterations, storage path, default file types
- Built groq_client.py: one shared function for every Groq call, with automatic
  retries and a check that Groq actually returned a real answer
- Updated every module to use these shared pieces instead of repeating logic
- Also cleaned up a leftover hardcoded test path from an unrelated project in
  splitter.py and embedder.py
- Hit a real production issue: Groq retired the models I'd been using
  (llama-3.1-8b-instant, llama-3.3-70b-versatile) - had to find and switch to
  a current model (openai/gpt-oss-20b)
- Learned: a 404 "model not found" error means the model name is wrong, not the
  API key - different from a 401 authentication error

## Day 9 - September 2-4, 2026
- Ran into a 413 Payload Too Large error: the Summarizer sends every file's code
  in one prompt, and the project has grown too large for Groq's free-tier
  per-request token limit
- First fix (a hard character budget across all files) solved the crash, but
  created a new problem: heavy truncation caused the summary to falsely claim
  real, working code was "missing" or "not shown"
- Learned: fixing hallucination doesn't help if the input itself is incomplete -
  garbage in, garbage out applies to context, not just prompts
- Redesigned the Summarizer as map-reduce: summarize each file separately in its
  own small Groq call first, then combine those summaries into one final summary
- This fixed the token limit problem properly, but revealed a second, worse issue:
  when a file's summary was still incomplete, the final summary sometimes invented
  a fake source ("the README explicitly notes...") to explain the gap, instead of
  just saying something was missing
- Learned: an AI covering a gap in its information by inventing a plausible-sounding
  citation is a more serious failure than plain guessing - it manufactures false
  authority
- Fixed by giving each file's summary more room before truncating, explicitly
  telling the AI not to speculate past a truncation point, and tightening the
  accuracy checker to reject any unsupported claim, not just claims about code
  behavior specifically
- Reran after both fixes: the fake README claim and the false "not implemented"
  claim about check_fix were both gone
- Noticed a smaller remaining issue: the summary described bug_finder.py's
  truncation as using a config.py setting, when it actually still uses its own
  hardcoded limit - logged as a known issue, not fixed yet
- Noticed heavy Groq rate-limiting (many 429 retries) from firing per-file calls
  back to back with no pause - works correctly via retries, but slow and
  inefficient - logged as a known improvement
- Phase 3 (all three agentic components) is now functionally complete, running
  on shared config and a shared, retry-safe Groq client
- Next: unify bug_finder's truncation with config.py, add pacing between
  per-file Groq calls, then decide the next Phase 2 priority (Docker, more
  file types, or GitHub URL support)