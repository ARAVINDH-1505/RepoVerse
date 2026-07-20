import os
import sys
from groq import Groq
from reader import find_files

client = Groq(api_key=os.environ["GROQ_API_KEY"])


def read_file_contents(files, max_chars_per_file: int = 1500) -> str:
    combined = []
    for file in files:
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        trimmed = text[:max_chars_per_file]
        combined.append(f"File: {file}\n{trimmed}")
    return "\n\n---\n\n".join(combined)


def generate_summary(code_context: str, feedback: str = None) -> str:
    if feedback:
        prompt = f"""Your previous summary of this project was incomplete.
Feedback on what was missing: {feedback}

Code from the project:
{code_context}

Write an improved summary that fixes this."""
    else:
        prompt = f"""You are a senior software engineer. Read the code below from a project
and write a clear summary. Cover:
1. What the project does
2. Its main components/files and what each does
3. What technology or libraries it uses

Code from the project:
{code_context}

Summary:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def check_summary(summary: str) -> str:
    prompt = f"""Check if this project summary clearly covers all three things:
1. What the project does
2. Its main components/files
3. What technology/libraries it uses

If all three are clearly covered, reply with exactly: GOOD
If something is missing or unclear, reply with: NEEDS_IMPROVEMENT: <short reason>

Summary to check:
{summary}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def check_accuracy(summary: str, code_context: str) -> str:
    prompt = f"""You are reviewing a summary for accuracy. Compare the summary against
the actual code below. Check ONLY for made-up claims — things stated in the summary
that are not actually shown in the code (like features, UIs, or behavior that don't exist).

If everything in the summary is grounded in the actual code, reply with exactly: GOOD
If something is made up or not supported by the code, reply with: NEEDS_IMPROVEMENT: <what is made up>

Actual code:
{code_context}

Summary to check:
{summary}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def summarize_repo(folder_path: str, max_iterations: int = 3) -> dict:
    files = find_files(folder_path, file_types=[".py", ".md", ".json"])

    if not files:
        return {"summary": "No matching files found in this folder.", "iterations": 0}

    code_context = read_file_contents(files)

    summary = generate_summary(code_context)
    iterations_used = 1

    for _ in range(max_iterations - 1):
        completeness_result = check_summary(summary)
        accuracy_result = check_accuracy(summary, code_context)

        if completeness_result.startswith("GOOD") and accuracy_result.startswith("GOOD"):
            break

        feedback_parts = []
        if not completeness_result.startswith("GOOD"):
            feedback_parts.append(completeness_result)
        if not accuracy_result.startswith("GOOD"):
            feedback_parts.append(accuracy_result)

        combined_feedback = " | ".join(feedback_parts)
        summary = generate_summary(code_context, feedback=combined_feedback)
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