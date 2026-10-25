import React from "react";
import { Brain, Eye, Target, Zap } from "lucide-react";

type ExplainabilityHeaderProps = {
  focusAreas: string[];
};

export const ExplainabilityHeader: React.FC<ExplainabilityHeaderProps> = ({
  focusAreas,
}) => {
  const focusText =
    focusAreas.length > 0
      ? focusAreas.slice(0, 3).join(", ")
      : "No focus areas provided in model metrics";

  return (
    <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900 p-6 rounded-xl border-2 border-slate-200 dark:border-slate-700">
      <div className="flex items-center gap-3 mb-3">
        <div className="p-3 bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl">
          <Brain className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl text-slate-900 dark:text-white tracking-tight">
            Evaluation Insights
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Aggregate evaluation summaries; not explanations of individual
            predictions
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mt-6">
        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <Eye className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Focus Areas
            </span>
          </div>
          <p className="text-sm text-slate-700 dark:text-slate-300">
            {focusText}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-5 h-5 text-green-600 dark:text-green-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Precision
            </span>
          </div>
          <p className="text-sm text-slate-700 dark:text-slate-300">
            Custom model uses engineered features for higher accuracy
          </p>
        </div>

        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Speed
            </span>
          </div>
          <p className="text-sm text-slate-700 dark:text-slate-300">
            Optimized feature extraction enables real-time processing
          </p>
        </div>
      </div>
    </div>
  );
};
