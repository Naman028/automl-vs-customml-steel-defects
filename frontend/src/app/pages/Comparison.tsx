import React, { useCallback, useEffect, useRef, useState } from "react";
import { ComparisonTable } from "../components/ComparisonTable";
import { ModelPerformanceDashboard } from "../components/performance/ModelPerformanceDashboard";
import { HistoricalAnalytics } from "../components/history/HistoricalAnalytics";
import { ModelExplainability } from "../components/explainability/ModelExplainability";
import { AdvancedMetricsDashboard } from "../components/advanced/AdvancedMetricsDashboard";
import {
  BarChart3,
  Activity,
  TrendingUp,
  Brain,
  LineChart,
  RefreshCw,
  Wifi,
  WifiOff,
} from "lucide-react";
import {
  ComparisonMetricsResponse,
  getComparisonMetrics,
} from "../services/api";

export const Comparison: React.FC = () => {
  const refreshIntervalMs = 5000;
  const [activeTab, setActiveTab] = useState<
    "metrics" | "performance" | "advanced" | "history" | "explainability"
  >("metrics");
  const [comparisonData, setComparisonData] =
    useState<ComparisonMetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const requestInFlight = useRef(false);

  const loadComparison = useCallback(
    async (initial = false, signal?: AbortSignal) => {
      if (requestInFlight.current) return;
      requestInFlight.current = true;
      if (initial) setLoading(true);
      else setRefreshing(true);

      try {
        const data = await getComparisonMetrics(signal);
        setComparisonData(data);
        setLastUpdated(new Date());
        setError(null);
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load comparison metrics",
        );
      } finally {
        requestInFlight.current = false;
        setLoading(false);
        setRefreshing(false);
      }
    },
    [],
  );

  useEffect(() => {
    const controller = new AbortController();
    void loadComparison(true, controller.signal);

    const intervalId = window.setInterval(() => {
      if (document.visibilityState === "visible") {
        void loadComparison(false, controller.signal);
      }
    }, refreshIntervalMs);

    const handleVisibility = () => {
      if (document.visibilityState === "visible") {
        void loadComparison(false, controller.signal);
      }
    };
    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      controller.abort();
      window.clearInterval(intervalId);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [loadComparison]);

  const tabs = [
    { id: "metrics" as const, label: "Model Metrics", icon: BarChart3 },
    { id: "performance" as const, label: "Performance", icon: TrendingUp },
    { id: "advanced" as const, label: "Advanced", icon: LineChart },
    {
      id: "explainability" as const,
      label: "Evaluation Insights",
      icon: Brain,
    },
    { id: "history" as const, label: "History", icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-3xl text-slate-900 dark:text-white tracking-tight mb-2">
              AutoML vs Custom ML Analysis
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Live comparison from the latest backend evaluation metrics
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div
              className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-xs ${error ? "border-amber-300 bg-amber-50 text-amber-700 dark:border-amber-700 dark:bg-amber-900/20 dark:text-amber-300" : "border-emerald-300 bg-emerald-50 text-emerald-700 dark:border-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300"}`}
            >
              {error ? (
                <WifiOff className="h-4 w-4" />
              ) : (
                <Wifi className="h-4 w-4" />
              )}
              <span>
                {error
                  ? "Live update interrupted"
                  : `Live · ${lastUpdated ? lastUpdated.toLocaleTimeString() : "connecting"}`}
              </span>
            </div>
            <button
              type="button"
              onClick={() => void loadComparison(false)}
              disabled={refreshing}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
              aria-label="Refresh comparison metrics"
            >
              <RefreshCw
                className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
              />
              Refresh
            </button>
          </div>
        </div>

        <div className="mb-6 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950 dark:border-amber-700 dark:bg-amber-950/30 dark:text-amber-100">
          <p className="font-semibold">
            Internal benchmark — independent generalization unverified
          </p>
          <p className="mt-1">
            These scores use 180 NEU test images from the same dataset source as
            training. A perfect score on this split does not establish
            performance on new camera images. Custom ML counts predictions below
            55% confidence as Unknown; AutoML currently always chooses a class.
            Confidence is shown for context and does not count as a model win.
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
                    ? "border-slate-700 dark:border-slate-400 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
                    : "border-transparent hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-600 dark:text-slate-400"
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
          {(activeTab === "metrics" ||
            activeTab === "performance" ||
            activeTab === "advanced" ||
            activeTab === "explainability") &&
            loading && (
              <div className="flex items-center justify-center h-64">
                <div className="w-16 h-16 border-4 border-slate-300 dark:border-slate-700 border-t-slate-700 dark:border-t-slate-300 rounded-full animate-spin"></div>
              </div>
            )}

          {(activeTab === "metrics" ||
            activeTab === "performance" ||
            activeTab === "advanced" ||
            activeTab === "explainability") &&
            !loading &&
            error &&
            !comparisonData && (
              <div className="rounded-xl border-2 border-red-300 bg-red-50 dark:bg-red-900/20 dark:border-red-700 p-4 text-red-700 dark:text-red-300">
                {error}
              </div>
            )}

          {activeTab === "metrics" && comparisonData && (
            <ComparisonTable comparison={comparisonData} />
          )}
          {activeTab === "performance" && comparisonData && (
            <ModelPerformanceDashboard comparison={comparisonData} />
          )}
          {activeTab === "advanced" && comparisonData && (
            <AdvancedMetricsDashboard comparison={comparisonData} />
          )}
          {activeTab === "explainability" && comparisonData && (
            <ModelExplainability comparison={comparisonData} />
          )}
          {activeTab === "history" && <HistoricalAnalytics />}
        </div>
      </div>
    </div>
  );
};
