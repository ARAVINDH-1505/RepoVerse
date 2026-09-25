from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from answer import get_answer
from summarizer import summarize_repo
from bug_finder import find_bugs
from fix_explainer import explain_and_fix
import config

app = FastAPI(title="RepoVerse API")


def validate_folder_path(folder_path: str) -> Path:
    resolved = Path(folder_path).resolve()
    allowed_root = Path(config.ALLOWED_PROJECT_ROOT).resolve()

    if not resolved.exists() or not resolved.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Folder does not exist or is not a directory: {folder_path}"
        )

    try:
        resolved.relative_to(allowed_root)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail=f"Folder must be inside the allowed root ({allowed_root})."
        )

    return resolved


def validate_file_path(file_path: str) -> Path:
    resolved = Path(file_path).resolve()
    allowed_root = Path(config.ALLOWED_PROJECT_ROOT).resolve()

    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=400, detail=f"File not found: {file_path}")

    try:
        resolved.relative_to(allowed_root)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail=f"File must be inside the allowed root ({allowed_root})."
        )

    return resolved


class QuestionRequest(BaseModel):
    question: str
    folder_path: str


class FolderRequest(BaseModel):
    folder_path: str


class BugModel(BaseModel):
    file: str
    line_hint: str
    issue: str
    why: str


class FixRequest(BaseModel):
    bug: BugModel


@app.post("/query")
def query(request: QuestionRequest):
    validate_folder_path(request.folder_path)
    return get_answer(request.question, request.folder_path)


@app.post("/summarize")
def summarize(request: FolderRequest):
    validate_folder_path(request.folder_path)
    return summarize_repo(request.folder_path)


@app.post("/bugs")
def bugs(request: FolderRequest):
    validate_folder_path(request.folder_path)
    found = find_bugs(request.folder_path)
    return {"count": len(found), "bugs": found}


@app.post("/fix")
def fix(request: FixRequest):
    bug = request.bug.model_dump()
    file_path = validate_file_path(bug["file"])

    code_context = file_path.read_text(encoding="utf-8", errors="ignore")[:config.MAX_CHARS_PER_FILE]
    return explain_and_fix(bug, code_context)
