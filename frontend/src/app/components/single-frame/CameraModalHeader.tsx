import React from 'react';
import { Camera, X } from 'lucide-react';

type CameraModalHeaderProps = {
  onClose: () => void;
};

export const CameraModalHeader: React.FC<CameraModalHeaderProps> = ({ onClose }) => {
  return (
    <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 dark:from-slate-800 dark:via-slate-700 dark:to-slate-800 px-6 py-4 flex justify-between items-center">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-white/10 backdrop-blur-sm rounded-lg">
          <Camera className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg text-white font-semibold">Camera Capture</h3>
          <p className="text-xs text-slate-300">Position your object and click capture</p>
        </div>
      </div>
      <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
        <X className="w-5 h-5 text-white" />
      </button>
    </div>
  );
};
