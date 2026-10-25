import { BACKEND_URL, CLASS_MAP } from "./constants";
import { BackendPredictResponse, PredictionResult } from "./types";

// API adapter for inference routes. Keeps backend payload parsing in one place.
type ModelSelection = "both" | "automl" | "custom";
type PredictionPair = {
  automl: PredictionResult | null;
  custom: PredictionResult | null;
};

async function dataUrlToFile(
  dataUrl: string,
  filename = "upload.jpg",
): Promise<File> {
  const res = await fetch(dataUrl);
  const blob = await res.blob();
  return new File([blob], filename, { type: blob.type || "image/jpeg" });
}

function formatPredictionResult(
  backendResult: BackendPredictResponse,
  modelName: string,
): PredictionResult {
  const displayName =
    CLASS_MAP[backendResult.predicted_class] || backendResult.predicted_class;
  const confidenceRaw =
    typeof backendResult.confidence === "number" ? backendResult.confidence : 0;
  const confidencePercent = Math.round(confidenceRaw * 100);
  const inferenceTime = backendResult.inference_time_ms || 100;
  const topK = backendResult.top_k?.map((item) => ({
    label: CLASS_MAP[item.class_name] || item.class_name,
    confidence: Math.round(item.confidence * 100),
  }));

  return {
    model: modelName,
    defect: displayName,
    confidence: confidencePercent,
    time: Math.round(inferenceTime),
    cost: modelName === "AutoML" ? 3.5 : 0.8,
    inferenceTime: Math.round(inferenceTime),
    memoryUsage: modelName === "AutoML" ? 450 : 120,
    topK,
  };
}

async function postFormData<T>(url: string, formData: FormData): Promise<T> {
  // Shared network/error wrapper so single and batch flows behave identically.
  const response = await fetch(url, { method: "POST", body: formData });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Backend error: ${response.status} - ${errorText}`);
  }
  return response.json() as Promise<T>;
}

function asModelResult(
  result: BackendPredictResponse | null | undefined,
  modelName: "AutoML" | "Custom",
): PredictionResult | null {
  return result ? formatPredictionResult(result, modelName) : null;
}

function mapPredictResponse(
  backendResult: Record<string, any>,
  modelSelection: ModelSelection,
): PredictionPair {
  // `both` mode returns nested `{ custom, automl }`; single-model modes return a flat payload.
  if (backendResult.custom || backendResult.automl) {
    return {
      custom: asModelResult(
        backendResult.custom as BackendPredictResponse,
        "Custom",
      ),
      automl: asModelResult(
        backendResult.automl as BackendPredictResponse,
        "AutoML",
      ),
    };
  }

  if (modelSelection === "automl") {
    return {
      custom: null,
      automl: formatPredictionResult(
        backendResult as BackendPredictResponse,
        "AutoML",
      ),
    };
  }

  return {
    custom: formatPredictionResult(
      backendResult as BackendPredictResponse,
      "Custom",
    ),
    automl: null,
  };
}

function buildErrorPrediction(): PredictionResult {
  return {
    model: "Custom",
    defect: "Error",
    confidence: 0,
    time: 0,
    cost: 0,
    inferenceTime: 0,
    memoryUsage: 0,
  };
}

export const scanImage = async (
  imageData: string,
  modelSelection: ModelSelection = "both",
): Promise<PredictionPair> => {
  const file = await dataUrlToFile(imageData, "scan.jpg");
  const formData = new FormData();
  formData.append("file", file);

  const backendResult = await postFormData<Record<string, any>>(
    `${BACKEND_URL}/predict?model_type=${modelSelection}`,
    formData,
  );
  return mapPredictResponse(backendResult, modelSelection);
};

export const scanBatchImages = async (
  images: string[],
  modelSelection: ModelSelection = "both",
): Promise<PredictionPair[]> => {
  const files = await Promise.all(
    images.map((img, idx) => dataUrlToFile(img, `batch_${idx + 1}.jpg`)),
  );

  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const batchResponse = await postFormData<{ results: Record<string, any>[] }>(
    `${BACKEND_URL}/predict/batch?model_type=${modelSelection}`,
    formData,
  );

  return batchResponse.results.map((result) => {
    // Batch keeps per-file errors inline so we preserve array length and ordering for the UI.
    if (result.error) {
      return {
        automl: null,
        custom: buildErrorPrediction(),
      };
    }

    return mapPredictResponse(result, modelSelection);
  });
};
