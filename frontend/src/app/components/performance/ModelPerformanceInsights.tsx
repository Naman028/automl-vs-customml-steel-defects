import React from "react";
import { Clock, TrendingUp, ShieldCheck } from "lucide-react";
import { ComparisonMetricsResponse, ModelPerformanceMetrics } from "../../services/api";

type ModelPerformanceInsightsProps = {
  comparison: ComparisonMetricsResponse;
  automlMetrics: ModelPerformanceMetrics;
  customMetrics: ModelPerformanceMetrics;
};

export const ModelPerformanceInsights: React.FC<
  ModelPerformanceInsightsProps
> = ({ comparison, automlMetrics, customMetrics }) => {
  const formatMs = (value: number) => `${Number(value).toFixed(2)}ms`;
  const winnerLabel =
    comparison.summary.winner === "custom"
      ? "Custom ML"
      : comparison.summary.winner === "automl"
      ? "AutoML"
      : "Tie";
  const accuracyDelta = (customMetrics.accuracy - automlMetrics.accuracy).toFixed(1);
  const speedup =
    customMetrics.avgInferenceTime > 0
      ? (automlMetrics.avgInferenceTime / customMetrics.avgInferenceTime).toFixed(2)
      : "N/A";

  return (
    <div className="grid md:grid-cols-3 gap-4">
      <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900 p-5 rounded-xl border-2 border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 bg-green-500 rounded-lg">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <h4 className="text-sm text-slate-700 dark:text-slate-300">
            Winner: {winnerLabel}
          </h4>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          Comparison result from deterministic metric rules. Accuracy delta:{" "}
          <strong className="text-green-600 dark:text-green-400">
            {accuracyDelta}%
          </strong>{" "}
          (Custom - AutoML). {comparison.summary.reason}
        </p>
      </div>

      <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900 p-5 rounded-xl border-2 border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 bg-blue-500 rounded-lg">
            <Clock className="w-5 h-5 text-white" />
          </div>
          <h4 className="text-sm text-slate-700 dark:text-slate-300">
            Speed Advantage
          </h4>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          Relative latency speedup:{" "}
          <strong className="text-blue-600 dark:text-blue-400">
            {speedup}x
          </strong>{" "}
          ({formatMs(customMetrics.avgInferenceTime)} vs{" "}
          {formatMs(automlMetrics.avgInferenceTime)}), enabling real-time processing
          capabilities.
        </p>
      </div>

      <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900 p-5 rounded-xl border-2 border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 bg-indigo-500 rounded-lg">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <h4 className="text-sm text-slate-700 dark:text-slate-300">
            Reliability
          </h4>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          Average confidence difference is{" "}
          <strong className="text-indigo-600 dark:text-indigo-400">
            {(customMetrics.avgConfidence - automlMetrics.avgConfidence).toFixed(1)}%
          </strong>{" "}
          (Custom - AutoML), with precision/recall shown in the chart and metric table.
        </p>
      </div>
    </div>
  );
};
