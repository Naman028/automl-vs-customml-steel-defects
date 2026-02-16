import React from "react";
import { PredictionResult } from "../../services/api";

type BatchResultWinnerProps = {
  automl: PredictionResult | null;
  custom: PredictionResult | null;
};

export const BatchResultWinner: React.FC<BatchResultWinnerProps> = ({
  automl,
  custom,
}) => {
  if (custom && automl) {
    if (custom.confidence > automl.confidence) {
      return (
        <div className="text-center">
          <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mb-2 mx-auto">
            <span className="text-2xl">WIN</span>
          </div>
          <p className="text-sm text-green-700 dark:text-green-300">
            Custom Wins
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            +{(custom.confidence - automl.confidence).toFixed(1)}%
          </p>
        </div>
      );
    }

    if (automl.confidence > custom.confidence) {
      return (
        <div className="text-center">
          <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mb-2 mx-auto">
            <span className="text-2xl">WIN</span>
          </div>
          <p className="text-sm text-blue-700 dark:text-blue-300">
            AutoML Wins
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            +{(automl.confidence - custom.confidence).toFixed(1)}%
          </p>
        </div>
      );
    }

    return (
      <div className="text-center">
        <div className="w-12 h-12 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mb-2 mx-auto">
          <span className="text-2xl">TIE</span>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-400">Tie</p>
      </div>
    );
  }

  if (custom) {
    return (
      <div className="text-center">
        <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mb-2 mx-auto">
          <span className="text-2xl">OK</span>
        </div>
        <p className="text-sm text-green-700 dark:text-green-300">
          Custom result
        </p>
      </div>
    );
  }

  if (automl) {
    return (
      <div className="text-center">
        <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mb-2 mx-auto">
          <span className="text-2xl">OK</span>
        </div>
        <p className="text-sm text-blue-700 dark:text-blue-300">
          AutoML result
        </p>
      </div>
    );
  }

  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mb-2 mx-auto">
        <span className="text-2xl">N/A</span>
      </div>
      <p className="text-sm text-slate-600 dark:text-slate-400">No result</p>
    </div>
  );
};
