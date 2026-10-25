import { BACKEND_URL } from "./constants";

export type Gc10ClassMetric = {
  class_name: string;
  precision: number;
  recall: number;
  f1: number;
  support: number;
  threshold: number;
};

export type Gc10Metrics = {
  status: "trained";
  model_available: boolean;
  task: string;
  feature_extractor: string;
  limitation: string;
  split_counts: Record<string, number>;
  training_seconds: number;
  epochs_completed: number;
  audit: {
    usable_images: number;
    duplicate_copies_removed: number;
    explicit_label_repairs: Record<string, number>;
    excluded_annotations: Array<{ annotation: string; reason: string }>;
  };
  test: {
    macro_f1: number;
    micro_f1: number;
    mean_average_precision: number;
    exact_match_accuracy: number;
    per_class: Gc10ClassMetric[];
  };
};

export type Gc10Prediction = {
  predicted_labels: string[];
  limitation: string;
  classes: Array<{
    class_name: string;
    probability: number;
    threshold: number;
    predicted: boolean;
  }>;
};

async function readResponse(response: Response) {
  if (!response.ok) throw new Error(`GC10 request failed (${response.status})`);
  return response.json();
}

export async function getGc10Metrics(
  signal?: AbortSignal,
): Promise<Gc10Metrics | { status: "not_trained" }> {
  const payload = await readResponse(
    await fetch(`${BACKEND_URL}/gc10/metrics`, { signal, cache: "no-store" }),
  );
  if (payload.status === "not_trained") return payload;
  if (payload.status !== "trained" || !Array.isArray(payload.test?.per_class)) {
    throw new Error("Invalid GC10 results response");
  }
  return payload;
}

export async function predictGc10(file: File): Promise<Gc10Prediction> {
  const body = new FormData();
  body.append("file", file);
  return readResponse(
    await fetch(`${BACKEND_URL}/gc10/predict`, { method: "POST", body }),
  );
}
