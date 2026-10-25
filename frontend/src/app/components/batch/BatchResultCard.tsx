import React from "react";
import { BatchResult } from "./BatchScannerTypes";
import { BatchResultModelPanel } from "./BatchResultModelPanel";
import { BatchResultWinner } from "./BatchResultWinner";

type BatchResultCardProps = {
  result: BatchResult;
  index: number;
};

export const BatchResultCard: React.FC<BatchResultCardProps> = ({
  result,
  index,
}) => {
  return (
    <div
      className="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 border-2 border-slate-200 dark:border-slate-700"
      style={{ animation: `fadeInUp 0.3s ease-out ${index * 0.05}s both` }}
    >
      <div className="grid md:grid-cols-4 gap-4">
        <div>
          <img
            src={result.imageData}
            alt={result.fileName}
            className="w-full h-32 object-cover rounded-lg"
          />
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 truncate">
            {result.fileName}
          </p>
        </div>

        <BatchResultModelPanel
          title="AutoML"
          titleClass="text-blue-700 dark:text-blue-300"
          accentClass="text-lg text-blue-600 dark:text-blue-400"
          borderClass="border-blue-200 dark:border-blue-800"
          result={result.automl}
        />

        <BatchResultModelPanel
          title="Custom ML"
          titleClass="text-green-700 dark:text-green-300"
          accentClass="text-lg text-green-600 dark:text-green-400"
          borderClass="border-green-200 dark:border-green-800"
          result={result.custom}
        />

        <div className="flex items-center justify-center">
          <BatchResultWinner automl={result.automl} custom={result.custom} />
        </div>
      </div>
    </div>
  );
};
