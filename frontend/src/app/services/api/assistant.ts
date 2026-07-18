import { BACKEND_URL } from "./constants";
import { PredictionResult } from "./types";

export type AssistantSource = {
  title: string;
  content: string;
  score?: string;
};

export type AssistantResponse = {
  answer: string;
  sources: AssistantSource[];
  used_llm: boolean;
  assistant_mode: string;
};

const DEFECT_TO_BACKEND_LABEL: Record<string, string> = {
  Crazing: "Crazing",
  Inclusion: "Inclusion",
  Patches: "Patches",
  Pitted: "Pitted_Surface",
  "Pitted Surface": "Pitted_Surface",
  "Rolled-in Scale": "Rolled_in_Scale",
  "Rolled in Scale": "Rolled_in_Scale",
  Scratches: "Scratches",
};

function toBackendDefectLabel(defect: string): string {
  return DEFECT_TO_BACKEND_LABEL[defect] || defect;
}

function buildPredictionPayload(prediction?: PredictionResult | null) {
  if (!prediction) {
    return undefined;
  }
  const predictedClass = toBackendDefectLabel(prediction.defect);
  return {
    predicted_class: predictedClass,
    raw_top_class: predictedClass,
    confidence: Math.max(0, Math.min(1, prediction.confidence / 100)),
    threshold: 0.5,
    top_k:
      prediction.topK?.map((item) => ({
        class_name: toBackendDefectLabel(item.label),
        confidence: Math.max(0, Math.min(1, item.confidence / 100)),
      })) ?? [],
  };
}

const PREDICTION_CONTEXT_PATTERNS = [
  /\b(this|current|detected|predicted)\s+(defect|result|prediction)\b/i,
  /\b(what|which)\s+(was|is|did)\s+.{0,20}\b(detect|detected|predict|predicted)\b/i,
  /\b(prediction|result|confidence|top[- ]?k|alternative)\b/i,
  /\b(why)\s+.{0,20}\b(predict|predicted|classification|classified)\b/i,
  /\b(this|detected)\s+(one|issue)\b/i,
];

export function questionUsesPredictionContext(question: string): boolean {
  return PREDICTION_CONTEXT_PATTERNS.some((pattern) => pattern.test(question.trim()));
}

export const askAssistant = async (
  question: string,
  prediction?: PredictionResult | null
): Promise<AssistantResponse> => {
  const response = await fetch(`${BACKEND_URL}/assistant`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      prediction: questionUsesPredictionContext(question)
        ? buildPredictionPayload(prediction)
        : undefined,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `Assistant request failed: ${response.status} - ${errorText}`
    );
  }

  return response.json() as Promise<AssistantResponse>;
};
