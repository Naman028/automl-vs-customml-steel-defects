import React from "react";
import { Clock } from "lucide-react";
import { PredictionResult } from "../../services/api";

type PredictionModelCardProps = {
  result: PredictionResult;
  title: string;
  icon: React.ReactNode;
  accentTextClass: string;
  borderClass: string;
  bgClass: string;
  confidenceWinner?: boolean;
  timeWinner?: boolean;
};

export const PredictionModelCard: React.FC<PredictionModelCardProps> = ({
  result,
  title,
  icon,
  accentTextClass,
  borderClass,
  bgClass,
  confidenceWinner,
  timeWinner,
}) => {
  const renderConfidenceBar = (confidence: number) => {
    const width = confidence;
    const color =
      confidence >= 90
        ? "bg-green-500"
        : confidence >= 80
          ? "bg-yellow-500"
          : "bg-orange-500";

    return (
      <div className="flex items-center gap-2">
        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-6 overflow-hidden">
          <div
            className={`${color} h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
            style={{ width: `${width}%` }}
          >
            <span className="text-xs text-white drop-shadow">
              {confidence}%
            </span>
          </div>
        </div>
      </div>
    );
  };

  const renderTopK = (topK?: Array<{ label: string; confidence: number }>) => {
    if (!topK || topK.length === 0) return null;
    return (
      <div className="mt-3 text-xs text-gray-600 dark:text-gray-400">
        <div className="mb-1 uppercase tracking-wide">Top Predictions</div>
        <div className="flex flex-wrap gap-2">
          {topK.map((item) => (
            <span
              key={item.label}
              className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full px-2 py-1"
            >
              {item.label} ({item.confidence}%)
            </span>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className={`${bgClass} rounded-lg p-4 border ${borderClass}`}>
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <h4 className="text-lg text-gray-900 dark:text-white">{title}</h4>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-700 dark:text-gray-300">
              Detected Defect
            </span>
            <span className={accentTextClass}>{result.defect}</span>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-700 dark:text-gray-300">Confidence</span>
            {confidenceWinner && (
              <span className="text-xs text-green-600 dark:text-green-400">
                Winner
              </span>
            )}
          </div>
          {renderConfidenceBar(result.confidence)}
          {renderTopK(result.topK)}
        </div>

        <div className="grid grid-cols-1 gap-3">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-1">
              <Clock className="w-4 h-4" />
              <span>Inference Time</span>
            </div>
            <div className="flex items-center justify-between">
              <p className="text-lg text-gray-900 dark:text-white">
                {result.time}ms
              </p>
              {timeWinner && (
                <span className="text-xs text-green-600 dark:text-green-400">
                  Winner
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
