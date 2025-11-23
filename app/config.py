import json
import os

from dotenv import load_dotenv
from google import genai

from .models import SnippetInput, SnippetScore
from .rag_store import search_similar  # ← RAG の検索を読み込み

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------------------------------------
# 採点システムの基本プロンプト
# -------------------------------------------------------
SYSTEM_PROMPT = """
あなたは学習スニペットを採点する講師です。
以下の4項目をそれぞれ 0〜10 点で採点し、JSON形式で出力してください。

評価基準は次の通りです：

1. 学びの深さ (depth_of_learning)
   - 背景、理由、仕組み、抽象化、応用、例示が含まれるほど高得点。

2. 専門性 (specialization)
   - 技術用語、概念、アルゴリズム、数学的・プログラミング的要素が含まれるほど高得点。

3. 簡潔さ (conciseness)
   - 冗長が少なく、核心だけが簡潔に述べられているほど高得点。
   - ただし短すぎて内容が薄い場合は減点。

4. 論理性 (logic)
   - 文章構造、因果関係、説明の流れが明瞭なほど高得点。

出力形式（これ以外は一切書かないこと）：
{
    "depth_of_learning": int,
    "specialization": int,
    "conciseness": int,
    "logic": int,
    "feedback": "string"
}
"""


# -------------------------------------------------------
# RAGプロンプト生成（類似スニペットを注入する）
# -------------------------------------------------------
def build_rag_prompt(snippet: SnippetInput):
    """RAG統合プロンプト生成"""

    # ① search_similar で類似スニペットを取得
    similar_examples = search_similar(snippet.content, k=2)

    # ② 類似スニペットをMarkdownとして整形
    example_md = ""
    for i, ex in enumerate(similar_examples, 1):
        example_md += f"\n\n### 類似例 {i}\n{ex}\n"

    # ③ Gemini に渡すプロンプト全体を構築
    return f"""
{SYSTEM_PROMPT}

--- 類似スニペット（参考用） ---
{example_md}

--- 採点対象 ---
タイトル: {snippet.title}
内容:
{snippet.content}
"""


# -------------------------------------------------------
# RAG＋Gemini採点
# -------------------------------------------------------
async def score_snippet(snippet: SnippetInput):
    """RAG付きスニペット採点API"""

    # ① プロンプトを構築（RAG注入）
    prompt = build_rag_prompt(snippet)

    # ② Gemini に JSON schema 出力を要求
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": SnippetScore.model_json_schema(),
        },
    )

    # ③ Gemini の返却値 → SnippetScore に変換
    result = SnippetScore.model_validate_json(response.text)

    # ④ byte_length はフロントから送られる
    byte_length = snippet.byte_length

    # ⑤ 4項目の平均値 → 0〜1 の正規化
    quality = (
        (
            result.depth_of_learning
            + result.specialization
            + result.conciseness
            + result.logic
        )
        / 4
        / 10
    )

    # ⑥ 最終スコア（0〜byte_length）
    final = int(byte_length * quality)
    final = max(0, min(final, byte_length))

    # ⑦ total にセットして返却
    result.total = final
    return result
