from pydantic import BaseModel


class SnippetInput(BaseModel):
    title: str | None = None
    content: str
