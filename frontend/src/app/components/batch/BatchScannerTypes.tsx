import { PredictionResult } from "../../services/api";

export interface BatchResult {
  fileName: string;
  imageData: string;
  automl: PredictionResult | null;
  custom: PredictionResult | null;
}
