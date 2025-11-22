from fastapi import FastAPI

from app.models import SnippetInput

app = FastAPI()


@app.get("/hello")
async def hello():
    return {"message": "Hello, FastAPI!"}


@app.post("/score")
async def score(snippet: SnippetInput):
    return {
        "status": "received",
        "title": snippet.title,
        "received_content": snippet.content,
    }
