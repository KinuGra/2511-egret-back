import json
import os

from dotenv import load_dotenv
from google import genai

from .models import SnippetInput, SnippetScore

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
あなたは学習スニペットを採点する講師です。
以下4項目を 0～10 点で採点し、JSON形式で出力してください：

1. 学びの深さ (depth_of_learning)
2. 専門性 (specialization)
3. 簡潔さ (conciseness)
4. 論理性 (logic)

この形式だけで返してください：
{
    "depth_of_learning": int,
    "specialization": int,
    "conciseness": int,
    "logic": int,
    "feedback": "文章"
}
"""


async def score_snippet(snippet: SnippetInput):
    prompt = f"""
{SYSTEM_PROMPT}
--- スニペット ---
タイトル: {snippet.title}
内容:
{snippet.content}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": SnippetScore.model_json_schema(),
        },
    )
    recipe = SnippetScore.model_validate_json(response.text)

    total = (
        recipe.depth_of_learning
        + recipe.specialization
        + recipe.conciseness
        + recipe.logic
    )

    # 既存 recipe に total を追加したい場合
    return SnippetScore(
        depth_of_learning=recipe.depth_of_learning,
        specialization=recipe.specialization,
        conciseness=recipe.conciseness,
        logic=recipe.logic,
        feedback=recipe.feedback,
        total=total,
    )
