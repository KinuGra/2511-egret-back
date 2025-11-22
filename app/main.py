from fastapi import FastAPI

from app.config import score_snippet
from app.models import SnippetInput

app = FastAPI()


@app.get("/hello")
async def hello():
    return {"message": "Hello, FastAPI!"}


@app.post("/score")
async def score(snippet: SnippetInput):
    result = await score_snippet(snippet)
    return result
