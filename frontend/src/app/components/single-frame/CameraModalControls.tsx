import React from "react";
import { Scan, X } from "lucide-react";
import { Button } from "../ui/button";

type CameraModalControlsProps = {
  disabled: boolean;
  scanning: boolean;
  onCancel: () => void;
  onCapture: () => void;
};

export const CameraModalControls: React.FC<CameraModalControlsProps> = ({
  disabled,
  scanning,
  onCancel,
  onCapture,
}) => {
  return (
    <div className="bg-slate-50 dark:bg-slate-800 px-6 py-4 flex justify-center gap-4">
      <Button
        onClick={onCancel}
        variant="outline"
        className="border-2 border-slate-300 dark:border-slate-600"
      >
        <X className="w-4 h-4 mr-2" />
        Cancel
      </Button>
      <Button
        onClick={onCapture}
        disabled={disabled}
        className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white shadow-lg px-8"
      >
        <Scan className="w-5 h-5 mr-2" />
        {scanning ? "Processing..." : "Capture & Analyze"}
      </Button>
    </div>
  );
};
