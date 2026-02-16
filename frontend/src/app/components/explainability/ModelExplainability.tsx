import React from 'react';
import { ExplainabilityHeader } from './ExplainabilityHeader';
import { ExplainabilityInsights } from './ExplainabilityInsights';
import { FeatureImportance, FeatureImportancePanel } from './FeatureImportancePanel';
import { ComparisonMetricsResponse } from '../../services/api';

type ModelExplainabilityProps = {
  comparison: ComparisonMetricsResponse;
};

export const ModelExplainability: React.FC<ModelExplainabilityProps> = ({ comparison }) => {
  const automlFeatures: FeatureImportance[] = comparison.automl.explainability.feature_importance.map((f) => ({
    feature: f.feature,
    importance: f.importance,
    description: f.description ?? '',
  }));

  const customFeatures: FeatureImportance[] = comparison.custom.explainability.feature_importance.map((f) => ({
    feature: f.feature,
    importance: f.importance,
    description: f.description ?? '',
  }));

  const focusAreas = [
    ...comparison.automl.explainability.focus_areas,
    ...comparison.custom.explainability.focus_areas,
  ];

  return (
    <div className="space-y-6">
      <ExplainabilityHeader focusAreas={focusAreas} />

      <div className="grid lg:grid-cols-2 gap-6">
        <FeatureImportancePanel
          title="AutoML Feature Importance"
          subtitle="Automated feature selection"
          headerClass="bg-gradient-to-r from-blue-500 to-blue-600"
          accentClass="text-blue-600 dark:text-blue-400"
          barClass="bg-gradient-to-r from-blue-500 to-blue-600"
          features={automlFeatures}
        />
        <FeatureImportancePanel
          title="Custom ML Feature Importance"
          subtitle="Hand-crafted optimized features"
          headerClass="bg-gradient-to-r from-green-500 to-green-600"
          accentClass="text-green-600 dark:text-green-400"
          barClass="bg-gradient-to-r from-green-500 to-green-600"
          features={customFeatures}
        />
      </div>

      <ExplainabilityInsights
        automlAdvantages={comparison.automl.explainability.advantages}
        customAdvantages={comparison.custom.explainability.advantages}
      />
    </div>
  );
};
