from pathlib import Path
import argparse
import numpy as np
from PIL import Image
import tensorflow as tf


BASE_DIR = Path(__file__).resolve().parent

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
        "python run_tflite.py --image \"C:\\path\\to\\image.jpg\""
    )

labels = None
if LABELS_PATH.exists():
    labels = [line.strip() for line in LABELS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]

interpreter = tf.lite.Interpreter(model_path=str(MODEL_PATH))
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Inspect input shape
in_shape = input_details[0]["shape"]
_, h, w, _ = in_shape
print("Input shape:", in_shape)
print("Output details:", output_details)

# Load and preprocess image
img = Image.open(IMAGE_PATH).convert("RGB").resize((w, h))
x = np.array(img)

# Match model input type
input_dtype = input_details[0]["dtype"]
if input_dtype == np.float32:
    x = x.astype(np.float32) / 255.0
else:
    x = x.astype(input_dtype)

x = np.expand_dims(x, axis=0)
interpreter.set_tensor(input_details[0]["index"], x)
interpreter.invoke()

output = interpreter.get_tensor(output_details[0]["index"])
print("Output:", output)

if labels:
    scores = output[0]
    top_idx = int(np.argmax(scores))
    top_label = labels[top_idx] if top_idx < len(labels) else f"index_{top_idx}"
    print(f"Top label: {top_label}")
