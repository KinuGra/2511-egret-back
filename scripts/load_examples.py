import json
import uuid

from app.rag_store import add_example

# data/examples.jsonl を読み込んで ChromaDB に追加するスクリプト


def main():
    examples_path = "data/examples.jsonl"

    with open(examples_path, "r", encoding="utf-8") as f:
        for line in f:
            example = json.loads(line)

            # JSONL から値を取得
            example_id = example.get("id") or str(uuid.uuid4())
            text = example["text"]

            # rag_store の add_example を呼び出して保存
            add_example(example_id, text)
            print(f"Added example: {example_id}")

    print("=== Done loading examples into ChromaDB ===")


if __name__ == "__main__":
    main()
