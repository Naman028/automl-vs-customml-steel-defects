import React from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ComparisonMetricsResponse } from "../../services/api";

type AdvancedMetricsDashboardProps = {
  comparison: ComparisonMetricsResponse;
};

const toPct = (v: number) => `${(v * 100).toFixed(1)}%`;

const buildThresholdSeries = (
  thresholds: number[] = [],
  precision: number[] = [],
  recall: number[] = [],
  coverage: number[] = []
) =>
  thresholds.map((t, i) => ({
    threshold: Number(t.toFixed(2)),
    precision: (precision[i] ?? 0) * 100,
    recall: (recall[i] ?? 0) * 100,
    coverage: (coverage[i] ?? 0) * 100,
  }));

const buildAvgPrSeries = (
  prCurves: Record<string, { precision: number[]; recall: number[]; thresholds: number[] }> = {}
) => {
  const buckets = new Map<number, { sum: number; count: number }>();
  Object.values(prCurves).forEach((curve) => {
    const n = Math.min(curve.recall.length, curve.precision.length);
    for (let i = 0; i < n; i += 1) {
      const recallPct = Math.max(0, Math.min(100, curve.recall[i] * 100));
      const precisionPct = Math.max(0, Math.min(100, curve.precision[i] * 100));
      const recallBucket = Math.round(recallPct);
      const prev = buckets.get(recallBucket) ?? { sum: 0, count: 0 };
      buckets.set(recallBucket, { sum: prev.sum + precisionPct, count: prev.count + 1 });
    }
  });
  const rows: Array<{ recall: number; precision: number }> = Array.from(buckets.entries()).map(
    ([recall, agg]) => ({
      recall,
      precision: agg.count > 0 ? agg.sum / agg.count : 0,
    })
  );
  rows.sort((a, b) => a.recall - b.recall);
  return rows;
};

