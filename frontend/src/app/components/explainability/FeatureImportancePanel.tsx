import React from "react";
import { Brain } from "lucide-react";

export type FeatureImportance = {
  feature: string;
  importance: number;
  description: string;
};

type FeatureImportancePanelProps = {
  title: string;
  subtitle: string;
  headerClass: string;
  accentClass: string;
  barClass: string;
  features: FeatureImportance[];
};

export const FeatureImportancePanel: React.FC<FeatureImportancePanelProps> = ({
  title,
  subtitle,
  headerClass,
  accentClass,
  barClass,
  features,
}) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg overflow-hidden">
      <div className={`px-6 py-4 text-white ${headerClass}`}>
        <h3 className="text-lg flex items-center gap-2">
          <Brain className="w-5 h-5" />
          {title}
        </h3>
        <p className="text-xs mt-1">{subtitle}</p>
      </div>

      <div className="p-6 space-y-4">
        {features.length === 0 && (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            No performance indicators available for this model export.
          </p>
        )}
        {features.map((feature, index) => (
          <div
            key={feature.feature}
            className="space-y-2"
            style={{ animation: `fadeInUp 0.4s ease-out ${index * 0.1}s both` }}
          >
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-700 dark:text-slate-300">
                {feature.feature}
              </span>
              <span className={`text-sm ${accentClass}`}>
                {feature.importance}%
              </span>
            </div>
            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2.5 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${barClass}`}
                style={{
                  width: `${feature.importance}%`,
                  transitionDelay: `${index * 0.1}s`,
                }}
              ></div>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {feature.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
