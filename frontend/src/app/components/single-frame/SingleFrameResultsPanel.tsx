import React from "react";
import { Scan } from "lucide-react";
import { PredictionResult } from "../../services/api";
import { PredictionTable } from "../shared-generalUi/PredictionTable";

type SingleFrameResultsPanelProps = {
  predictions: {
    automl: PredictionResult | null;
    custom: PredictionResult | null;
  } | null;
};

export const SingleFrameResultsPanel: React.FC<
  SingleFrameResultsPanelProps
> = ({ predictions }) => {
  if (predictions) {
    return <PredictionTable predictions={predictions} />;
  }

  return (
    <div className="h-full flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-900/50 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700">
      <div className="text-center text-slate-500 dark:text-slate-400 p-8">
        <Scan className="w-20 h-20 mx-auto mb-4 opacity-30" />
        <p className="text-lg mb-2 text-slate-700 dark:text-slate-300">
          No analysis yet
        </p>
        <p className="text-sm">Capture or upload an image</p>
      </div>
    </div>
  );
};
