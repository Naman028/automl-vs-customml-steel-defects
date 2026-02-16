import React from "react";
import { AlertCircle } from "lucide-react";
import { CostAnalysis } from "../../services/api";

type CostRoiAnalysisProps = {
  costData: CostAnalysis;
};

export const CostRoiAnalysis: React.FC<CostRoiAnalysisProps> = ({
  costData,
}) => {
  const breakEvenMonths = Math.ceil(
    costData.custom.setupCost / costData.savings,
  );

  return (
    <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900 p-6 rounded-xl border-2 border-slate-200 dark:border-slate-700">
      <h3 className="text-lg text-slate-900 dark:text-white mb-4 flex items-center gap-2">
        <AlertCircle className="w-5 h-5" />
        Return on Investment (ROI) Analysis
      </h3>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm text-slate-700 dark:text-slate-300 mb-3 uppercase tracking-wider">
            Break-even Analysis
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Custom ML Setup Cost:
              </span>
              <span className="text-slate-900 dark:text-white">
                ${costData.custom.setupCost}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Monthly Savings:
              </span>
              <span className="text-green-600 dark:text-green-400">
                ${costData.savings}
              </span>
            </div>
            <div className="flex justify-between pt-2 border-t border-slate-200 dark:border-slate-700">
              <span className="text-sm text-slate-700 dark:text-slate-300">
                Break-even Period:
              </span>
              <span className="text-lg text-purple-600 dark:text-purple-400">
                {breakEvenMonths} months
              </span>
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-sm text-slate-700 dark:text-slate-300 mb-3 uppercase tracking-wider">
            Cost Per Prediction
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                AutoML per prediction:
              </span>
              <span className="text-blue-600 dark:text-blue-400">$3.50</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Custom ML per prediction:
              </span>
              <span className="text-green-600 dark:text-green-400">$0.80</span>
            </div>
            <div className="flex justify-between pt-2 border-t border-slate-200 dark:border-slate-700">
              <span className="text-sm text-slate-700 dark:text-slate-300">
                Savings per prediction:
              </span>
              <span className="text-lg text-purple-600 dark:text-purple-400">
                $2.70 (77%)
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-green-50 dark:bg-green-950/20 border-2 border-green-200 dark:border-green-800 rounded-lg">
        <p className="text-sm text-green-800 dark:text-green-200">
          <strong>Recommendation:</strong> Custom ML model provides superior
          cost efficiency at scale. Initial setup investment of $
          {costData.custom.setupCost} pays off within {breakEvenMonths} months,
          with annual savings of ${(costData.savings * 12).toLocaleString()}{" "}
          compared to AutoML.
        </p>
      </div>
    </div>
  );
};
