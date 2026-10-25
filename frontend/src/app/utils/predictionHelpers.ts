import { PredictionResult, HistoricalPrediction } from "../services/api";

/**
 * Determines the winner between AutoML and Custom predictions
 */
export const determineWinner = (
  automl: PredictionResult | null,
  custom: PredictionResult | null,
): "AutoML" | "Custom" | "Tie" => {
  if (!automl && !custom) return "Tie";
  if (!automl) return "Custom";
  if (!custom) return "AutoML";

  if (custom.confidence > automl.confidence) return "Custom";
  if (automl.confidence > custom.confidence) return "AutoML";
  return "Tie";
};

/**
 * Creates a history entry from prediction results
 */
export const createHistoryEntry = (
  imageName: string,
  imageData: string,
  automl: PredictionResult | null,
  custom: PredictionResult | null,
): Omit<HistoricalPrediction, "id" | "timestamp"> => ({
  imageName,
  imageData,
  automlDefect: automl?.defect || "N/A",
  customDefect: custom?.defect || "N/A",
  automlConfidence: automl?.confidence || 0,
  customConfidence: custom?.confidence || 0,
  automlTime: automl?.time,
  customTime: custom?.time,
  automlCost: automl?.cost,
  customCost: custom?.cost,
  winner: determineWinner(automl, custom),
});

/**
 * Converts file to base64 data URL
 */
export const fileToDataUrl = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target?.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};
