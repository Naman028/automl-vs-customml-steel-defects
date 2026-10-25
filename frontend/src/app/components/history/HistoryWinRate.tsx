import React from "react";

type HistoryWinRateProps = {
  automlWins: number;
  customWins: number;
  ties: number;
  total: number;
};

export const HistoryWinRate: React.FC<HistoryWinRateProps> = ({
  automlWins,
  customWins,
  ties,
  total,
}) => {
  const automlRate = total ? (automlWins / total) * 100 : 0;
  const customRate = total ? (customWins / total) * 100 : 0;
  const tieRate = total ? (ties / total) * 100 : 0;

  return (
    <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-lg">
      <h3 className="text-lg text-slate-900 dark:text-white mb-4">
        Performance Head-to-Head
      </h3>

      <div className="space-y-4">
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">
              AutoML Model
            </span>
            <span className="text-sm text-slate-600 dark:text-slate-400">
              {automlWins} wins ({automlRate.toFixed(1)}%)
            </span>
          </div>
          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-4 overflow-hidden">
            <div
              className="bg-gradient-to-r from-slate-400 to-slate-600 h-full rounded-full transition-all duration-1000"
              style={{ width: `${automlRate}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">
              Custom Model
            </span>
            <span className="text-sm text-slate-600 dark:text-slate-400">
              {customWins} wins ({customRate.toFixed(1)}%)
            </span>
          </div>
          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-4 overflow-hidden">
            <div
              className="bg-gradient-to-r from-slate-500 to-slate-700 h-full rounded-full transition-all duration-1000"
              style={{ width: `${customRate}%` }}
            ></div>
          </div>
        </div>

        {ties > 0 && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-slate-700 dark:text-slate-300">
                Ties
              </span>
              <span className="text-sm text-slate-600 dark:text-slate-400">
                {ties} ({tieRate.toFixed(1)}%)
              </span>
            </div>
            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-4 overflow-hidden">
              <div
                className="bg-gradient-to-r from-slate-300 to-slate-500 h-full rounded-full transition-all duration-1000"
                style={{ width: `${tieRate}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
