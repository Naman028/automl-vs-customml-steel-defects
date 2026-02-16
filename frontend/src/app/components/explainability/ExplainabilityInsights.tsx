import React from 'react';
import { Brain } from 'lucide-react';

type ExplainabilityInsightsProps = {
  automlAdvantages: string[];
  customAdvantages: string[];
};

export const ExplainabilityInsights: React.FC<ExplainabilityInsightsProps> = ({
  automlAdvantages,
  customAdvantages,
}) => {
  const automlItems =
    automlAdvantages.length > 0
      ? automlAdvantages
      : ["No AutoML explainability advantages provided in metrics payload."];
  const customItems =
    customAdvantages.length > 0
      ? customAdvantages
      : ["No Custom ML explainability advantages provided in metrics payload."];

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/30 dark:to-blue-900/20 p-6 rounded-xl border-2 border-blue-200 dark:border-blue-800">
        <h4 className="text-sm text-blue-900 dark:text-blue-200 uppercase tracking-wider mb-3 flex items-center gap-2">
          <Brain className="w-4 h-4" />
          AutoML Approach
        </h4>
        <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
          {automlItems.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-blue-500 mt-1">-</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/30 dark:to-green-900/20 p-6 rounded-xl border-2 border-green-200 dark:border-green-800">
        <h4 className="text-sm text-green-900 dark:text-green-200 uppercase tracking-wider mb-3 flex items-center gap-2">
          <Brain className="w-4 h-4" />
          Custom ML Advantage
        </h4>
        <ul className="space-y-2 text-sm text-green-800 dark:text-green-200">
          {customItems.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-green-500 mt-1">-</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
