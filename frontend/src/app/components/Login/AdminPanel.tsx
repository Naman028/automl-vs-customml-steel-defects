import React from "react";
import {
  Shield,
  Users,
  Settings,
  Database,
  Download,
  Activity,
  TrendingUp,
  AlertCircle,
} from "lucide-react";
import { metricsData } from "../../services/api";
import { Button } from "../ui/button";

export const AdminPanel: React.FC = () => {
  const exportAllData = () => {
    const csv = [
      ["Metric", "AutoML", "Custom ML", "Winner"],
      ...metricsData.map((m) => [m.metric, m.automl, m.custom, m.winner]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `admin_full_report_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-900 dark:to-slate-950 p-8 rounded-2xl border-2 border-slate-200 dark:border-slate-700 shadow-xl mb-6">
      <div className="flex items-center gap-4 mb-6">
        <div className="p-4 bg-gradient-to-br from-red-600 to-red-700 rounded-xl shadow-lg">
          <Shield className="w-8 h-8 text-white" />
        </div>
        <div>
          <h2 className="text-2xl text-slate-900 dark:text-white tracking-tight">
            Administrator Control Panel
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Full system access and advanced controls
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Active Users
            </span>
          </div>
          <div className="text-3xl text-slate-900 dark:text-white">247</div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            +23 this month
          </p>
        </div>

        <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Scans Today
            </span>
          </div>
          <div className="text-3xl text-slate-900 dark:text-white">1,247</div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            +15% vs yesterday
          </p>
        </div>

        <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Accuracy Rate
            </span>
          </div>
          <div className="text-3xl text-slate-900 dark:text-white">92.4%</div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Custom ML model
          </p>
        </div>

        <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              System Status
            </span>
          </div>
          <div className="text-xl text-slate-900 dark:text-white">
            Operational
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            99.9% uptime
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <Button
          onClick={exportAllData}
          className="bg-gradient-to-r from-slate-700 to-slate-900 hover:from-slate-800 hover:to-slate-950 text-white shadow-lg hover:shadow-xl"
        >
          <Download className="w-4 h-4 mr-2" />
          Export Full System Report
        </Button>

        <Button
          variant="outline"
          className="border-2 border-slate-300 dark:border-slate-600"
        >
          <Database className="w-4 h-4 mr-2" />
          Database Backup
        </Button>

        <Button
          variant="outline"
          className="border-2 border-slate-300 dark:border-slate-600"
        >
          <Settings className="w-4 h-4 mr-2" />
          System Settings
        </Button>
      </div>

      <div className="mt-6 p-4 bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-950/20 dark:to-orange-950/20 border-2 border-red-200 dark:border-red-800 rounded-xl">
        <p className="text-sm text-red-800 dark:text-red-200">
          <strong>🔒 Administrator Privileges Active:</strong> You have full
          access to all system features, data exports, user management, and
          configuration settings.
        </p>
      </div>
    </div>
  );
};
