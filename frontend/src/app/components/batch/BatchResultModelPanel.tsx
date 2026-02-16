import React from "react";
import { PredictionResult } from "../../services/api";

type BatchResultModelPanelProps = {
  title: string;
  titleClass: string;
  accentClass: string;
  borderClass: string;
  result: PredictionResult | null;
};

export const BatchResultModelPanel: React.FC<BatchResultModelPanelProps> = ({
  title,
  titleClass,
  accentClass,
  borderClass,
  result,
}) => {
  if (!result) {
    return (
      <div
        className={`bg-white dark:bg-slate-900 rounded-lg p-3 border ${borderClass} opacity-60`}
      >
        <h4 className={`text-xs uppercase tracking-wider mb-2 ${titleClass}`}>
          {title}
        </h4>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Not available
        </p>
      </div>
    );
  }

  return (
    <div
      className={`bg-white dark:bg-slate-900 rounded-lg p-3 border ${borderClass}`}
    >
      <h4 className={`text-xs uppercase tracking-wider mb-2 ${titleClass}`}>
        {title}
      </h4>
      <p className="text-sm text-slate-900 dark:text-white mb-1">
        {result.defect}
      </p>
      <p className={`${accentClass}`}>{result.confidence}%</p>
      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
        {result.time}ms
      </p>
    </div>
  );
};
