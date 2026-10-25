import React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { BarChart as BarIcon, Target } from "lucide-react";
import { ModelPerformanceMetrics } from "../../services/api";

type ModelPerformanceChartsProps = {
  automlMetrics: ModelPerformanceMetrics;
  customMetrics: ModelPerformanceMetrics;
};

export const ModelPerformanceCharts: React.FC<ModelPerformanceChartsProps> = ({
  automlMetrics,
  customMetrics,
}) => {
  const maxInference = Math.max(
    automlMetrics.avgInferenceTime,
    customMetrics.avgInferenceTime,
    1,
  );
  const toSpeedScore = (ms: number) =>
    Math.max(0, 100 - (ms / maxInference) * 100);

  const performanceData = [
    {
      metric: "Accuracy",
      AutoML: automlMetrics.accuracy,
      Custom: customMetrics.accuracy,
    },
    {
      metric: "Precision",
      AutoML: automlMetrics.precision,
      Custom: customMetrics.precision,
    },
    {
      metric: "Recall",
      AutoML: automlMetrics.recall,
      Custom: customMetrics.recall,
    },
    {
      metric: "F1 Score",
      AutoML: automlMetrics.f1Score,
      Custom: customMetrics.f1Score,
    },
  ];

  const radarData = [
    {
      metric: "Accuracy",
      AutoML: automlMetrics.accuracy,
      Custom: customMetrics.accuracy,
      fullMark: 100,
    },
    {
      metric: "Precision",
      AutoML: automlMetrics.precision,
      Custom: customMetrics.precision,
      fullMark: 100,
    },
    {
      metric: "Recall",
      AutoML: automlMetrics.recall,
      Custom: customMetrics.recall,
      fullMark: 100,
    },
    {
      metric: "F1",
      AutoML: automlMetrics.f1Score,
      Custom: customMetrics.f1Score,
      fullMark: 100,
    },
    {
      metric: "Speed",
      AutoML: toSpeedScore(automlMetrics.avgInferenceTime),
      Custom: toSpeedScore(customMetrics.avgInferenceTime),
      fullMark: 100,
    },
  ];

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg">
        <h3 className="text-lg text-slate-900 dark:text-white mb-4 flex items-center gap-2">
          <BarIcon className="w-5 h-5" />
          Performance Metrics Comparison
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="metric" stroke="#64748b" />
            <YAxis domain={[0, 100]} stroke="#64748b" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #475569",
                borderRadius: "8px",
                color: "#fff",
              }}
            />
            <Legend />
            <Bar dataKey="AutoML" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            <Bar dataKey="Custom" fill="#10b981" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border-2 border-slate-200 dark:border-slate-700 shadow-lg">
        <h3 className="text-lg text-slate-900 dark:text-white mb-4 flex items-center gap-2">
          <Target className="w-5 h-5" />
          Overall Performance Profile
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="metric" stroke="#64748b" />
            <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#64748b" />
            <Radar
              name="AutoML"
              dataKey="AutoML"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
            />
            <Radar
              name="Custom"
              dataKey="Custom"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.3}
            />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
