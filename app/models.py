from pydantic import BaseModel


class SnippetInput(BaseModel):
    title: str | None = None
    content: str


class SnippetScore(BaseModel):
    depth_of_learning: int
    specialization: int
    conciseness: int
    logic: int
    feedback: str
    total: int
