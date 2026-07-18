import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from label_normalization import to_display_label

DOCS_PATH = Path(__file__).with_name("knowledge_base.md")
DATASET_INDEX_PATH = Path(__file__).with_name("assistant_dataset_index.json")

DEFECT_LABELS = {
    "Cr": "Crazing",
    "In": "Inclusion",
    "Pa": "Patches",
    "PS": "Pitted Surface",
    "RS": "Rolled-in Scale",
    "Sc": "Scratches",
}

LABEL_KEYWORDS = {
    "Crazing": {"crazing", "cr"},
    "Inclusion": {"inclusion", "inclusions", "in"},
    "Patches": {"patch", "patches", "pa"},
    "Pitted_Surface": {"pitted", "pitted_surface", "pittedsurface", "ps"},
    "Rolled_in_Scale": {"rolled", "scale", "rolled_in_scale", "rolledinscale", "rs"},
    "Scratches": {"scratch", "scratches", "sc"},
}

METAL_KEYWORDS = {
    "steel",
    "aluminum",
    "aluminium",
    "copper",
    "titanium",
    "brass",
    "bronze",
    "nickel",
    "metal",
}

METAL_FACTS = {
    "steel": "Steel is an iron-carbon alloy with high strength and wide industrial use.",
    "aluminum": "Aluminum is lightweight, corrosion resistant, and easy to form.",
    "aluminium": "Aluminium is lightweight, corrosion resistant, and easy to form.",
    "copper": "Copper is reddish, highly conductive, and commonly used in electrical parts. Quick check: color, high conductivity, and non-magnetic behavior.",
    "titanium": "Titanium has high strength-to-weight ratio and strong corrosion resistance.",
    "brass": "Brass is a copper-zinc alloy with yellow-gold appearance and good machinability.",
    "bronze": "Bronze is usually copper-tin alloy, known for wear resistance.",
    "nickel": "Nickel is corrosion resistant and often used in alloying and plating.",
}

COMPARISON_KEYWORDS = {
    "compare",
    "comparison",
    "metrics",
    "metric",
    "dashboard",
    "winner",
    "wins",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "fetched",
    "fetch",
    "source",
    "explainability",
}

DEFECT_ORDER = [
    "Crazing",
    "Inclusion",
    "Patches",
    "Pitted_Surface",
    "Rolled_in_Scale",
    "Scratches",
]

DEFECT_DISPLAY_NAMES = {
    "Crazing": "Crazing",
    "Inclusion": "Inclusion",
    "Patches": "Patches",
    "Pitted_Surface": "Pitted Surface",
    "Rolled_in_Scale": "Rolled-in Scale",
    "Scratches": "Scratches",
}

