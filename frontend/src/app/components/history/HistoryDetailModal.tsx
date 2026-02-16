import React from "react";
import { Award, Clock, Eye, X } from "lucide-react";
import { format } from "date-fns";
import { HistoricalPrediction } from "../../services/api";

type HistoryDetailModalProps = {
  prediction: HistoricalPrediction;
  onClose: () => void;
};

export const HistoryDetailModal: React.FC<HistoryDetailModalProps> = ({
  prediction,
  onClose,
}) => {
  return (
    <div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-gradient-to-r from-slate-100 to-slate-50 dark:from-slate-700 dark:to-slate-800 px-6 py-4 border-b-2 border-slate-200 dark:border-slate-700 flex justify-between items-center">
          <h3 className="text-xl text-slate-900 dark:text-white">
            Prediction Details
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {prediction.imageData ? (
            <div className="relative aspect-video bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800 rounded-xl border-2 border-slate-300 dark:border-slate-600 overflow-hidden">
              <img
                src={prediction.imageData}
                alt={prediction.imageName}
                className="w-full h-full object-contain"
              />
              <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white p-2 text-sm text-center">
                {prediction.imageName}
              </div>
            </div>
          ) : (
            <div className="relative aspect-video bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800 rounded-xl border-2 border-slate-300 dark:border-slate-600 flex items-center justify-center">
              <div className="text-center">
                <Eye className="w-16 h-16 text-slate-400 dark:text-slate-500 mx-auto mb-2" />
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {prediction.imageName}
                </p>
              </div>
            </div>
          )}

          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <Clock className="w-4 h-4" />
            {format(prediction.timestamp, "MMMM dd, yyyy - HH:mm:ss")}
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700/50 dark:to-slate-800/50 p-5 rounded-xl border border-slate-200 dark:border-slate-600">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  AutoML Model
                </h4>
                {prediction.winner === "AutoML" && (
                  <Award className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                )}
              </div>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
                    Defect Type
                  </p>
                  <p className="text-lg text-slate-900 dark:text-white">
                    {prediction.automlDefect}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
                    Confidence
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-200 dark:bg-slate-600 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full"
                        style={{ width: `${prediction.automlConfidence}%` }}
                      />
                    </div>
                    <span className="text-sm text-slate-900 dark:text-white">
                      {prediction.automlConfidence}%
                    </span>
                  </div>
                </div>
                {prediction.automlTime && (
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
                      Inference Time
                    </p>
                    <p className="text-sm text-slate-700 dark:text-slate-300">
                      {prediction.automlTime}ms
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700/50 dark:to-slate-800/50 p-5 rounded-xl border border-slate-200 dark:border-slate-600">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Custom Model
                </h4>
                {prediction.winner === "Custom" && (
                  <Award className="w-5 h-5 text-green-600 dark:text-green-400" />
                )}
              </div>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
                    Defect Type
                  </p>
                  <p className="text-lg text-slate-900 dark:text-white">
                    {prediction.customDefect}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
                    Confidence
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-200 dark:bg-slate-600 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full"
                        style={{ width: `${prediction.customConfidence}%` }}
                      />
                    </div>
                    <span className="text-sm text-slate-900 dark:text-white">
                      {prediction.customConfidence}%
                    </span>
                  </div>
                </div>
                {prediction.customTime && (
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
                      Inference Time
                    </p>
                    <p className="text-sm text-slate-700 dark:text-slate-300">
                      {prediction.customTime}ms
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
