import React from "react";
import { Brain, TrendingUp, Zap } from "lucide-react";
import { PredictionResult } from "../../services/api";
import { PredictionModelCard } from "./PredictionModelCard";

interface PredictionTableProps {
  predictions: {
    automl: PredictionResult | null;
    custom: PredictionResult | null;
  };
}

export const PredictionTable: React.FC<PredictionTableProps> = ({
  predictions,
}) => {
  const getWinner = (
    automlValue: number | undefined,
    customValue: number | undefined,
    lowerIsBetter = false,
  ) => {
    if (!automlValue || !customValue) return null;
    if (lowerIsBetter) {
      return customValue < automlValue ? "custom" : "automl";
    }
    return customValue > automlValue ? "custom" : "automl";
  };

  const confidenceWinner = getWinner(
    predictions.automl?.confidence,
    predictions.custom?.confidence,
  );
  const timeWinner = getWinner(
    predictions.automl?.time,
    predictions.custom?.time,
    true,
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl text-gray-900 dark:text-white">
          Prediction Results
        </h3>
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <TrendingUp className="w-4 h-4" />
          <span>
            {predictions.automl && predictions.custom ? "Dual" : "Single"} Model
            Analysis
          </span>
        </div>
      </div>

      {predictions.automl && (
        <PredictionModelCard
          result={predictions.automl}
          title="AutoML Model"
          icon={<Brain className="w-5 h-5 text-blue-600 dark:text-blue-400" />}
          accentTextClass="text-blue-600 dark:text-blue-400"
          borderClass="border-blue-200 dark:border-blue-800"
          bgClass="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20"
          confidenceWinner={confidenceWinner === "automl"}
          timeWinner={timeWinner === "automl"}
        />
      )}

      {predictions.custom && (
        <PredictionModelCard
          result={predictions.custom}
          title="Custom Model"
          icon={<Zap className="w-5 h-5 text-green-600 dark:text-green-400" />}
          accentTextClass="text-green-600 dark:text-green-400"
          borderClass="border-green-200 dark:border-green-800"
          bgClass="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20"
          confidenceWinner={confidenceWinner === "custom"}
          timeWinner={timeWinner === "custom"}
        />
      )}

      {predictions.automl && predictions.custom && null}
    </div>
  );
};
