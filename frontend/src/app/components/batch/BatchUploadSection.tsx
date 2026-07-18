import React from "react";
import { Upload } from "lucide-react";
import { Button } from "../ui/button";

type BatchUploadSectionProps = {
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  onFilesSelected: (files: File[]) => void;
};

export const BatchUploadSection: React.FC<BatchUploadSectionProps> = ({
  fileInputRef,
  onFilesSelected,
}) => {
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      onFilesSelected(files);
    }
  };

  return (
    <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl p-8 text-center hover:border-slate-400 dark:hover:border-slate-600 transition-colors">
      <Upload className="w-16 h-16 mx-auto mb-4 text-slate-400" />
      <h3 className="text-lg text-slate-900 dark:text-white mb-2">
        Upload Images
      </h3>
      <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
        Select multiple images to process in batch
      </p>
      <Button
        onClick={() => fileInputRef.current?.click()}
        className="bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-600"
      >
        <Upload className="w-4 h-4 mr-2" />
        Select Images
      </Button>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  );
};
