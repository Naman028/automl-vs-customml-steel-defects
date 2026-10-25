import React, { useEffect, useState } from "react";
import { getGc10Metrics, Gc10Metrics } from "../services/api/gc10";
import { Gc10PredictionPanel } from "../components/gc10/Gc10PredictionPanel";

const percentage = (value: number) => `${(value * 100).toFixed(1)}%`;
const readableName = (name: string) => name.replaceAll("_", " ");

export function Gc10Results() {
  const [metrics, setMetrics] = useState<Gc10Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    getGc10Metrics(controller.signal)
      .then((response) =>
        setMetrics(response.status === "trained" ? response : null),
      )
      .catch((cause) => {
        if (!controller.signal.aborted) setError(String(cause.message));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, []);

  return (
    <main className="max-w-7xl mx-auto px-4 py-8 space-y-6 text-slate-900 dark:text-slate-100">
      <header>
        <h1 className="text-3xl font-semibold">GC10 local experiment</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Ten defect categories. An image may contain more than one category.
        </p>
      </header>
      <div className="rounded-xl border border-amber-300 bg-amber-50 p-4 text-amber-950 dark:bg-amber-950/30 dark:text-amber-100">
        This experiment has its own dataset and evaluation. Its scores are
        separate from the six-class NEU AutoML comparison. Capture groups are
        inferred from filenames; independent camera generalization is
        unverified.
      </div>
      {error && (
        <p role="alert" className="text-red-600">
          {error}
        </p>
      )}
      {loading && <p>Loading GC10 results…</p>}
      {!loading && !metrics && !error && (
        <p>No trained GC10 results are available yet.</p>
      )}
      {metrics && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ["Macro F1", metrics.test.macro_f1],
              ["Micro F1", metrics.test.micro_f1],
              ["Mean average precision", metrics.test.mean_average_precision],
              ["Exact label-set match", metrics.test.exact_match_accuracy],
            ].map(([title, score]) => (
              <div
                key={String(title)}
                className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5"
              >
                <p className="text-sm text-slate-500">{title}</p>
                <p className="mt-2 text-3xl">{percentage(Number(score))}</p>
              </div>
            ))}
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Train: {metrics.split_counts.train} · Validation:{" "}
            {metrics.split_counts.val} · Test: {metrics.split_counts.test}{" "}
            images. Thresholds selected on validation images only. Exact match
            requires every predicted label to match an image’s annotations.
          </p>
          <section className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 overflow-x-auto">
            <h2 className="text-xl mb-4">Per-class test results</h2>
            <table className="w-full text-left text-sm">
              <thead>
                <tr>
                  {[
                    "Category",
                    "Precision",
                    "Recall",
                    "F1",
                    "Positive images",
                  ].map((title) => (
                    <th key={title} className="p-3">
                      {title}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {metrics.test.per_class.map((row) => (
                  <tr
                    key={row.class_name}
                    className="border-t border-slate-200 dark:border-slate-700"
                  >
                    <td className="p-3 capitalize">
                      {readableName(row.class_name)}
                    </td>
                    <td className="p-3">{percentage(row.precision)}</td>
                    <td className="p-3">{percentage(row.recall)}</td>
                    <td className="p-3">{percentage(row.f1)}</td>
                    <td className="p-3">{row.support}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
          <Gc10PredictionPanel modelAvailable={metrics.model_available} />
          <section className="text-sm text-slate-600 dark:text-slate-400 space-y-2">
            <h2 className="text-lg text-slate-900 dark:text-slate-100">
              Training and data preparation
            </h2>
            <p>
              {metrics.feature_extractor}. Training completed in{" "}
              {(metrics.training_seconds / 60).toFixed(1)} minutes.
            </p>
            <p>
              {metrics.audit.duplicate_copies_removed} duplicate copies removed;{" "}
              {metrics.audit.excluded_annotations.length} annotations excluded.
              Explicit spelling corrections:{" "}
              {Object.entries(metrics.audit.explicit_label_repairs)
                .map(([name, count]) => `${name} (${count})`)
                .join(", ") || "none"}
              .
            </p>
            <p>{metrics.limitation}</p>
          </section>
        </>
      )}
    </main>
  );
}
