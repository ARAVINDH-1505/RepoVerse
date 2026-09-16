import sys
import time
from reader import find_files
from groq_client import call_groq
import config


def summarize_single_file(file_path: str, content: str, max_chars: int = None) -> str:
    if max_chars is None:
        max_chars = config.MAX_CHARS_PER_FILE

    was_truncated = len(content) > max_chars
    trimmed = content[:max_chars]

    truncation_note = (
        "\n\n[This file was cut off at this point due to length. Do not guess, speculate, "
        "or invent anything about what might come after this point.]"
        if was_truncated else ""
    )

    prompt = f"""Summarize what this single code file does, in 2-3 sentences.
Only describe what is literally shown below. Do not invent documentation, comments,
READMEs, future plans, or anything not directly visible in the code shown.

File: {file_path}
Code:
{trimmed}{truncation_note}

Summary:"""

    return call_groq(prompt)


def build_project_context(folder_path: str) -> str:
    files = find_files(folder_path, file_types=config.DEFAULT_FILE_TYPES)

    if not files:
        return ""

    entries = []
    total_chars = 0
    skipped = 0

    for index, file in enumerate(files):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if not text.strip():
            continue

        if index > 0:
            time.sleep(config.PER_FILE_CALL_DELAY_SECONDS)

        file_summary = summarize_single_file(str(file), text)
        entry = f"File: {file}\nSummary: {file_summary}"

        if total_chars + len(entry) > config.MAX_TOTAL_CONTEXT_CHARS:
            skipped += 1
            continue

        entries.append(entry)
        total_chars += len(entry)

    if skipped:
        entries.append(
            f"[Note: {skipped} additional file summaries were left out to stay within size limits.]"
        )

    return "\n\n".join(entries)


def generate_summary(project_context: str, feedback: str = None) -> str:
    if feedback:
        prompt = f"""Your previous summary of this project was incomplete.
Feedback on what was missing: {feedback}

Per-file summaries from the project:
{project_context}

Write an improved overall project summary that fixes this."""
    else:
        prompt = f"""You are a senior software engineer. Below are short summaries of each
file in a project. Using ONLY this information, write a clear overall project summary. Cover:
1. What the project does
2. Its main components/files and what each does
3. What technology or libraries it uses

Per-file summaries from the project:
{project_context}

Overall project summary:"""

    return call_groq(prompt)


def check_summary(summary: str) -> str:
    prompt = f"""Check if this project summary clearly covers all three things:
1. What the project does
2. Its main components/files
3. What technology/libraries it uses

If all three are clearly covered, reply with exactly: GOOD
If something is missing or unclear, reply with: NEEDS_IMPROVEMENT: <short reason>

Summary to check:
{summary}"""

    return call_groq(prompt).strip()


def check_accuracy(summary: str, project_context: str) -> str:
    prompt = f"""You are reviewing a project summary for accuracy. Compare the summary against
the per-file summaries below. Check for ANY claim in the summary that is not directly
supported by the per-file summaries - including claims about documentation, comments,
README files, future plans, or things the project "explicitly notes." If the per-file
summaries do not mention something, the overall summary must not claim it either, even
if it sounds plausible or well-written.

If everything in the summary is grounded in the per-file summaries, reply with exactly: GOOD
If something is made up or unsupported, reply with: NEEDS_IMPROVEMENT: <what is made up>

Per-file summaries:
{project_context}

Overall summary to check:
{summary}"""

    return call_groq(prompt).strip()


def summarize_repo(folder_path: str, max_iterations: int = None) -> dict:
    if max_iterations is None:
        max_iterations = config.MAX_AGENT_ITERATIONS

    project_context = build_project_context(folder_path)

    if not project_context:
        return {"summary": "No matching files found in this folder.", "iterations": 0}

    summary = generate_summary(project_context)
    iterations_used = 1

    for _ in range(max_iterations - 1):
        completeness_result = check_summary(summary)
        accuracy_result = check_accuracy(summary, project_context)

        if completeness_result.startswith("GOOD") and accuracy_result.startswith("GOOD"):
            break

        feedback_parts = []
        if not completeness_result.startswith("GOOD"):
            feedback_parts.append(completeness_result)
        if not accuracy_result.startswith("GOOD"):
            feedback_parts.append(accuracy_result)

        combined_feedback = " | ".join(feedback_parts)
        summary = generate_summary(project_context, feedback=combined_feedback)
        iterations_used += 1

    return {"summary": summary, "iterations": iterations_used}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please give a folder path. Example: python summarizer.py ./my_project")
        sys.exit(1)

    target_folder = sys.argv[1]
    result = summarize_repo(target_folder)

    print(f"Used {result['iterations']} round(s) to get a good summary.\n")
    print(result["summary"])
