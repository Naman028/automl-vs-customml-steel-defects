import React from 'react';
import { User, ClipboardCheck, Clock, Target } from 'lucide-react';

export const EmployeePanel: React.FC = () => {
  return (
    <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-900 dark:to-slate-950 p-8 rounded-2xl border-2 border-slate-200 dark:border-slate-700 shadow-xl mb-6">
      <div className="flex items-center gap-4 mb-6">
        <div className="p-4 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl shadow-lg">
          <User className="w-8 h-8 text-white" />
        </div>
        <div>
          <h2 className="text-2xl text-slate-900 dark:text-white tracking-tight">Employee Dashboard</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">Your inspection workspace</p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <ClipboardCheck className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">Today's Scans</span>
          </div>
          <div className="text-3xl text-slate-900 dark:text-white">42</div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Target: 50/day</p>
        </div>

        <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">Accuracy</span>
          </div>
          <div className="text-3xl text-slate-900 dark:text-white">95.2%</div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Above target</p>
        </div>

        <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider">Hours Active</span>
          </div>
          <div className="text-3xl text-slate-900 dark:text-white">7.5h</div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">This shift</p>
        </div>
      </div>

      <div className="mt-6 p-4 bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 border border-slate-200 dark:border-slate-700 rounded-xl">
        <p className="text-sm text-slate-700 dark:text-slate-300">
          <strong>👷 Employee Access:</strong> You can perform scans, view results, and access the comparison dashboard. Contact your administrator for additional permissions.
        </p>
      </div>
    </div>
  );
};