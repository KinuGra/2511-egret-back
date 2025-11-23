import os

import chromadb
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Gemini クライアント（Embedding 用）
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ------------------------------
# 1. Gemini Embedding で文章 → ベクトル変換
# ------------------------------
def embed_text(text: str) -> list[float]:
    response = client.models.embed_content(model="text-embedding-004", contents=text)
    embedding_objs = response.embeddings
    if not embedding_objs or not hasattr(embedding_objs[0], "values"):
        raise ValueError(f"Unexpected embedding format: {embedding_objs}")
    vector = embedding_objs[0].values
    return vector


# ------------------------------
# 2. ChromaDB（永続型）の初期化
# ------------------------------
# この `data/chroma_db` フォルダにベクトルデータが保存される。
chroma_client = chromadb.PersistentClient(path="data/chroma_db")


# ------------------------------
# 3. コレクション作成（例データ保管庫）
# ------------------------------
collection = chroma_client.get_or_create_collection(
    name="snippet_examples"  # 名前は自由だが一意に
)


# ------------------------------
# 4. 例文を追加する関数
# ------------------------------
def add_example(example_id: str, text: str):
    vector = embed_text(text)
    print(f"Adding example {example_id}, vector length {len(vector)}")
    collection.add(
        ids=[example_id],
        embeddings=[vector],
        documents=[text],
    )


# ------------------------------
# 5. 類似スニペットを検索する関数
# ------------------------------
def search_similar(query: str, k: int = 3):
    """
    クエリ（ユーザーのスニペット）に似た例文を k 件検索して返す。
    """
    query_embedding = embed_text(query)

    result = collection.query(query_embeddings=[query_embedding], n_results=k)

    # result["documents"] は "各クエリに対するリスト" なので 0 番目を返す
    return result["documents"][0] if result["documents"] else []
