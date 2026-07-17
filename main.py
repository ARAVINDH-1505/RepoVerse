from fastapi import FastAPI
from pydantic import BaseModel
from answer import get_answer

app = FastAPI()


class QuestionRequest(BaseModel):
    question: str
    folder_path: str


@app.post("/query")
def query(request: QuestionRequest):
    result = get_answer(request.question, request.folder_path)
    return result