DEFECT_PRECAUTIONS = {
    "Crazing": "Control roll/strip temperature and cooling; reduce friction with proper lubrication.",
    "Inclusion": "Improve steel cleanliness, slag control, and refractory condition monitoring.",
    "Patches": "Stabilize lubrication/emulsion, keep rolls clean, and maintain uniform process temperature.",
    "Pitted_Surface": "Control storage corrosion risks (moisture/salts) and tune pickling/rinse parameters.",
    "Rolled_in_Scale": "Strengthen descaling (pressure/nozzle alignment) and control scale formation before rolling.",
    "Scratches": "Remove burrs/debris on line path, maintain rolls, and improve handling/packaging practices.",
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
    sections = re.split(r"^##\s+", text, flags=re.MULTILINE)
    docs = []
    for section in sections:
        chunk = section.strip()
        if not chunk:
            continue
        parts = chunk.split("\n", 1)
        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""
        if title.startswith("# "):
            continue
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


def _load_dataset_index() -> Optional[Dict]:
    if not DATASET_INDEX_PATH.exists():
        return None
    try:
        return json.loads(DATASET_INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def _score_dataset_doc(query_tf: Dict[str, int], doc: Dict, idf: Dict[str, float], avg_len: float) -> float:
    # BM25 with conservative defaults for short QA prompts.
    k1 = 1.2
    b = 0.75
    tf = doc.get("tf", {})
    doc_len = max(float(doc.get("length", 0)), 1.0)
    if not query_tf:
        return 0.0

    score = 0.0
    for term, qf in query_tf.items():
        f = float(tf.get(term, 0.0))
        if f <= 0:
            continue
        term_idf = float(idf.get(term, 0.0))
        denom = f + k1 * (1 - b + b * (doc_len / max(avg_len, 1e-6)))
        score += term_idf * ((f * (k1 + 1)) / max(denom, 1e-6)) * qf
    return score


def _sanitize_answer_text(text: str) -> str:
    clean = text.replace("**", "")
    clean = clean.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    clean = clean.replace("â€‘", "-")
    clean = re.sub(r"\r\n?", "\n", clean)
    clean = re.sub(r"[ \t]+", " ", clean)
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean.strip()


def _is_metal_question(query_tokens: List[str]) -> bool:
    return any(tok in METAL_KEYWORDS for tok in query_tokens)


def _is_defect_question(query_tokens: List[str]) -> bool:
    if "defect" in query_tokens or "surface" in query_tokens:
        return True
    token_set = set(query_tokens)
    for keywords in LABEL_KEYWORDS.values():
        if token_set.intersection(keywords):
            return True
    return False


def _is_defect_catalog_question(question: str, query_tokens: List[str]) -> bool:
    q = question.lower()
    return (
        "defects" in query_tokens
        and (
            "how many" in q
            or bool(re.search(r"\b[1-9]\d*\b", q))
            or any(word in query_tokens for word in {"six", "types", "list", "all"})
            or "type" in query_tokens
        )
    )


def _is_defect_definition_question(question: str, query_tokens: List[str]) -> bool:
    q = re.sub(r"[^a-z0-9 ]+", "", question.lower())
    return bool(
        re.search(r"\bwhat (is|are) (a )?(steel )?(surface )?defects?\b", q)
        or re.search(r"\bdefine (surface )?defects?\b", q)
        or ("meaning" in query_tokens and {"defect", "defects"}.intersection(query_tokens))
    )


def _is_scanner_question(query_tokens: List[str]) -> bool:
    equipment = {"scanner", "camera", "equipment", "device", "sensor", "imaging", "setup"}
    actions = {"scan", "detect", "inspect", "inspection", "required", "require", "use"}
    return bool(set(query_tokens).intersection(equipment)) and bool(
        set(query_tokens).intersection(actions)
    )


def _is_ambiguous_surface_question(query_tokens: List[str]) -> bool:
    return (
        "surface" in query_tokens
        and bool(set(query_tokens).intersection({"identify", "detect", "classify"}))
        and not _matched_defect_labels(query_tokens)
    )


def _is_comparison_question(query_tokens: List[str]) -> bool:
    if "comparison" in query_tokens or "compare" in query_tokens:
        return True
    metric_hits = sum(1 for tok in query_tokens if tok in COMPARISON_KEYWORDS)
    return metric_hits >= 2


def _is_precaution_question(query_tokens: List[str]) -> bool:
    return any(
        tok in {"precaution", "precautions", "prevent", "prevented", "prevention", "avoid", "reduce"}
        for tok in query_tokens
    )


def _matched_defect_labels(query_tokens: List[str]) -> set:
    token_set = set(query_tokens)
    return {
        label
        for label, keywords in LABEL_KEYWORDS.items()
        if token_set.intersection(keywords)
    }


def _prediction_label(prediction: Optional[Dict]) -> Optional[str]:
    if not prediction:
        return None
    raw = prediction.get("raw_top_class") or prediction.get("predicted_class")
    return str(raw) if raw in LABEL_KEYWORDS else None


def _uses_prediction_context(question: str, query_tokens: List[str]) -> bool:
    q = question.lower().strip()
    patterns = (
        r"\b(this|current|detected|predicted)\s+(defect|result|prediction)\b",
        r"\b(what|which)\s+(was|is|did)\b.{0,20}\b(detect|detected|predict|predicted)\b",
        r"\b(prediction|result|confidence|top[- ]?k|alternative)\b",
        r"\bwhy\b.{0,20}\b(predict|predicted|classification|classified)\b",
        r"\b(this|detected)\s+(one|issue)\b",
    )
    return any(re.search(pattern, q) for pattern in patterns)


def _asks_for_prediction_explanation(question: str) -> bool:
    q = question.lower()
    return bool(
        re.search(
            r"\b(detect|detected|predict|predicted|prediction|result|confidence|top[- ]?k|alternative)\b",
            q,
        )
    )


def _has_detail_intent(query_tokens: List[str]) -> bool:
    return bool(
        set(query_tokens).intersection(
            {
                "cause", "causes", "root", "prevent", "prevented", "prevention", "avoid",
                "reduce", "fix", "action", "inspect", "inspection", "check",
                "confirm", "lab", "serious", "severity", "impact", "risk",
                "acceptable", "reject", "identify", "visual", "look",
            }
        )
    )


def _extract_answer_sections(text: str) -> Dict[str, str]:
    headings = {
        "Most likely defect": "defect",
        "Why (visual cues)": "visual",
        "Likely root causes": "causes",
        "Impact / risk": "impact",
        "What to check now (fast actions)": "actions",
        "Good next steps": "next",
    }
    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.lower().startswith("most likely defect:"):
            current = "defect"
            value = line.split(":", 1)[1].strip()
            if value:
                sections.setdefault(current, []).append(value)
            continue
        heading = line.rstrip(":")
        if heading in headings:
            current = headings[heading]
            sections.setdefault(current, [])
            continue
        if current and line:
            sections[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items() if lines}


def _focus_dataset_answer(text: str, query_tokens: List[str]) -> str:
    sections = _extract_answer_sections(text)
    if not sections:
        return text

    tokens = set(query_tokens)
    selected: List[Tuple[str, str]] = []
    if tokens.intersection({"cause", "causes", "root", "why"}):
        selected.append(("Likely root causes", "causes"))
    if tokens.intersection({"identify", "detect", "visual", "look", "appearance"}):
        selected.append(("Visual cues", "visual"))
    if tokens.intersection({"prevent", "prevented", "prevention", "avoid", "reduce", "fix", "action"}):
        selected.extend([("Recommended actions", "actions"), ("Next steps", "next")])
    if tokens.intersection({"serious", "severity", "impact", "risk", "acceptable", "reject"}):
        selected.append(("Impact and risk", "impact"))
    if tokens.intersection({"inspect", "inspection", "check", "confirm", "lab"}):
        selected.extend([("Inspection actions", "actions"), ("Confirmation", "next")])

    rendered = []
    seen = set()
    for title, key in selected:
        if key in sections and key not in seen:
            rendered.append(f"{title}:\n{sections[key]}")
            seen.add(key)
    if rendered:
        return "\n\n".join(rendered)
    if "visual" in sections:
        return f"Visual cues:\n{sections['visual']}"
    return text


def _build_defect_catalog_answer(include_precautions: bool) -> str:
    lines = [f"There are {len(DEFECT_ORDER)} main defect classes in this project:"]
    for label in DEFECT_ORDER:
        display = DEFECT_DISPLAY_NAMES.get(label, to_display_label(label))
        if include_precautions:
            lines.append(f"- {display}: {DEFECT_PRECAUTIONS.get(label, 'Apply standard QA controls.')}")
        else:
            lines.append(f"- {display}")
    lines.append("Use consistent lighting and clear surface images for reliable detection.")
    return "\n".join(lines)


def _build_defect_definition_answer() -> str:
    return (
        "A surface defect is an unintended irregularity on or near a metal surface that can affect "
        "appearance, coating, forming, fatigue life, or product acceptance. In this project, the six "
        "detected steel-surface classes are Crazing, Inclusion, Patches, Pitted Surface, "
        "Rolled-in Scale, and Scratches."
    )


def _build_scanner_answer() -> str:
    return (
        "For this image-classification system, use an industrial area-scan camera rather than a document scanner.\n"
        "- Camera: monochrome or RGB industrial camera with stable manual exposure; 2-5 MP is sufficient for a prototype.\n"
        "- Lens: choose the focal length so the steel region fills the frame and the smallest important defect spans several pixels.\n"
        "- Lighting: diffuse LED bar/dome lighting to suppress glare; use dark-field lighting when scratches or shallow texture must stand out.\n"
        "- Mounting: rigid, perpendicular mounting with fixed working distance and an enclosure from ambient light.\n"
        "- Triggering: use a hardware trigger/encoder for a moving strip; use a line-scan camera instead for continuous high-speed, wide-strip inspection.\n"
        "- Input quality: capture a sharp surface crop and send it to the model as JPEG or PNG. Validate the setup on real production samples before QA use."
    )


def _answer_operational_question(question: str, query_tokens: List[str]) -> Optional[str]:
    q = question.lower()
    tokens = set(query_tokens)

    if tokens.intersection({"precision", "recall", "f1"}):
        definitions = {
            "precision": "Precision is TP / (TP + FP): among predictions assigned to a class, the fraction that are correct.",
            "recall": "Recall is TP / (TP + FN): among real examples of a class, the fraction the model detects.",
            "f1": "F1 score is the harmonic mean of precision and recall: 2 x precision x recall / (precision + recall).",
        }
        return "\n".join(definitions[key] for key in ("precision", "recall", "f1") if key in tokens)
    if "confidence" in tokens:
        return (
            "Confidence is the model's probability-like score for its selected class, not a guarantee of correctness. "
            "This app treats CustomML results below 55% as Unknown. Review top-k alternatives and validate uncertain "
            "or safety-critical cases with a qualified inspector."
        )
    if ("top" in tokens and "k" in tokens) or "top-k" in q:
        return (
            "Top-k lists the k classes with the highest model scores. A small gap between the first and second result "
            "means the image is ambiguous and should be reviewed."
        )
    if "format" in tokens or "formats" in tokens or ("file" in tokens and "accepted" in tokens):
        return (
            "Accepted image formats are JPEG/JPG, PNG, WebP, and BMP. The maximum upload size is 5 MB per image. "
            "Use a sharp RGB crop of the steel surface with consistent lighting."
        )
    if "lighting" in tokens or "light" in tokens:
        return (
            "Use stable diffuse LED lighting to reduce glare. For scratches and shallow linear texture, add low-angle "
            "dark-field bar lighting so edges and grooves create contrast. Lock exposure and white balance, shield the "
            "setup from ambient light, and validate it on real samples."
        )
    if "false" in tokens and tokens.intersection({"positive", "positives"}):
        return (
            "To reduce false positives: keep lighting and exposure fixed, clean the surface and lens, crop out background, "
            "reject low-confidence predictions, inspect top-k score gaps, and retrain with representative normal/no-defect "
            "and hard-negative camera images."
        )
    if tokens.intersection({"severe", "severity", "serious"}) and tokens.intersection({"defect", "defects"}):
        return (
            "No defect class is always the most severe. Severity depends on depth, area, location, product grade, forming "
            "and fatigue requirements, and the applicable acceptance standard. Deep inclusions or pits can be structurally "
            "important; scratches or patches may be cosmetic or rejectable depending on specification."
        )
    if "human" in tokens and tokens.intersection({"inspector", "inspection", "replace"}):
        return (
            "No. This model is a screening aid and must not replace qualified inspection. A human should review "
            "low-confidence, safety-critical, novel, or reject/accept decisions under the applicable quality standard."
        )
    if "rust" in tokens and tokens.intersection({"detect", "identify", "classify"}):
        return (
            "No—not reliably. Rust is not one of the six trained classes. The model may force it into a known class or "
            "return Unknown, so rust detection requires labeled rust and normal-surface data plus separate validation."
        )
    if tokens.intersection({"aluminum", "aluminium"}) and tokens.intersection({"detect", "defect", "defects"}):
        return (
            "No—not reliably. The classifier was trained for six steel-surface defect classes, not aluminum defects. "
            "Aluminum requires its own representative dataset, training, and independent evaluation."
        )
    return None


def _build_comparison_help_answer() -> str:
    return (
        "Comparison data flow:\n"
        "- Frontend requests GET /compare/metrics.\n"
        "- Backend route in app.py loads AutoML and Custom metrics JSON files.\n"
        "- Backend normalizes both payloads to one schema in comparison.py.\n"
        "- Backend computes per-metric winners (accuracy, precision, recall, F1, latency, false positives, model size).\n"
        "- Frontend renders the table/cards from comparison_rows, wins, and summary.\n\n"
        "Explainability section:\n"
        "- It reads explainability.feature_importance, focus_areas, and advantages from the same payload.\n"
        "- If raw metrics do not provide these fields, backend fallback values are generated from model metrics."
    )


def _answer_metal_question(question: str) -> Optional[str]:
    q_tokens = set(_tokenize(question))
    if "strongest" in q_tokens:
        return (
            "It depends on the use-case. In common engineering contexts, steel is usually "
            "stronger than aluminum, while titanium gives high strength with lower weight."
        )
    for metal, fact in METAL_FACTS.items():
        if metal in q_tokens:
            return fact
    if "metal" in q_tokens:
        return (
            "For metal identification, check color/texture, magnet response, conductivity, "
            "density, and spark test (with proper safety)."
        )
    return None


def retrieve_from_dataset(
    question: str, top_k: int = 1, context_label: Optional[str] = None
) -> List[Dict[str, str]]:
    index = _load_dataset_index()
    if not index:
        return []

    query_tokens = _tokenize(question)
    if not query_tokens:
        return []
    query_tf = {}
    for tok in query_tokens:
        query_tf[tok] = query_tf.get(tok, 0) + 1

    matched_labels = _matched_defect_labels(query_tokens)
    if not matched_labels and context_label in LABEL_KEYWORDS:
        matched_labels.add(context_label)

    idf = index.get("idf", {})
    docs = index.get("documents", [])
    avg_len = float(index.get("avg_doc_len", 1.0))

    scored: List[Tuple[float, Dict]] = []
    for doc in docs:
        doc_label = str(doc.get("metadata", {}).get("label", ""))
        if matched_labels:
            if not doc_label:
                continue
            if doc_label not in matched_labels:
                continue
        score = _score_dataset_doc(query_tf, doc, idf, avg_len)
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    results: List[Dict[str, str]] = []
    seen_contents = set()
    for score, doc in scored:
        if len(results) >= top_k:
            break
        raw_title = doc.get("metadata", {}).get("label") or "Dataset QA"
        title = DEFECT_DISPLAY_NAMES.get(str(raw_title), str(raw_title))
        content = _sanitize_answer_text(str(doc.get("output", "")))
        content = _focus_dataset_answer(content, query_tokens)
        content_key = re.sub(r"\s+", " ", content.lower())
        if content_key in seen_contents:
            continue
        seen_contents.add(content_key)
        results.append(
            {
                "title": str(title),
                "content": content,
                "score": f"{score:.4f}",
            }
        )
    return results

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
        results.append({"title": title, "content": _sanitize_answer_text(body), "score": str(score)})
    return results

def _format_top_k(top_k: List[Dict[str, float]]) -> str:
    parts = []
    for item in top_k[:3]:
        name = to_display_label(item.get("class_name", "Unknown"))
        conf = item.get("confidence", 0.0)
        parts.append(f"{name}: {conf:.1%}")
    return ", ".join(parts)

def _defect_title(defect_code: str) -> str:
    return DEFECT_LABELS.get(defect_code, to_display_label(defect_code))

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
    query_tokens = _tokenize(question)
    explicit_labels = _matched_defect_labels(query_tokens)
    uses_prediction = bool(prediction) and _uses_prediction_context(question, query_tokens)
    context_label = _prediction_label(prediction) if uses_prediction and not explicit_labels else None

    if uses_prediction and _asks_for_prediction_explanation(question):
        response_parts.append(explain_prediction(prediction))

    mode = os.getenv("ASSISTANT_MODE", "local").strip().lower()
    is_metal = _is_metal_question(query_tokens)
    is_defect = _is_defect_question(query_tokens) or bool(context_label)
    is_catalog = _is_defect_catalog_question(question, query_tokens)
    is_comparison = _is_comparison_question(query_tokens)
    is_precaution = _is_precaution_question(query_tokens)
    operational_answer = _answer_operational_question(question, query_tokens)

    docs: List[Dict[str, str]] = []
    if uses_prediction and _asks_for_prediction_explanation(question) and not _has_detail_intent(query_tokens):
        pass
    elif operational_answer:
        response_parts.append(operational_answer)
    elif is_comparison:
        response_parts.append(_build_comparison_help_answer())
    elif _is_scanner_question(query_tokens):
        response_parts.append(_build_scanner_answer())
    elif is_catalog:
        response_parts.append(_build_defect_catalog_answer(include_precautions=is_precaution))
    elif _is_defect_definition_question(question, query_tokens):
        response_parts.append(_build_defect_definition_answer())
    elif _is_ambiguous_surface_question(query_tokens):
        response_parts.append(
            "Please specify what you want to identify: a metal type or one of the six surface "
            "defects (Crazing, Inclusion, Patches, Pitted Surface, Rolled-in Scale, or Scratches). "
            "If you have an image, scan it first and then ask about the detected result."
        )
    elif is_metal:
        metal_answer = _answer_metal_question(question)
        if metal_answer:
            response_parts.append(metal_answer)
        else:
            docs = retrieve_docs(question)
    elif mode == "dataset" and is_defect:
        docs = retrieve_from_dataset(question, context_label=context_label)
        if not docs:
            docs = retrieve_docs(question)
    else:
        docs = retrieve_docs(question)

    if docs:
        for doc in docs:
            response_parts.append(f"{doc['title']}: {doc['content']}")
    elif not response_parts:
        response_parts.append(
            "I could not find a direct match. Ask about steel defects (crazing, inclusion, patches, "
            "pitted surface, rolled-in scale, scratches) or metal identification."
        )

    return {
        "answer": _sanitize_answer_text("\n\n".join(response_parts)),
        "sources": docs,
        "used_llm": False,
        "assistant_mode": mode or "local",
    }
