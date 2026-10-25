import React from "react";
import { Award, TrendingUp } from "lucide-react";

type HistorySummaryStatsProps = {
  automlWins: number;
  customWins: number;
  avgAutomlConfidence: number;
  avgCustomConfidence: number;
  total: number;
};

export const HistorySummaryStats: React.FC<HistorySummaryStatsProps> = ({
  automlWins,
  customWins,
  avgAutomlConfidence,
  avgCustomConfidence,
  total,
}) => {
  const automlRate = total ? (automlWins / total) * 100 : 0;
  const customRate = total ? (customWins / total) * 100 : 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-2 mb-2">
          <Award className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
            AutoML Wins
          </span>
        </div>
        <div className="text-3xl text-slate-900 dark:text-white">
          {automlWins}
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          {automlRate.toFixed(1)}% win rate
        </p>
      </div>

      <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-2 mb-2">
          <Award className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
            Custom Wins
          </span>
        </div>
        <div className="text-3xl text-slate-900 dark:text-white">
          {customWins}
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          {customRate.toFixed(1)}% win rate
        </p>
      </div>

      <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
            Avg AutoML
          </span>
        </div>
        <div className="text-3xl text-slate-900 dark:text-white">
          {avgAutomlConfidence.toFixed(1)}%
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Confidence
        </p>
      </div>

      <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
            Avg Custom
          </span>
        </div>
        <div className="text-3xl text-slate-900 dark:text-white">
          {avgCustomConfidence.toFixed(1)}%
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Confidence
        </p>
      </div>
    </div>
  );
};
