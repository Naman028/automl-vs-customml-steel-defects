import React from 'react';
import { Camera } from 'lucide-react';
import { Button } from '../ui/button';

type CameraModalPreviewProps = {
  videoRef: React.RefObject<HTMLVideoElement>;
  error: string | null;
  scanning: boolean;
  onRetry: () => void;
};

export const CameraModalPreview: React.FC<CameraModalPreviewProps> = ({
  videoRef,
  error,
  scanning,
  onRetry,
}) => {
  return (
    <div className="relative bg-slate-950 aspect-video">
      {error ? (
        <div className="w-full h-full flex items-center justify-center p-8">
          <div className="text-center">
            <Camera className="w-16 h-16 text-slate-400 mx-auto mb-4 opacity-50" />
            <p className="text-slate-300 mb-2">{error}</p>
            <Button onClick={onRetry} variant="outline" className="mt-4">
              Try Again
            </Button>
          </div>
        </div>
      ) : (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-contain"
          />
          {scanning && (
            <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 border-4 border-slate-600 border-t-white rounded-full animate-spin mx-auto mb-3"></div>
                <p className="text-white">Processing...</p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
