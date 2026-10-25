import React from "react";
import {
  ComparisonMetricsResponse,
  ModelPerformanceMetrics,
} from "../../services/api";
import { ModelPerformanceCards } from "./ModelPerformanceCards";
import { ModelPerformanceCharts } from "./ModelPerformanceCharts";
import { ModelPerformanceInsights } from "./ModelPerformanceInsights";

type ModelPerformanceDashboardProps = {
  comparison: ComparisonMetricsResponse;
};

const toPercent = (value: number | null | undefined): number =>
  typeof value === "number" ? Math.round(value * 1000) / 10 : 0;

export const ModelPerformanceDashboard: React.FC<
  ModelPerformanceDashboardProps
> = ({ comparison }) => {
  const automlMetrics: ModelPerformanceMetrics = {
    accuracy: toPercent(comparison.automl.core.accuracy),
    precision: toPercent(comparison.automl.core.precision),
    recall: toPercent(comparison.automl.core.recall),
    f1Score: toPercent(comparison.automl.core.f1),
    avgInferenceTime: comparison.automl.core.inference_ms.mean ?? 0,
    totalPredictions: comparison.automl.metadata.sample_count ?? 0,
    avgConfidence: toPercent(comparison.automl.core.confidence),
  };

  const customMetrics: ModelPerformanceMetrics = {
    accuracy: toPercent(comparison.custom.core.accuracy),
    precision: toPercent(comparison.custom.core.precision),
    recall: toPercent(comparison.custom.core.recall),
    f1Score: toPercent(comparison.custom.core.f1),
    avgInferenceTime: comparison.custom.core.inference_ms.mean ?? 0,
    totalPredictions: comparison.custom.metadata.sample_count ?? 0,
    avgConfidence: toPercent(comparison.custom.core.confidence),
  };

  return (
    <div className="space-y-6">
      <ModelPerformanceCards
        automlMetrics={automlMetrics}
        customMetrics={customMetrics}
      />
      <ModelPerformanceCharts
        automlMetrics={automlMetrics}
        customMetrics={customMetrics}
      />
      <ModelPerformanceInsights
        comparison={comparison}
        automlMetrics={automlMetrics}
        customMetrics={customMetrics}
      />
    </div>
  );
};
