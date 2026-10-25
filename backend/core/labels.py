"""Shared label normalization for AutoML/class-name consistency."""

from typing import Dict, Iterable, List

CANONICAL_AUTOML_LABELS = [
    "Crazing",
    "Inclusion",
    "Scratches",
    "Pitted_Surface",
    "Rolled_in_Scale",
    "Patches",
]

_ALIASES_TO_CANONICAL: Dict[str, str] = {
    "crazing": "Crazing",
    "inclusion": "Inclusion",
    "scratches": "Scratches",
    "patches": "Patches",
    "pitted": "Pitted_Surface",
    "pitted surface": "Pitted_Surface",
    "pitted_surface": "Pitted_Surface",
    "rolled-in scale": "Rolled_in_Scale",
    "rolled in scale": "Rolled_in_Scale",
    "rolled_in_scale": "Rolled_in_Scale",
}

_SHORT_TO_CANONICAL: Dict[str, str] = {
    "Cr": "Crazing",
    "In": "Inclusion",
    "Pa": "Patches",
    "PS": "Pitted_Surface",
    "RS": "Rolled_in_Scale",
    "Sc": "Scratches",
}

_CANONICAL_TO_SHORT: Dict[str, str] = {
    "Crazing": "Cr",
    "Inclusion": "In",
    "Patches": "Pa",
    "Pitted_Surface": "PS",
    "Rolled_in_Scale": "RS",
    "Scratches": "Sc",
}

_DISPLAY_LABELS: Dict[str, str] = {
    "Crazing": "Crazing",
    "Inclusion": "Inclusion",
    "Patches": "Patches",
    "Pitted_Surface": "Pitted",
    "Rolled_in_Scale": "Rolled-in Scale",
    "Scratches": "Scratches",
}


def normalize_automl_label(label: str) -> str:
    key = (label or "").strip()
    if not key:
        return key
    if key in _SHORT_TO_CANONICAL:
        return _SHORT_TO_CANONICAL[key]
    return _ALIASES_TO_CANONICAL.get(key.lower(), key)


def normalize_automl_labels(labels: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for label in labels:
        norm = normalize_automl_label(label)
        if norm and norm not in seen:
            seen.add(norm)
            out.append(norm)
    return out


def automl_to_short_code(label: str) -> str:
    canonical = normalize_automl_label(label)
    return _CANONICAL_TO_SHORT.get(canonical, canonical)


def to_display_label(label: str) -> str:
    canonical = normalize_automl_label(label)
    return _DISPLAY_LABELS.get(canonical, _SHORT_TO_CANONICAL.get(canonical, canonical))
