import sys
import json
import ast
from pathlib import Path
from reader import find_files
from groq_client import call_groq
import config


def is_syntactically_valid(file_path: str) -> bool:
    try:
        full_source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        ast.parse(full_source)
        return True
    except SyntaxError:
        return False
    except OSError:
        return True


def read_file_contents(files, max_chars_per_file: int = None) -> list[dict]:
    if max_chars_per_file is None:
        max_chars_per_file = config.MAX_CHARS_PER_FILE

    file_data = []
    for file in files:
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        file_data.append({"path": str(file), "content": text[:max_chars_per_file]})
    return file_data


def is_valid_bug(bug: dict) -> bool:
    required_keys = {"line_hint", "issue", "why"}
    return isinstance(bug, dict) and required_keys.issubset(bug.keys())


def find_candidate_bugs(file_data: dict) -> list[dict]:
    prompt = f"""You are a senior code reviewer. Look at the code below from one file
and find real bugs - things that would cause wrong behavior, crashes, or security issues.
Do NOT report style preferences, missing comments, or naming choices. Only real bugs.

If you find no real bugs, reply with exactly: []

If you find bugs, reply with ONLY a JSON list, no other text, in this exact format:
[
  {{"line_hint": "short quote or description of where", "issue": "what is wrong", "why": "why it is a problem"}}
]

File: {file_data['path']}
Code:
{file_data['content']}

JSON response:"""

    raw = call_groq(prompt).strip()

    try:
        bugs = json.loads(raw)
    except json.JSONDecodeError:
        return []

    return [bug for bug in bugs if is_valid_bug(bug)]


def filter_real_bugs(candidate_bugs: list[dict], file_data: dict, syntax_ok: bool) -> list[dict]:
    if not candidate_bugs:
        return []

    bugs_text = json.dumps(candidate_bugs, indent=2)

    syntax_fact = (
        "VERIFIED FACT: this exact file was just checked with Python's own parser and it "
        "parses successfully with NO syntax errors. Any claimed bug that describes a syntax "
        "error, a missing return/body, an undefined variable causing a crash, or the file "
        "'failing to import/run/parse' is FALSE, no exceptions - mark it a FALSE ALARM."
        if syntax_ok else
        "VERIFIED FACT: this file was checked with Python's own parser and DOES contain a "
        "real syntax error."
    )

    prompt = f"""You are a strict senior engineer reviewing a junior engineer's bug report.
Below is the actual code, and a list of bugs someone claims to have found in it.

{syntax_fact}

For each claimed bug, mark it REAL only if ALL of these are true:
1. You can point to the exact line and describe a specific input or situation that
   triggers the problem.
2. The problem would actually happen in how this code is really used (a local script
   run by its own owner, on their own machine, is NOT an attacker scenario).
3. It is not a generic security term (e.g. "injection," "sanitization," "arbitrary
   execution") used without a real, concrete attack path in THIS code. This code has
   no database queries and no network-facing input, so SQL injection and remote
   attacker scenarios do not apply here.

If a claimed bug fails any of these checks, it is a FALSE ALARM, not real.

Reply with ONLY a JSON list containing just the bugs you judge to be REAL, in the same
format they were given to you. If none are real, reply with exactly: []

File: {file_data['path']}
Code:
{file_data['content']}

Claimed bugs:
{bugs_text}

JSON response with only the real bugs:"""

    raw = call_groq(prompt).strip()

    try:
        real_bugs = json.loads(raw)
    except json.JSONDecodeError:
        return []

    return [bug for bug in real_bugs if is_valid_bug(bug)]


def find_bugs(folder_path: str) -> list[dict]:
    files = find_files(folder_path, file_types=[".py"])

    if not files:
        return []

    file_data_list = read_file_contents(files)

    all_real_bugs = []

    for file_data in file_data_list:
        try:
            syntax_ok = is_syntactically_valid(file_data["path"])

            candidates = find_candidate_bugs(file_data)
            if not candidates:
                continue

            real_bugs = filter_real_bugs(candidates, file_data, syntax_ok)

            for bug in real_bugs:
                bug["file"] = file_data["path"]

            all_real_bugs.extend(real_bugs)

        except RuntimeError as e:
            print(f"Skipping {file_data['path']} after repeated API failures: {e}")
            continue

    return all_real_bugs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please give a folder path. Example: python bug_finder.py ./my_project")
        sys.exit(1)

    target_folder = sys.argv[1]
    bugs = find_bugs(target_folder)

    if not bugs:
        print("No real bugs found.")
    else:
        print(f"Found {len(bugs)} real bug(s):\n")
        for bug in bugs:
            print(f"File: {bug['file']}")
            print(f"Location: {bug['line_hint']}")
            print(f"Issue: {bug['issue']}")
            print(f"Why: {bug['why']}")
            print("---")
