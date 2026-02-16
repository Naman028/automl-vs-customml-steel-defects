import React from "react";
import { CheckCircle2, DollarSign, TrendingDown } from "lucide-react";
import { CostAnalysis } from "../../services/api";

type CostSummaryCardsProps = {
  costData: CostAnalysis;
};

export const CostSummaryCards: React.FC<CostSummaryCardsProps> = ({
  costData,
}) => {
  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/30 dark:to-blue-900/20 p-6 rounded-xl border-2 border-blue-200 dark:border-blue-800">
        <div className="flex items-center gap-2 mb-3">
          <DollarSign className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <span className="text-sm text-blue-700 dark:text-blue-300 uppercase tracking-wider">
            AutoML Monthly
          </span>
        </div>
        <div className="text-3xl text-blue-700 dark:text-blue-300 mb-1">
          ${costData.automl.totalMonthly.toLocaleString()}
        </div>
        <p className="text-xs text-blue-600 dark:text-blue-400">Per month</p>
      </div>

      <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/30 dark:to-green-900/20 p-6 rounded-xl border-2 border-green-200 dark:border-green-800">
        <div className="flex items-center gap-2 mb-3">
          <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
          <span className="text-sm text-green-700 dark:text-green-300 uppercase tracking-wider">
            Custom ML Monthly
          </span>
        </div>
        <div className="text-3xl text-green-700 dark:text-green-300 mb-1">
          ${costData.custom.totalMonthly.toLocaleString()}
        </div>
        <p className="text-xs text-green-600 dark:text-green-400">Per month</p>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/30 dark:to-purple-900/20 p-6 rounded-xl border-2 border-purple-200 dark:border-purple-800">
        <div className="flex items-center gap-2 mb-3">
          <TrendingDown className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <span className="text-sm text-purple-700 dark:text-purple-300 uppercase tracking-wider">
            Monthly Savings
          </span>
        </div>
        <div className="text-3xl text-purple-700 dark:text-purple-300 mb-1">
          ${costData.savings.toLocaleString()}
        </div>
        <p className="text-xs text-purple-600 dark:text-purple-400">
          With Custom ML
        </p>
      </div>

      <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/30 dark:to-orange-900/20 p-6 rounded-xl border-2 border-orange-200 dark:border-orange-800">
        <div className="flex items-center gap-2 mb-3">
          <CheckCircle2 className="w-5 h-5 text-orange-600 dark:text-orange-400" />
          <span className="text-sm text-orange-700 dark:text-orange-300 uppercase tracking-wider">
            Cost Reduction
          </span>
        </div>
        <div className="text-3xl text-orange-700 dark:text-orange-300 mb-1">
          {costData.savingsPercentage}%
        </div>
        <p className="text-xs text-orange-600 dark:text-orange-400">
          Lower costs
        </p>
      </div>
    </div>
  );
};
