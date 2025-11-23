from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import score_snippet
from app.models import SnippetInput
from app.rag_store import search_similar

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番は特定ドメインに
    allow_credentials=True,
    allow_methods=["*"],  # ← OPTIONS を含む全メソッドを許可
    allow_headers=["*"],  # ← Content-Type も許可
)


@app.get("/hello")
async def hello():
    return {"message": "Hello, FastAPI!"}


@app.post("/score")
async def score(snippet: SnippetInput):
    result = await score_snippet(snippet)
    return result


@app.post("/test-rag")
async def test_rag(snippet: SnippetInput):
    sims = search_similar(snippet.content, k=2)
    return {"input": snippet.content, "similar_examples": sims}
