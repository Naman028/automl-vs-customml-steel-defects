import React from "react";
import { Camera, Upload, X } from "lucide-react";
import { Button } from "../ui/button";

const MODEL_CONFIG = {
  both: { label: "Both Models", colors: "from-slate-700 to-slate-900" },
  automl: { label: "AutoML Only", colors: "from-blue-600 to-blue-700" },
  custom: { label: "Custom Only", colors: "from-green-600 to-green-700" },
} as const;

type ModelSelection = keyof typeof MODEL_CONFIG;

type SingleFrameImagePanelProps = {
  capturedImage: string | null;
  scanning: boolean;
  modelSelection: ModelSelection;
  fileInputRef: React.RefObject<HTMLInputElement>;
  onReset: () => void;
  onCameraOpen: () => void;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onModelChange: (value: ModelSelection) => void;
};

export const SingleFrameImagePanel: React.FC<SingleFrameImagePanelProps> = ({
  capturedImage,
  scanning,
  modelSelection,
  fileInputRef,
  onReset,
  onCameraOpen,
  onFileUpload,
  onModelChange,
}) => {
  return (
    <div className="space-y-4 max-w-[560px] mx-auto lg:mx-0 h-full">
      <div
        className={`relative bg-slate-950 rounded-xl overflow-hidden border-2 border-slate-200 dark:border-slate-700 ${
          capturedImage
            ? "aspect-square lg:aspect-auto lg:h-full"
            : "aspect-square max-h-[560px]"
        }`}
      >
        {capturedImage ? (
          <>
            <img
              src={capturedImage}
              alt="Captured"
              className="w-full h-full object-cover"
            />
            <button
              onClick={onReset}
              className="absolute top-3 right-3 p-2.5 bg-red-500 hover:bg-red-600 rounded-lg text-white transition-all hover:scale-110 shadow-lg z-10"
            >
              <X className="w-4 h-4" />
            </button>
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-500">
            <div className="text-center">
              <Camera className="w-20 h-20 mx-auto mb-3 opacity-30" />
              <p className="text-sm text-slate-400">Image Preview</p>
            </div>
          </div>
        )}
        {scanning && (
          <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-20">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-slate-600 border-t-white rounded-full animate-spin mx-auto mb-3"></div>
              <p className="text-white">Analyzing...</p>
            </div>
          </div>
        )}
      </div>

      {!capturedImage && (
        <div className="space-y-3">
          <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900 p-4 rounded-xl border-2 border-slate-200 dark:border-slate-700">
            <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-3">
              Model Selection
            </p>
            <div className="grid grid-cols-3 gap-2">
              {(["both", "automl", "custom"] as const).map((value) => {
                const config = MODEL_CONFIG[value];
                return (
                  <button
                    key={value}
                    onClick={() => onModelChange(value)}
                    className={`py-2.5 px-3 rounded-lg text-xs transition-all ${
                      modelSelection === value
                        ? `bg-gradient-to-r ${config.colors} text-white shadow-lg scale-105`
                        : "bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700"
                    }`}
                  >
                    {config.label}
                  </button>
                );
              })}
            </div>
          </div>
          <Button
            onClick={onCameraOpen}
            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg py-3 text-base font-semibold"
          >
            <Camera className="w-5 h-5 mr-2" />
            Open Camera
          </Button>
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-slate-300 dark:border-slate-700" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white dark:bg-slate-900 px-3 text-slate-500">
                Or
              </span>
            </div>
          </div>
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
            className="w-full border-2 border-slate-300 dark:border-slate-600"
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload Image
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={onFileUpload}
            className="hidden"
          />
        </div>
      )}
    </div>
  );
};
