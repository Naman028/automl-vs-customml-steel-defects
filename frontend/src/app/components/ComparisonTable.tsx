import React from "react";
import { useAuth } from "../contexts/AuthContext";
import { ComparisonMetricsResponse } from "../services/api";
import { Download, Trophy, BarChart3 } from "lucide-react";
import { Button } from "./ui/button";

type ComparisonTableProps = {
  comparison: ComparisonMetricsResponse;
};

export const ComparisonTable: React.FC<ComparisonTableProps> = ({
  comparison,
}) => {
  const { user } = useAuth();
  const rows = comparison.comparison_rows;
  const metricCount = rows.length;

  const handleExport = () => {
    const headers = ["Metric", "AutoML", "Custom ML", "Winner"];
    const csvRows = rows.map((m) => [m.metric, m.automl, m.custom, m.winner]);
    const csv = [headers, ...csvRows].map((row) => row.join(",")).join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `steel-defect-comparison-${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const customWins = comparison.wins.custom;
  const automlWins = comparison.wins.automl;
  const summaryParts = comparison.summary.reason.split("|").map((s) => s.trim());

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 transition-colors duration-300">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl text-gray-900 dark:text-white mb-2">
            {metricCount}-Metric Model Comparison
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            AutoML vs Custom ML Performance Analysis
          </p>
        </div>
        {user?.role === "admin" && (
          <Button onClick={handleExport} className="bg-green-600 hover:bg-green-700">
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                AutoML Wins
              </p>
              <p className="text-3xl text-blue-600 dark:text-blue-400">
                {automlWins}
              </p>
            </div>
            <BarChart3 className="w-10 h-10 text-blue-600 dark:text-blue-400 opacity-50" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                Custom ML Wins
              </p>
              <p className="text-3xl text-purple-600 dark:text-purple-400">
                {customWins}
              </p>
            </div>
            <Trophy className="w-10 h-10 text-purple-600 dark:text-purple-400 opacity-50" />
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-200 dark:border-gray-700">
              <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">
                Metric
              </th>
              <th className="text-center py-3 px-4 text-blue-600 dark:text-blue-400">
                AutoML
              </th>
              <th className="text-center py-3 px-4 text-purple-600 dark:text-purple-400">
                Custom ML
              </th>
              <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300">
                Winner
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((metric, index) => (
              <tr
                key={`${metric.key}-${index}`}
                className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
              >
                <td className="py-4 px-4 text-gray-900 dark:text-white">
                  {metric.metric}
                </td>
                <td
                  className={`py-4 px-4 text-center ${
                    metric.winner === "automl"
                      ? "bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                      : "text-gray-600 dark:text-gray-400"
                  }`}
                >
                  {metric.automl}
                </td>
                <td
                  className={`py-4 px-4 text-center ${
                    metric.winner === "custom"
                      ? "bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300"
                      : "text-gray-600 dark:text-gray-400"
                  }`}
                >
                  {metric.custom}
                </td>
                <td className="py-4 px-4 text-center">
                  {metric.winner === "automl" && (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm">
                      AutoML
                    </span>
                  )}
                  {metric.winner === "custom" && (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full text-sm">
                      Custom
                    </span>
                  )}
                  {metric.winner === "tie" && (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-full text-sm">
                      Tie
                    </span>
                  )}
                  {metric.winner === "none" && (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-full text-sm">
                      N/A
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Performance
          </p>
          <p className="text-lg text-yellow-700 dark:text-yellow-300">
            {summaryParts[0] ?? "See winner counts above"}
          </p>
        </div>

        <div className="bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 rounded-lg p-4 border border-indigo-200 dark:border-indigo-800">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Accuracy
          </p>
          <p className="text-lg text-indigo-700 dark:text-indigo-300">
            {summaryParts[1] ?? "See table for metric deltas"}
          </p>
        </div>

        <div className="bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20 rounded-lg p-4 border border-emerald-200 dark:border-emerald-800">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Stability
          </p>
          <p className="text-lg text-emerald-700 dark:text-emerald-300">
            {summaryParts[2] ?? "Balanced precision and recall"}
          </p>
        </div>
      </div>
    </div>
  );
};
