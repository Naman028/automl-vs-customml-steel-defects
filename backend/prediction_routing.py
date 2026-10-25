"""Route optional AutoML predictions without coupling routing to model weights."""

from collections.abc import Callable
import logging
from typing import Any

from PIL import Image

Prediction = dict[str, Any]
Predictor = Callable[[Image.Image], Prediction]
LOGGER = logging.getLogger(__name__)


def optional_prediction(
    image: Image.Image, local: Predictor | None, vertex: Predictor | None, context: str
) -> tuple[Prediction | None, str | None]:
    # Preserve local-first behavior: a local failure is surfaced, not hidden by a paid call.
    predictor = local if local is not None else vertex
    if predictor is None:
        return None, None
    try:
        return predictor(image), None
    except Exception as error:
        LOGGER.warning("Optional AutoML prediction failed context=%s error=%s", context, error)
        return None, str(error)
