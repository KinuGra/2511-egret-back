# プロジェクト作成

```
# 仮想環境（Windowsの場合はactivateのコマンドが違います）
python -m venv venv
source venv/bin/activate

# ライブラリ
pip install "fastapi[standard]" uvicorn openai chromadb pydantic-settings python-dotenv google-genai
pip install chromadb

# requirements.txtを作成
pip freeze > requirements.txt
```

# 起動

```
uvicorn app.main:app --reload
```

# RAG: 例データを一括登録するコマンド

```
python -m scripts.load_examples
```
