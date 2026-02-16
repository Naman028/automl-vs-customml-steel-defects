import React from "react";
import { Activity, Award, Clock, Eye } from "lucide-react";
import { format } from "date-fns";
import { HistoricalPrediction } from "../../services/api";

type HistoryTableProps = {
  history: HistoricalPrediction[];
  onSelect: (prediction: HistoricalPrediction) => void;
};

export const HistoryTable: React.FC<HistoryTableProps> = ({
  history,
  onSelect,
}) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-lg overflow-hidden">
      <div className="px-6 py-4 bg-gradient-to-r from-slate-100 to-slate-50 dark:from-slate-700 dark:to-slate-800 border-b border-slate-200 dark:border-slate-700">
        <h3 className="text-lg text-slate-900 dark:text-white flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Recent Predictions History
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th className="px-4 py-3 text-left text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  Time
                </div>
              </th>
              <th className="px-4 py-3 text-left text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                Image
              </th>
              <th className="px-4 py-3 text-left text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                Defect Type
              </th>
              <th className="px-4 py-3 text-center text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                AutoML
              </th>
              <th className="px-4 py-3 text-center text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                Custom
              </th>
              <th className="px-4 py-3 text-center text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                Winner
              </th>
              <th className="px-4 py-3 text-center text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
            {history.length === 0 ? (
              <tr>
                <td
                  colSpan={7}
                  className="px-4 py-8 text-center text-slate-500 dark:text-slate-400"
                >
                  No predictions yet. Upload images to see history here.
                </td>
              </tr>
            ) : (
              history.map((item, index) => (
                <tr
                  key={item.id}
                  className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
                  style={{
                    animation: `fadeInUp 0.3s ease-out ${index * 0.05}s both`,
                  }}
                >
                  <td className="px-4 py-3 text-sm text-slate-600 dark:text-slate-400">
                    {format(item.timestamp, "MMM dd, HH:mm")}
                  </td>
                  <td className="px-4 py-3">
                    {item.imageData ? (
                      <img
                        src={item.imageData}
                        alt={item.imageName}
                        className="w-16 h-16 object-cover rounded-lg border border-slate-200 dark:border-slate-700"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-lg flex items-center justify-center">
                        <Eye className="w-6 h-6 text-slate-400" />
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex px-3 py-1 text-xs bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full">
                      {item.customDefect !== "N/A"
                        ? item.customDefect
                        : item.automlDefect}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-flex px-3 py-1 text-sm rounded-lg ${
                        item.winner === "AutoML"
                          ? "bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold"
                          : "text-slate-600 dark:text-slate-400"
                      }`}
                    >
                      {item.automlConfidence}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-flex px-3 py-1 text-sm rounded-lg ${
                        item.winner === "Custom"
                          ? "bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold"
                          : "text-slate-600 dark:text-slate-400"
                      }`}
                    >
                      {item.customConfidence}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {item.winner === "AutoML" && (
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white rounded-full text-xs">
                        <Award className="w-3 h-3" />
                        AutoML
                      </span>
                    )}
                    {item.winner === "Custom" && (
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white rounded-full text-xs">
                        <Award className="w-3 h-3" />
                        Custom
                      </span>
                    )}
                    {item.winner === "Tie" && (
                      <span className="text-slate-500 dark:text-slate-400 text-xs">
                        Tie
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => onSelect(item)}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 rounded-lg text-xs transition-colors"
                    >
                      <Eye className="w-3 h-3" />
                      View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
