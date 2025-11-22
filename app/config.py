import json
import os

from dotenv import load_dotenv
from google import genai

from .models import SnippetInput, SnippetScore

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
あなたは学習スニペットを採点する講師です。
以下の4項目をそれぞれ 0〜10 点で採点し、JSON形式で出力してください。

評価基準は次の通りです：

1. 学びの深さ (depth_of_learning)
   - 背景・理由・仕組み・抽象化・具体例が書かれているほど高得点。

2. 専門性 (specialization)
   - 技術的な用語・概念・手法・数式・アルゴリズムが適切に含まれるほど高得点。

3. 簡潔さ (conciseness)
   - 冗長な説明が少なく、不要な文章がないほど高得点。
   - ただし短すぎて情報がない場合は低得点。

4. 論理性 (logic)
   - 文の流れ、因果関係、構成（導入→本論→まとめ）が整っているほど高得点。

---

最終スコアの計算ロジック（情報として示すが、あなたは計算しない）：
- 質 = 上記4項目の平均（0〜10）を 0〜1 に正規化した値
- 最終スコア = 質 × byte数
- 0 ≤ 最終スコア ≤ byte数

---

出力形式：
以下の JSON 形式のみを返してください（解説や文章は書かない）：

{
    "depth_of_learning": int,
    "specialization": int,
    "conciseness": int,
    "logic": int,
    "feedback": "string"
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

    # Gemini の採点結果を SnippetScore 型に
    recipe = SnippetScore.model_validate_json(response.text)

    # ----------------------
    # ① byte数
    # ----------------------
    byte_length = snippet.byte_length

    # ----------------------
    # ② 質 = 4項目平均を0〜1に正規化
    # ----------------------
    quality = (
        (
            recipe.depth_of_learning
            + recipe.specialization
            + recipe.conciseness
            + recipe.logic
        )
        / 4
        / 10
    )

    # ----------------------
    # ③ 最終スコア = byte数 × 質（0〜byte_length）
    # ----------------------
    final_score = int(byte_length * quality)
    final_score = max(0, min(final_score, byte_length))

    # SnippetScore に total を反映
    return SnippetScore(
        depth_of_learning=recipe.depth_of_learning,
        specialization=recipe.specialization,
        conciseness=recipe.conciseness,
        logic=recipe.logic,
        feedback=recipe.feedback,
        total=final_score,  # ←ここに最終スコアを入れる
    )
