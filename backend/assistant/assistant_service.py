import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DOCS_PATH = Path(__file__).with_name("knowledge_base.md")

DEFECT_LABELS = {
    "Cr": "Crazing",
    "In": "Inclusion",
    "Pa": "Patches",
    "PS": "Pitted Surface",
    "RS": "Rolled-in Scale",
    "Sc": "Scratches",
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "is", "are", "was", "were",
    "what", "why", "how", "can", "i", "we", "you", "about", "tell", "me", "it",
    "this", "that", "for", "on", "with", "as", "do", "does",
}

def _load_docs() -> List[Tuple[str, str]]:
    if not DOCS_PATH.exists():
        return []
    text = DOCS_PATH.read_text(encoding="utf-8")
    sections = re.split(r"^##\\s+", text, flags=re.MULTILINE)
    docs = []
    for section in sections:
        chunk = section.strip()
        if not chunk:
            continue
        parts = chunk.split("\n", 1)
        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""
        docs.append((title, body))
    return docs

def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]

def _score_doc(query_tokens: List[str], doc_text: str) -> int:
    if not query_tokens:
        return 0
    doc_tokens = set(_tokenize(doc_text))
    return sum(1 for t in query_tokens if t in doc_tokens)

def retrieve_docs(question: str, top_k: int = 2) -> List[Dict[str, str]]:
    docs = _load_docs()
    if not docs:
        return []
    query_tokens = _tokenize(question)
    scored = []
    for title, body in docs:
        score = _score_doc(query_tokens, f"{title}\n{body}")
        if score > 0:
            scored.append((score, title, body))
    scored.sort(reverse=True, key=lambda x: x[0])
    results = []
    for score, title, body in scored[:top_k]:
        results.append({"title": title, "content": body, "score": str(score)})
    return results

def _format_top_k(top_k: List[Dict[str, float]]) -> str:
    parts = []
    for item in top_k[:3]:
        name = item.get("class_name", "Unknown")
        conf = item.get("confidence", 0.0)
        parts.append(f"{name}: {conf:.1%}")
    return ", ".join(parts)

def _defect_title(defect_code: str) -> str:
    return DEFECT_LABELS.get(defect_code, defect_code)

def explain_prediction(prediction: Dict) -> str:
    predicted_class = prediction.get("raw_top_class") or prediction.get("predicted_class", "Unknown")
    confidence = float(prediction.get("confidence", 0.0))
    threshold = float(prediction.get("threshold", 0.0))
    top_k = prediction.get("top_k", [])

    defect_name = _defect_title(predicted_class)
    top_k_text = _format_top_k(top_k) if isinstance(top_k, list) else ""
    confidence_note = "High confidence" if confidence >= max(threshold, 0.5) else "Low confidence"

    parts = [
        f"Prediction: {defect_name} ({confidence:.1%}). {confidence_note}.",
    ]
    if top_k_text:
        parts.append(f"Top alternatives: {top_k_text}.")
    return " ".join(parts)

def answer_question(question: str, prediction: Optional[Dict] = None) -> Dict:
    response_parts = []
    if prediction:
        response_parts.append(explain_prediction(prediction))

    docs = retrieve_docs(question)
    if docs:
        for doc in docs:
            response_parts.append(f"{doc['title']}: {doc['content']}")
    else:
        response_parts.append("I could not find a direct match in the knowledge base.")

    return {
        "answer": "\n\n".join(response_parts),
        "sources": docs,
        "used_llm": False,
        "assistant_mode": os.getenv("ASSISTANT_MODE", "local"),
    }
