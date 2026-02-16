import React from 'react';
import { AlertCircle, X } from 'lucide-react';

type SingleFrameErrorBannerProps = {
  error: string | null;
  onDismiss: () => void;
};

export const SingleFrameErrorBanner: React.FC<SingleFrameErrorBannerProps> = ({
  error,
  onDismiss,
}) => {
  if (!error) return null;

  return (
    <div className="mt-4 bg-red-50 dark:bg-red-950/20 border-2 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 p-4 rounded-xl flex items-start gap-3">
      <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="text-sm leading-relaxed">{error}</p>
      </div>
      <button
        onClick={onDismiss}
        className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
