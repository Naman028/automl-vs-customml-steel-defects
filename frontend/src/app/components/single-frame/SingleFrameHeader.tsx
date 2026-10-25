import React from "react";
import { Scan } from "lucide-react";

export const SingleFrameHeader: React.FC = () => {
  return (
    <div className="relative px-8 py-6 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 dark:from-slate-800 dark:via-slate-700 dark:to-slate-800">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div className="relative flex items-center gap-4">
        <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
          <Scan className="w-7 h-7 text-white" />
        </div>
        <div>
          <h2 className="text-2xl text-white tracking-tight">
            Surface Analysis Scanner
          </h2>
          <p className="text-slate-300 text-sm mt-0.5">
            Real-time defect detection with integrated AI assistant
          </p>
        </div>
      </div>
    </div>
  );
};
