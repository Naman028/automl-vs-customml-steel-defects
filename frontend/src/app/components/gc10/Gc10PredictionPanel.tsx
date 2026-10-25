import React, { useState } from "react";
import { Gc10Prediction, predictGc10 } from "../../services/api/gc10";

const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

export function Gc10PredictionPanel({
  modelAvailable,
}: {
  modelAvailable: boolean;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [prediction, setPrediction] = useState<Gc10Prediction | null>(null);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState("");

  async function runPrediction() {
    if (!file) return;
    if (file.size > MAX_IMAGE_BYTES) {
      setError("Choose an image smaller than 5 MB.");
      return;
    }
    setPredicting(true);
    setError("");
    setPrediction(null);
    try {
      setPrediction(await predictGc10(file));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Prediction failed");
    } finally {
      setPredicting(false);
    }
  }

  return (
    <section className="rounded-xl border border-slate-200 dark:border-slate-700 p-5 space-y-3">
      <h2 className="text-xl">Try a GC10 image</h2>
      <p className="text-sm">
        The model predicts category presence. It does not draw defect boxes or
        certify defect-free steel.
      </p>
      {!modelAvailable && (
        <p>
          Restore or train the local checkpoint to enable predictions. Saved
          experiment results remain available.
        </p>
      )}
      {error && (
        <p role="alert" className="text-red-600">
          {error}
        </p>
      )}
      <input
        aria-label="GC10 image"
        type="file"
        disabled={!modelAvailable || predicting}
        accept="image/jpeg,image/png,image/webp,image/bmp"
        onChange={(event) => {
          setFile(event.target.files?.[0] ?? null);
          setPrediction(null);
          setError("");
        }}
      />
      <button
        className="ml-3 rounded-lg bg-slate-800 text-white px-4 py-2 disabled:opacity-50"
        disabled={!file || predicting || !modelAvailable}
        onClick={() => void runPrediction()}
      >
        {predicting ? "Predicting..." : "Predict categories"}
      </button>
      {prediction && (
        <div aria-live="polite">
          <p>
            {prediction.predicted_labels.length
              ? prediction.predicted_labels
                  .map((label) => label.replaceAll("_", " "))
                  .join(", ")
              : "No category reached its threshold. This does not establish that the surface is defect-free."}
          </p>
          <ul className="mt-3 grid gap-2 sm:grid-cols-2">
            {prediction.classes.map((item) => (
              <li key={item.class_name} className="text-sm capitalize">
                {item.class_name.replaceAll("_", " ")}:{" "}
                {(item.probability * 100).toFixed(1)}%
                {item.predicted ? " - selected" : ""}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
