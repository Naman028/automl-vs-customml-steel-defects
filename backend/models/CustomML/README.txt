What the model is trained on:
- Dataset: NEU surface defect dataset (folder name: neu_final_dataset).
- Expected structure: neu_final_dataset/{train,val,test}/{class_name}/image files.
- Classes (from ImageFolder folders): Cr, In, PS, Pa, RS, Sc.
- Model: ResNet18 fine-tuned for the dataset's class count.

Local verification steps (CPU works):

  Create venv and install deps:
   python -m venv .venv
   .venv\Scripts\activate  (Windows)
   pip install -r requirements.txt

Run training:
   python -m trainer.train --data_dir path/to/neu_final_dataset --output_dir outputs --epochs 8

Outputs:
- outputs/best.pt
- outputs/metrics.json

Evaluate (precision/recall/F1):
  The training run evaluates on the test split automatically and writes metrics to outputs/metrics.json.
  Open outputs/metrics.json to see per-class precision/recall/F1, macro/weighted averages, and confusion matrix.

Vertex AI steps (clean, repeatable):
1) Enable APIs: Vertex AI, Cloud Storage.
2) Create a GCS bucket in your region.
3) Upload dataset to GCS:
   gsutil -m cp -r neu_final_dataset gs://YOUR_BUCKET/data/neu_final_dataset
4) Package the trainer (this folder already contains setup.py and trainer/__init__.py).
5) Submit a custom job:
   gcloud ai custom-jobs create ^
     --region=YOUR_REGION ^
     --display-name=defect-train ^
     --python-module=trainer.train ^
     --package-path=. ^
     --container-uri=us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-1.py310 ^
     --args="--data_dir=gs://YOUR_BUCKET/data/neu_final_dataset,--epochs=8" ^
     --base-output-dir=gs://YOUR_BUCKET/vertex_outputs/

Notes:
- When AIP_MODEL_DIR is set by Vertex, outputs are written there automatically.
- GCS data paths are supported; data is downloaded to /tmp/data during training.
- Use TRAIN_BATCH_SIZE and TRAIN_NUM_WORKERS env vars to match GPU/CPU on Vertex.
