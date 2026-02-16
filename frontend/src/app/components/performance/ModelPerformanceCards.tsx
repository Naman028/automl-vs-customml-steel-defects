import React from "react";
import { Activity, Target, TrendingUp, Zap } from "lucide-react";
import { ModelPerformanceMetrics } from "../../services/api";

type ModelPerformanceCardsProps = {
  automlMetrics: ModelPerformanceMetrics;
  customMetrics: ModelPerformanceMetrics;
};

export const ModelPerformanceCards: React.FC<ModelPerformanceCardsProps> = ({
  automlMetrics,
  customMetrics,
}) => {
  const formatMs = (value: number) => `${Number(value).toFixed(2)}ms`;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/30 dark:to-blue-900/20 p-5 rounded-xl border-2 border-blue-200 dark:border-blue-800 hover:scale-105 transition-transform duration-300">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-500 rounded-lg">
            <Target className="w-5 h-5 text-white" />
          </div>
          <span className="text-xs text-blue-700 dark:text-blue-300 uppercase tracking-wider">
            Accuracy
          </span>
        </div>
        <div className="space-y-1">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl text-slate-900 dark:text-white">
              AutoML:
            </span>
            <span className="text-2xl text-blue-600 dark:text-blue-400">
              {automlMetrics.accuracy}%
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl text-slate-900 dark:text-white">
              Custom:
            </span>
            <span className="text-2xl text-green-600 dark:text-green-400">
              {customMetrics.accuracy}%
            </span>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/30 dark:to-purple-900/20 p-5 rounded-xl border-2 border-purple-200 dark:border-purple-800 hover:scale-105 transition-transform duration-300">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-purple-500 rounded-lg">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <span className="text-xs text-purple-700 dark:text-purple-300 uppercase tracking-wider">
            Inference
          </span>
        </div>
        <div className="space-y-1">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl text-slate-900 dark:text-white">
              AutoML:
            </span>
            <span className="text-2xl text-purple-600 dark:text-purple-400">
              {formatMs(automlMetrics.avgInferenceTime)}
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl text-slate-900 dark:text-white">
              Custom:
            </span>
            <span className="text-2xl text-green-600 dark:text-green-400">
              {formatMs(customMetrics.avgInferenceTime)}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/30 dark:to-orange-900/20 p-5 rounded-xl border-2 border-orange-200 dark:border-orange-800 hover:scale-105 transition-transform duration-300">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-orange-500 rounded-lg">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <span className="text-xs text-orange-700 dark:text-orange-300 uppercase tracking-wider">
            Confidence
          </span>
        </div>
        <div className="space-y-1">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl text-slate-900 dark:text-white">
              AutoML:
            </span>
            <span className="text-2xl text-orange-600 dark:text-orange-400">
              {automlMetrics.avgConfidence}%
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl text-slate-900 dark:text-white">
              Custom:
            </span>
            <span className="text-2xl text-green-600 dark:text-green-400">
              {customMetrics.avgConfidence}%
            </span>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950/30 dark:to-emerald-900/20 p-5 rounded-xl border-2 border-emerald-200 dark:border-emerald-800 hover:scale-105 transition-transform duration-300">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-emerald-500 rounded-lg">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <span className="text-xs text-emerald-700 dark:text-emerald-300 uppercase tracking-wider">
            Predictions
          </span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl text-emerald-600 dark:text-emerald-400">
            {automlMetrics.totalPredictions.toLocaleString()}
          </span>
        </div>
        <p className="text-xs text-emerald-700 dark:text-emerald-400 mt-1">
          Total processed
        </p>
      </div>
    </div>
  );
};
