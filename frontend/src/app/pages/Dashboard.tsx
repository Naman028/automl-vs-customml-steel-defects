import React from "react";
import { SteelTypes } from "../components/catalog/SteelTypes";
import { MetalTypes } from "../components/catalog/MetalTypes";
import { SingleFrameScanner } from "../components/single-frame/SingleFrameScanner";
import { BatchScanner } from "../components/batch/BatchScanner";

export const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 transition-colors duration-300">
      {/* Decorative background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-slate-200/30 dark:bg-slate-700/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-slate-200/30 dark:bg-slate-700/10 rounded-full blur-3xl"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Metal Types Showcase */}
        <MetalTypes />

        {/* Defect Types Showcase */}
        <SteelTypes />

        {/* Single Frame Scanner with AI */}
        <SingleFrameScanner />

        {/* Batch Processing */}
        <BatchScanner />
      </div>
    </div>
  );
};
