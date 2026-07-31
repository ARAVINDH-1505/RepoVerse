import os
import json
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])


def explain_bug(bug: dict, code_context: str) -> str:
    prompt = f"""Explain this bug in simple, plain English, for someone learning to code.
Cover: what is wrong, why it happens, and what could go wrong because of it.
Do not use unexplained technical jargon.

File: {bug['file']}
Bug location: {bug['line_hint']}
Issue: {bug['issue']}
Why it matters: {bug['why']}

Relevant code:
{code_context}

Plain English explanation:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def propose_fix(bug: dict, code_context: str, feedback: str = None) -> str:
    if feedback:
        extra = f"\n\nYour previous fix had a problem: {feedback}\nFix this issue in your new version."
    else:
        extra = ""

    prompt = f"""Fix this specific bug in the code below. Only fix this one issue,
do not change anything else, do not rewrite unrelated parts.

File: {bug['file']}
Issue: {bug['issue']}

Current code:
{code_context}

Reply with ONLY the corrected code, no explanation, no markdown formatting.{extra}

Corrected code:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def check_fix(bug: dict, original_code: str, fixed_code: str) -> str:
    prompt = f"""You are a strict code reviewer. Compare the original code and the fixed code.

Check ALL of these:
1. Does the fix actually solve the stated issue?
2. Did the fix avoid changing unrelated code or behavior?
3. Is the fixed code still valid, runnable Python?

Issue that should be fixed: {bug['issue']}

Original code:
{original_code}

Fixed code:
{fixed_code}

If all three checks pass, reply with exactly: GOOD
If any fail, reply with: NEEDS_IMPROVEMENT: <specific problem>"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def explain_and_fix(bug: dict, code_context: str, max_iterations: int = 3) -> dict:
    explanation = explain_bug(bug, code_context)

    fixed_code = propose_fix(bug, code_context)
    iterations_used = 1

    for _ in range(max_iterations - 1):
        check_result = check_fix(bug, code_context, fixed_code)

        if check_result.startswith("GOOD"):
            break

        fixed_code = propose_fix(bug, code_context, feedback=check_result)
        iterations_used += 1

    return {
        "explanation": explanation,
        "fixed_code": fixed_code,
        "iterations": iterations_used
    }


if __name__ == "__main__":
    from bug_finder import find_bugs
    from reader import find_files

    target_folder = "./my_project"
    bugs = find_bugs(target_folder)

    if not bugs:
        print("No bugs to explain.")
    else:
        first_bug = bugs[0]

        file_path = first_bug["file"]
        from pathlib import Path
        code_context = Path(file_path).read_text(encoding="utf-8", errors="ignore")[:1500]

        result = explain_and_fix(first_bug, code_context)

        print("EXPLANATION:")
        print(result["explanation"])
        print("\nFIXED CODE:")
        print(result["fixed_code"])
        print(f"\n(Used {result['iterations']} round(s) to get a good fix)")
