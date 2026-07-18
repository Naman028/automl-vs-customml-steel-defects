import React, { useRef, useState } from "react";
import {
  PredictionResult,
  askAssistant,
  scanImage,
} from "../../services/api";
import { usePredictionHistory } from "../../contexts/PredictionHistoryContext";
import { createHistoryEntry } from "../../utils/predictionHelpers";
import { CameraModal } from "./CameraModal";
import { SingleFrameHeader } from "./SingleFrameHeader";
import { SingleFrameImagePanel } from "./SingleFrameImagePanel";
import { SingleFrameResultsPanel } from "./SingleFrameResultsPanel";
import { SingleFrameAssistant } from "./SingleFrameAssistant";
import { SingleFrameErrorBanner } from "./SingleFrameErrorBanner";

const DEFECT_QUESTIONS = [
  "What causes this defect?",
  "How can it be prevented?",
  "How serious is this defect?",
  "What should operator check first?",
  "What immediate corrective action is recommended?",
  "How to confirm this in lab?",
  "Is this acceptable or should it be rejected?",
];
const METAL_QUESTIONS = [
  "What are the 6 steel surface defects?",
  "How to detect Rolled-in Scale?",
  "How to identify Pitted Surface?",
  "How to prevent Inclusion defects?",
  "What causes Crazing in steel?",
  "How can scratches be prevented?",
  "How to identify copper?",
];

export const SingleFrameScanner: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [cameraModalOpen, setCameraModalOpen] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [predictions, setPredictions] = useState<{
    automl: PredictionResult | null;
    custom: PredictionResult | null;
  } | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [predictionError, setPredictionError] = useState<string | null>(null);
  const [modelSelection, setModelSelection] = useState<
    "both" | "automl" | "custom"
  >("both");
  const { addPrediction } = usePredictionHistory();
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatResponse, setChatResponse] = useState<string>("");
  const [chatLoading, setChatLoading] = useState(false);

  const processPrediction = async (imageData: string, imageName: string) => {
    setScanning(true);
    setPredictionError(null);
    setCapturedImage(imageData);

    try {
      const results = await scanImage(imageData, modelSelection);
      setPredictions(results);
      if (results.custom || results.automl) {
        addPrediction(
          createHistoryEntry(
            imageName,
            imageData,
            results.automl,
            results.custom,
          ),
        );
      }
    } catch (error) {
      console.error("Prediction error:", error);
      setPredictionError(
        "Failed to get prediction from backend. Please ensure the backend server is running on http://localhost:8001 and try again.",
      );
    } finally {
      setScanning(false);
    }
  };

  const handleCameraCapture = async (imageData: string) => {
    const imageName = `camera_${Date.now()}.jpg`;
    await processPrediction(imageData, imageName);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (event) => {
      await processPrediction(event.target?.result as string, file.name);
    };
    reader.readAsDataURL(file);
  };

  const resetScan = () => {
    setPredictions(null);
    setCapturedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleAskAI = async () => {
    if (!chatQuestion.trim()) return;
    setChatLoading(true);
    try {
      const selectedPrediction = predictions?.custom || predictions?.automl;
      const response = await askAssistant(chatQuestion, selectedPrediction);
      setChatResponse(response.answer);
    } catch (error) {
      console.error("Assistant error:", error);
      setChatResponse(
        "Assistant backend request failed. Ensure backend is running and try again.",
      );
    } finally {
      setChatLoading(false);
    }
  };

  const quickQuestions = predictions ? DEFECT_QUESTIONS : METAL_QUESTIONS;

  return (
    <div className="relative bg-white dark:bg-slate-900 rounded-2xl shadow-xl overflow-hidden transition-all duration-500 border border-slate-200/50 dark:border-slate-700/50">
      <SingleFrameHeader />

      <div className="p-8">
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          <SingleFrameImagePanel
            capturedImage={capturedImage}
            scanning={scanning}
            modelSelection={modelSelection}
            fileInputRef={fileInputRef}
            onReset={resetScan}
            onCameraOpen={() => setCameraModalOpen(true)}
            onFileUpload={handleFileUpload}
            onModelChange={setModelSelection}
          />

          <SingleFrameResultsPanel predictions={predictions} />
        </div>

        <SingleFrameAssistant
          hasPredictions={!!predictions}
          chatQuestion={chatQuestion}
          chatResponse={chatResponse}
          chatLoading={chatLoading}
          quickQuestions={quickQuestions}
          onQuestionChange={setChatQuestion}
          onAsk={handleAskAI}
          onQuickQuestion={setChatQuestion}
        />

        <SingleFrameErrorBanner
          error={predictionError}
          onDismiss={() => setPredictionError(null)}
        />
      </div>

      <CameraModal
        isOpen={cameraModalOpen}
        onClose={() => setCameraModalOpen(false)}
        onCapture={handleCameraCapture}
        scanning={scanning}
      />
    </div>
  );
};
