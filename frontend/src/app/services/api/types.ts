export interface SteelDefect {
  name: string;
  displayName: string;
  description: string;
  severity: "Low" | "Medium" | "High";
  imageUrl: string;
}

export interface PredictionResult {
  model: string;
  defect: string;
  confidence: number;
  time: number;
  cost: number;
  topK?: Array<{ label: string; confidence: number }>;
  inferenceTime?: number;
  memoryUsage?: number;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1Score?: number;
}

export interface HistoricalPrediction {
  id: string;
  timestamp: Date;
  imageName: string;
  imageData?: string;
  automlDefect: string;
  customDefect: string;
  automlConfidence: number;
  customConfidence: number;
  automlTime?: number;
  customTime?: number;
  automlCost?: number;
  customCost?: number;
  winner: "AutoML" | "Custom" | "Tie";
}

export interface ModelPerformanceMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  avgInferenceTime: number;
  totalPredictions: number;
  avgConfidence: number;
}

export type WinnerType = "automl" | "custom" | "tie" | "none";

export interface ModelMetricsSchema {
  metadata: {
    model_name: string;
    run_id: string;
    timestamp: number;
    dataset_version: string;
    sample_count: number;
    classes: string[];
  };
  core: {
    accuracy: number | null;
    precision: number | null;
    recall: number | null;
    f1: number | null;
    confidence: number | null;
    inference_ms: {
      mean: number | null;
      p50: number | null;
      p95: number | null;
      min: number | null;
      max: number | null;
    };
  };
  ops: {
    training_time: string | number | null;
    model_size_mb: number | null;
    gpu_required: boolean | null;
    setup_complexity: string | null;
    false_positive_rate: number | null;
  };
  explainability: {
    feature_importance: Array<{
      feature: string;
      importance: number;
      description?: string;
    }>;
    focus_areas: string[];
    advantages: string[];
  };
  details: {
    confusion_matrix: number[][];
    y_true?: number[];
    y_pred?: number[];
    probabilities?: number[][];
    per_class_metrics?: Array<{
      class_name: string;
      precision: number;
      recall: number;
      f1: number;
      support: number;
    }>;
    pr_curves?: Record<
      string,
      {
        precision: number[];
        recall: number[];
        thresholds: number[];
      }
    >;
    threshold_metrics?: {
      thresholds: number[];
      precision: number[];
      recall: number[];
      coverage?: number[];
    };
    dataset_counts?: {
      train: number;
      val: number;
      test: number;
      total: number;
    };
  };
}

export interface ComparisonMetricsResponse {
  automl: ModelMetricsSchema;
  custom: ModelMetricsSchema;
  wins: {
    automl: number;
    custom: number;
  };
  per_metric_winners: Record<string, WinnerType>;
  comparison_rows: Array<{
    key: string;
    metric: string;
    automl: string;
    custom: string;
    winner: WinnerType;
  }>;
  summary: {
    winner: WinnerType;
    reason: string;
  };
}

export interface MetalType {
  name: string;
  displayName: string;
  description: string;
  properties: string;
  imageUrl: string;
  color: string;
}

export type BackendPredictResponse = {
  predicted_class: string;
  confidence: number;
  all_probabilities: Record<string, number>;
  top_k?: Array<{ class_name: string; confidence: number }>;
  raw_top_class: string;
  threshold: number;
  inference_time_ms?: number;
};
