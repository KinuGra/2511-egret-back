# プロジェクト作成

```
# 仮想環境（Windowsの場合はactivateのコマンドが違います）
python -m venv venv
source venv/bin/activate

# ライブラリ
pip install "fastapi[standard]" uvicorn openai chromadb pydantic-settings
pip install google-generativeai pydantic python-dotenv
pip install -q -U google-genai

# requirements.txtを作成
pip freeze > requirements.txt
```

# 起動

```
uvicorn app.main:app --reload
```
