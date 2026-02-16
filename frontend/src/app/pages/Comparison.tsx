import React, { useEffect, useState } from 'react';
import { ComparisonTable } from '../components/ComparisonTable';
import { ModelPerformanceDashboard } from '../components/performance/ModelPerformanceDashboard';
import { HistoricalAnalytics } from '../components/history/HistoricalAnalytics';
import { ModelExplainability } from '../components/explainability/ModelExplainability';
import { AdvancedMetricsDashboard } from '../components/advanced/AdvancedMetricsDashboard';
import { BarChart3, Activity, TrendingUp, Brain, LineChart } from 'lucide-react';
import { ComparisonMetricsResponse, getComparisonMetrics } from '../services/api';

export const Comparison: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'metrics' | 'performance' | 'advanced' | 'history' | 'explainability'>('metrics');
  const [comparisonData, setComparisonData] = useState<ComparisonMetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getComparisonMetrics();
        setComparisonData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load comparison metrics');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const tabs = [
    { id: 'metrics' as const, label: 'Model Metrics', icon: BarChart3 },
    { id: 'performance' as const, label: 'Performance', icon: TrendingUp },
    { id: 'advanced' as const, label: 'Advanced', icon: LineChart },
    { id: 'explainability' as const, label: 'Explainability', icon: Brain },
    { id: 'history' as const, label: 'History', icon: Activity }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl text-slate-900 dark:text-white tracking-tight mb-2">
            AutoML vs Custom ML Analysis
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Comprehensive comparison of Google Cloud Vertex AI models
          </p>
        </div>

        {/* Tabs Navigation */}
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-lg border-2 border-slate-200 dark:border-slate-700 mb-6 overflow-hidden">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 min-w-[150px] px-6 py-4 flex items-center justify-center gap-2 transition-all duration-300 border-b-4 ${
                  activeTab === tab.id
                    ? 'border-slate-700 dark:border-slate-400 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white'
                    : 'border-transparent hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-600 dark:text-slate-400'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span className="text-sm tracking-wide">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="animate-fadeIn">
          {(activeTab === 'metrics' || activeTab === 'performance' || activeTab === 'advanced' || activeTab === 'explainability') && loading && (
            <div className="flex items-center justify-center h-64">
              <div className="w-16 h-16 border-4 border-slate-300 dark:border-slate-700 border-t-slate-700 dark:border-t-slate-300 rounded-full animate-spin"></div>
            </div>
          )}

          {(activeTab === 'metrics' || activeTab === 'performance' || activeTab === 'advanced' || activeTab === 'explainability') && !loading && error && (
            <div className="rounded-xl border-2 border-red-300 bg-red-50 dark:bg-red-900/20 dark:border-red-700 p-4 text-red-700 dark:text-red-300">
              {error}
            </div>
          )}

          {activeTab === 'metrics' && comparisonData && <ComparisonTable comparison={comparisonData} />}
          {activeTab === 'performance' && comparisonData && <ModelPerformanceDashboard comparison={comparisonData} />}
          {activeTab === 'advanced' && comparisonData && <AdvancedMetricsDashboard comparison={comparisonData} />}
          {activeTab === 'explainability' && comparisonData && <ModelExplainability comparison={comparisonData} />}
          {activeTab === 'history' && <HistoricalAnalytics />}
        </div>
      </div>
    </div>
  );
};
