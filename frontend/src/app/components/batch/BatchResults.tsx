import React from "react";
import { Download } from "lucide-react";
import { Button } from "../ui/button";
import { BatchResult } from "./BatchScannerTypes";
import { BatchResultCard } from "./BatchResultCard";

type BatchResultsProps = {
  results: BatchResult[];
  error: string | null;
  onExport: () => void;
};

export const BatchResults: React.FC<BatchResultsProps> = ({
  results,
  error,
  onExport,
}) => {
  if (results.length === 0) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg text-slate-900 dark:text-white">
          Batch Results ({results.length})
        </h3>
        <Button
          onClick={onExport}
          variant="outline"
          size="sm"
          className="border-2 border-slate-300 dark:border-slate-600"
        >
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-950/20 border-2 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 p-4 rounded-xl">
          {error}
        </div>
      )}

      <div className="grid gap-4">
        {results.map((result, index) => (
          <BatchResultCard
            key={`${result.fileName}-${index}`}
            result={result}
            index={index}
          />
        ))}
      </div>
    </div>
  );
};
