import React from "react";
import { Scan, Trash2, X } from "lucide-react";
import { Button } from "../ui/button";

type BatchSelectedFilesProps = {
  files: File[];
  scanning: boolean;
  onRemoveFile: (index: number) => void;
  onClearAll: () => void;
  onScanAll: () => void;
};

export const BatchSelectedFiles: React.FC<BatchSelectedFilesProps> = ({
  files,
  scanning,
  onRemoveFile,
  onClearAll,
  onScanAll,
}) => {
  if (files.length === 0) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-lg text-slate-900 dark:text-white">
          Selected Files ({files.length})
        </h3>
        <Button
          onClick={onClearAll}
          variant="outline"
          size="sm"
          className="text-red-600 dark:text-red-400 border-red-300 dark:border-red-700"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Clear All
        </Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {files.map((file, index) => (
          <div
            key={index}
            className="relative bg-slate-50 dark:bg-slate-800 rounded-lg p-3 border border-slate-200 dark:border-slate-700 group"
          >
            <button
              onClick={() => onRemoveFile(index)}
              className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <X className="w-3 h-3" />
            </button>
            <p className="text-xs text-slate-700 dark:text-slate-300 truncate">
              {file.name}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
        ))}
      </div>

      <Button
        onClick={onScanAll}
        disabled={scanning}
        className="w-full bg-gradient-to-r from-slate-700 to-slate-900 hover:from-slate-800 hover:to-slate-950 text-white shadow-lg hover:shadow-xl"
      >
        {scanning ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
            Processing {files.length} images...
          </>
        ) : (
          <>
            <Scan className="w-4 h-4 mr-2" />
            Scan All Images
          </>
        )}
      </Button>
    </div>
  );
};
