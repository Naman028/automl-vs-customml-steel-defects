import React, { useRef, useState } from "react";
import { scanBatchImages } from "../../services/api";
import { usePredictionHistory } from "../../contexts/PredictionHistoryContext";
import {
  createHistoryEntry,
  fileToDataUrl,
} from "../../utils/predictionHelpers";
import { BatchScannerHeader } from "./BatchScannerHeader";
import { BatchUploadSection } from "./BatchUploadSection";
import { BatchSelectedFiles } from "./BatchSelectedFiles";
import { BatchResults } from "./BatchResults";
import { BatchResult } from "./BatchScannerTypes";

export const BatchScanner: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState<BatchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { addBatchPredictions } = usePredictionHistory();

  const handleFilesSelected = (files: File[]) => {
    setSelectedFiles((prev) => [...prev, ...files]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleBatchScan = async () => {
    if (selectedFiles.length === 0) return;

    setScanning(true);
    setError(null);

    try {
      const imageDataArray = await Promise.all(
        selectedFiles.map(fileToDataUrl),
      );
      const predictions = await scanBatchImages(imageDataArray);

      const batchResults: BatchResult[] = selectedFiles.map((file, index) => ({
        fileName: file.name,
        imageData: imageDataArray[index],
        automl: predictions[index].automl ?? null,
        custom: predictions[index].custom ?? null,
      }));

      setResults(batchResults);
      addBatchPredictions(
        selectedFiles.map((file, index) =>
          createHistoryEntry(
            file.name,
            imageDataArray[index],
            predictions[index].automl,
            predictions[index].custom,
          ),
        ),
      );
    } catch (err) {
      console.error("Batch prediction error:", err);
      setError(
        "Failed to get batch predictions. Please ensure the backend is running and reachable, then try again.",
      );
    } finally {
      setScanning(false);
    }
  };

  const clearAll = () => {
    setSelectedFiles([]);
    setResults([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const exportResults = () => {
    const csv = [
      [
        "File Name",
        "AutoML Defect",
        "AutoML Confidence",
        "AutoML Time (ms)",
        "Custom Defect",
        "Custom Confidence",
        "Custom Time (ms)",
        "Winner",
      ],
      ...results.map((r) => [
        r.fileName,
        r.automl ? r.automl.defect : "N/A",
        r.automl ? `${r.automl.confidence}%` : "N/A",
        r.automl ? r.automl.time : "N/A",
        r.custom ? r.custom.defect : "N/A",
        r.custom ? `${r.custom.confidence}%` : "N/A",
        r.custom ? r.custom.time : "N/A",
        r.automl && r.custom
          ? r.custom.confidence > r.automl.confidence
            ? "Custom"
            : r.automl.confidence > r.custom.confidence
              ? "AutoML"
              : "Tie"
          : r.custom
            ? "Custom"
            : r.automl
              ? "AutoML"
              : "N/A",
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `batch_scan_results_${new Date().toISOString()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="relative bg-white dark:bg-slate-900 rounded-2xl shadow-xl overflow-hidden transition-all duration-500 border border-slate-200/50 dark:border-slate-700/50">
      <BatchScannerHeader />

      <div className="p-8 space-y-6">
        <BatchUploadSection
          fileInputRef={fileInputRef}
          onFilesSelected={handleFilesSelected}
        />

        <BatchSelectedFiles
          files={selectedFiles}
          scanning={scanning}
          onRemoveFile={removeFile}
          onClearAll={clearAll}
          onScanAll={handleBatchScan}
        />

        <BatchResults
          results={results}
          error={error}
          onExport={exportResults}
        />
      </div>
    </div>
  );
};
