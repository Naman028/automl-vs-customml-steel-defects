import React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { DollarSign } from "lucide-react";
import { CostAnalysis } from "../../services/api";

type CostChartsProps = {
  costData: CostAnalysis;
};

export const CostCharts: React.FC<CostChartsProps> = ({ costData }) => {
  const monthlyComparisonData = [
    {
      category: "Setup",
      AutoML: costData.automl.setupCost,
      Custom: costData.custom.setupCost,
    },
    {
      category: "Inference",
      AutoML: costData.automl.monthlyInferenceCost,
      Custom: costData.custom.monthlyInferenceCost,
    },
    {
      category: "Training",
      AutoML: costData.automl.trainingCost,
      Custom: costData.custom.trainingCost,
    },
  ];

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg">
        <h3 className="text-lg text-slate-900 dark:text-white mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5" />
          Monthly Cost Breakdown
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthlyComparisonData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="category" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #475569",
                borderRadius: "8px",
                color: "#fff",
              }}
              formatter={(value) => `$${value}`}
            />
            <Legend />
            <Bar dataKey="AutoML" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            <Bar dataKey="Custom" fill="#10b981" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg">
        <h3 className="text-lg text-slate-900 dark:text-white mb-4">
          Annual Cost Projection
        </h3>

        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                AutoML (12 months)
              </span>
              <span className="text-xl text-blue-600 dark:text-blue-400">
                ${(costData.automl.totalMonthly * 12).toLocaleString()}
              </span>
            </div>
            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-blue-500 h-full rounded-full"
                style={{ width: "100%" }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Custom ML (12 months)
              </span>
              <span className="text-xl text-green-600 dark:text-green-400">
                ${(costData.custom.totalMonthly * 12).toLocaleString()}
              </span>
            </div>
            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-green-500 h-full rounded-full"
                style={{
                  width: `${(costData.custom.totalMonthly / costData.automl.totalMonthly) * 100}%`,
                }}
              ></div>
            </div>
          </div>

          <div className="pt-4 border-t-2 border-slate-200 dark:border-slate-700">
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-700 dark:text-slate-300">
                Annual Savings
              </span>
              <span className="text-2xl text-purple-600 dark:text-purple-400">
                ${(costData.savings * 12).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
