import logging
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


DATASET_DIR = Path(__file__).with_name("neu_defect_assistant_dataset")
TRAIN_PATH = DATASET_DIR / "train_simple.jsonl"
INDEX_PATH = Path(__file__).with_name("assistant_dataset_index.json")

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "is",
    "are",
    "was",
    "were",
    "what",
    "why",
    "how",
    "can",
    "i",
    "we",
    "you",
    "about",
    "tell",
    "me",
    "it",
    "this",
    "that",
    "for",
    "on",
    "with",
    "as",
    "do",
    "does",
    "pls",
    "please",
}


def tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def load_train_rows(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            input_text = item.get("input", "")
            output_text = item.get("output", "")
            metadata = item.get("metadata", {})
            rows.append(
                {
                    "id": item.get("id", ""),
                    "input": input_text,
                    "output": output_text,
                    "metadata": metadata,
                }
            )
    return rows


def build_index(rows: List[Dict]) -> Dict:
    doc_freq: Dict[str, int] = defaultdict(int)
    documents: List[Dict] = []

    for row in rows:
        label = str(row.get("metadata", {}).get("label", ""))
        # Retrieval should match the user's intent, not incidental words in a
        # long answer. Repeating the short question and label gives BM25 useful
        # weighting while the answer remains the returned content only.
        question_text = re.sub(r"\[IMAGE:[^\]]+\]", "", row["input"])
        row_type = str(row.get("metadata", {}).get("type", ""))
        retrieval_text = (
            f"{question_text} {question_text} {question_text} {label} {label} {label} {row_type}"
        )
        tokens = tokenize(retrieval_text)
        tf = Counter(tokens)
        unique_terms = set(tf.keys())
        for term in unique_terms:
            doc_freq[term] += 1
        documents.append(
            {
                "id": row["id"],
                "input": row["input"],
                "output": row["output"],
                "metadata": row.get("metadata", {}),
                "tf": dict(tf),
                "length": int(sum(tf.values())),
            }
        )

    n_docs = max(len(documents), 1)
    idf: Dict[str, float] = {}
    for term, df in doc_freq.items():
        # BM25-style smoothed IDF
        idf[term] = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))

    avg_len = sum(doc["length"] for doc in documents) / n_docs

    return {
        "version": 2,
        "source_file": str(TRAIN_PATH),
        "doc_count": len(documents),
        "avg_doc_len": avg_len,
        "idf": idf,
        "documents": documents,
    }


def main() -> None:
    if not TRAIN_PATH.exists():
        raise FileNotFoundError(f"Missing training dataset: {TRAIN_PATH}")

    rows = load_train_rows(TRAIN_PATH)
    if not rows:
        raise RuntimeError("No rows found in train_simple.jsonl")

    index = build_index(rows)
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    logger.info(" ".join(str(value) for value in (f"Wrote retrieval index: {INDEX_PATH}",)))
    logger.info(" ".join(str(value) for value in (f"Documents indexed: {index['doc_count']}",)))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