const ConfusionMatrixCard: React.FC<{
  title: string;
  classes: string[];
  cm: number[][];
}> = ({ title, classes, cm }) => (
  <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg p-4 overflow-x-auto">
    <h4 className="text-sm text-slate-700 dark:text-slate-300 mb-3">{title}</h4>
    <table className="text-xs min-w-full">
      <thead>
        <tr>
          <th className="p-2 text-left text-slate-600 dark:text-slate-400">True/Pred</th>
          {classes.map((c) => (
            <th key={c} className="p-2 text-slate-600 dark:text-slate-400">
              {c}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {cm.map((row, i) => {
          const rowTotal = row.reduce((a, b) => a + b, 0) || 1;
          return (
            <tr key={`${title}-${i}`} className="border-t border-slate-200 dark:border-slate-700">
              <td className="p-2 text-slate-700 dark:text-slate-300">{classes[i] ?? i}</td>
              {row.map((value, j) => {
                const normalized = value / rowTotal;
                const alpha = Math.max(0.08, normalized);
                const bg =
                  i === j
                    ? `rgba(16,185,129,${alpha})`
                    : `rgba(59,130,246,${Math.max(0.04, alpha * 0.7)})`;
                return (
                  <td key={`${i}-${j}`} className="p-2 text-center text-slate-700 dark:text-slate-300" style={{ backgroundColor: bg }}>
                    {value}
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

const PerClassTable: React.FC<{
  title: string;
  rows: Array<{ class_name: string; precision: number; recall: number; f1: number; support: number }>;
}> = ({ title, rows }) => (
  <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg p-4 overflow-x-auto">
    <h4 className="text-sm text-slate-700 dark:text-slate-300 mb-3">{title}</h4>
    <table className="text-xs min-w-full">
      <thead>
        <tr>
          <th className="p-2 text-left text-slate-600 dark:text-slate-400">Class</th>
          <th className="p-2 text-slate-600 dark:text-slate-400">Precision</th>
          <th className="p-2 text-slate-600 dark:text-slate-400">Recall</th>
          <th className="p-2 text-slate-600 dark:text-slate-400">F1</th>
          <th className="p-2 text-slate-600 dark:text-slate-400">Support</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={`${title}-${r.class_name}`} className="border-t border-slate-200 dark:border-slate-700">
            <td className="p-2 text-slate-700 dark:text-slate-300">{r.class_name}</td>
            <td className="p-2 text-center text-slate-700 dark:text-slate-300">{toPct(r.precision)}</td>
            <td className="p-2 text-center text-slate-700 dark:text-slate-300">{toPct(r.recall)}</td>
            <td className="p-2 text-center text-slate-700 dark:text-slate-300">{toPct(r.f1)}</td>
            <td className="p-2 text-center text-slate-700 dark:text-slate-300">{r.support}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export const AdvancedMetricsDashboard: React.FC<AdvancedMetricsDashboardProps> = ({ comparison }) => {
  const automlThr = comparison.automl.details.threshold_metrics;
  const customThr = comparison.custom.details.threshold_metrics;
  const automlThrSeries = buildThresholdSeries(
    automlThr?.thresholds,
    automlThr?.precision,
    automlThr?.recall,
    automlThr?.coverage
  );
  const customThrSeries = buildThresholdSeries(
    customThr?.thresholds,
    customThr?.precision,
    customThr?.recall,
    customThr?.coverage
  );

  const automlPr = buildAvgPrSeries(comparison.automl.details.pr_curves);
  const customPr = buildAvgPrSeries(comparison.custom.details.pr_curves);

  const counts = comparison.automl.details.dataset_counts ?? comparison.custom.details.dataset_counts;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4">
          <p className="text-xs text-slate-500 dark:text-slate-400">Train Images</p>
          <p className="text-2xl text-slate-900 dark:text-white">{counts?.train ?? "N/A"}</p>
        </div>
        <div className="rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4">
          <p className="text-xs text-slate-500 dark:text-slate-400">Validation Images</p>
          <p className="text-2xl text-slate-900 dark:text-white">{counts?.val ?? "N/A"}</p>
        </div>
        <div className="rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4">
          <p className="text-xs text-slate-500 dark:text-slate-400">Test Images</p>
          <p className="text-2xl text-slate-900 dark:text-white">{counts?.test ?? "N/A"}</p>
        </div>
        <div className="rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4">
          <p className="text-xs text-slate-500 dark:text-slate-400">Total Images</p>
          <p className="text-2xl text-slate-900 dark:text-white">{counts?.total ?? "N/A"}</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <ConfusionMatrixCard
          title="AutoML Confusion Matrix (Counts)"
          classes={comparison.automl.metadata.classes}
          cm={comparison.automl.details.confusion_matrix}
        />
        <ConfusionMatrixCard
          title="Custom ML Confusion Matrix (Counts)"
          classes={comparison.custom.metadata.classes}
          cm={comparison.custom.details.confusion_matrix}
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <PerClassTable
          title="AutoML Per-class Metrics"
          rows={comparison.automl.details.per_class_metrics ?? []}
        />
        <PerClassTable
          title="Custom ML Per-class Metrics"
          rows={comparison.custom.details.per_class_metrics ?? []}
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg p-4">
          <h4 className="text-sm text-slate-700 dark:text-slate-300 mb-3">AutoML Precision/Recall by Threshold</h4>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={automlThrSeries}>
              <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
              <XAxis dataKey="threshold" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="precision" stroke="#8b5cf6" dot={false} />
              <Line type="monotone" dataKey="recall" stroke="#3b82f6" dot={false} />
              <Line type="monotone" dataKey="coverage" stroke="#10b981" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg p-4">
          <h4 className="text-sm text-slate-700 dark:text-slate-300 mb-3">Custom ML Precision/Recall by Threshold</h4>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={customThrSeries}>
              <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
              <XAxis dataKey="threshold" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="precision" stroke="#8b5cf6" dot={false} />
              <Line type="monotone" dataKey="recall" stroke="#3b82f6" dot={false} />
              <Line type="monotone" dataKey="coverage" stroke="#10b981" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg p-4">
          <h4 className="text-sm text-slate-700 dark:text-slate-300 mb-3">AutoML Precision-Recall Curve (all classes)</h4>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={automlPr}>
              <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
              <XAxis type="number" dataKey="recall" domain={[0, 100]} tickCount={6} allowDecimals={false} />
              <YAxis type="number" dataKey="precision" domain={[0, 100]} tickCount={6} allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="precision" stroke="#3b82f6" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg p-4">
          <h4 className="text-sm text-slate-700 dark:text-slate-300 mb-3">Custom ML Precision-Recall Curve (all classes)</h4>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={customPr}>
              <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
              <XAxis type="number" dataKey="recall" domain={[0, 100]} tickCount={6} allowDecimals={false} />
              <YAxis type="number" dataKey="precision" domain={[0, 100]} tickCount={6} allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="precision" stroke="#10b981" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
