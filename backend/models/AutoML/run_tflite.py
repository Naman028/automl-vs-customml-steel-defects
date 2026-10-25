import logging
from pathlib import Path
import argparse
import sys
import numpy as np
from PIL import Image
import tensorflow as tf

logger = logging.getLogger(__name__)

try:
    from label_normalization import normalize_automl_label, normalize_automl_labels
except ImportError:
    _BACKEND_DIR = Path(__file__).resolve().parents[2]
    if str(_BACKEND_DIR) not in sys.path:
        sys.path.append(str(_BACKEND_DIR))
    from label_normalization import normalize_automl_label, normalize_automl_labels


BASE_DIR = Path(__file__).resolve().parent
from automl_contract import prepare_image, read_contract, embedded_labels

parser = argparse.ArgumentParser(description="Run AutoML TFLite model on a test image.")
parser.add_argument(
    "--model",
    default=str(BASE_DIR / "AutoML model.tflite"),
    help="Path to .tflite model file",
)
parser.add_argument(
    "--image",
    default=str(BASE_DIR / "test.jpg"),
    help="Path to input image",
)
parser.add_argument(
    "--labels",
    default=str(BASE_DIR / "labels.txt"),
    help="Path to labels.txt",
)
args = parser.parse_args()

MODEL_PATH = Path(args.model)
IMAGE_PATH = Path(args.image)
LABELS_PATH = Path(args.labels)

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
if not IMAGE_PATH.exists():
    raise FileNotFoundError(
        f"Test image not found: {IMAGE_PATH}\n"
        "Pass a valid image path via --image, for example:\n"
        'python run_tflite.py --image "C:\\path\\to\\image.jpg"'
    )

labels = None
if LABELS_PATH.exists():
    labels = normalize_automl_labels(
        [
            line.strip()
            for line in LABELS_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    )

interpreter = tf.lite.Interpreter(model_path=str(MODEL_PATH))
if labels != embedded_labels(MODEL_PATH):
    raise ValueError("AutoML labels must match embedded output label order")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Inspect input shape
in_shape = input_details[0]["shape"]
_, h, w, _ = in_shape
logger.info(
    " ".join(
        str(value)
        for value in (
            "Input shape:",
            in_shape,
        )
    )
)
logger.info(
    " ".join(
        str(value)
        for value in (
            "Output details:",
            output_details,
        )
    )
)

# Load and preprocess image
with Image.open(IMAGE_PATH) as img:
    x = prepare_image(img, input_details[0], read_contract(str(MODEL_PATH.resolve())))
interpreter.set_tensor(input_details[0]["index"], x)
interpreter.invoke()

output = interpreter.get_tensor(output_details[0]["index"])
logger.info(
    " ".join(
        str(value)
        for value in (
            "Output:",
            output,
        )
    )
)

if labels:
    scores = output[0]
    top_idx = int(np.argmax(scores))
    top_label = normalize_automl_label(
        labels[top_idx] if top_idx < len(labels) else f"index_{top_idx}"
    )
    logger.info(" ".join(str(value) for value in (f"Top label: {top_label}",)))
