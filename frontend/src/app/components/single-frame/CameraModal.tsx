import React, { useCallback, useEffect, useRef, useState } from "react";
import { CameraModalControls } from "./CameraModalControls";
import { CameraModalHeader } from "./CameraModalHeader";
import { CameraModalPreview } from "./CameraModalPreview";

interface CameraModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCapture: (imageData: string) => void;
  scanning?: boolean;
}

export const CameraModal: React.FC<CameraModalProps> = ({
  isOpen,
  onClose,
  onCapture,
  scanning = false,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startCamera = useCallback(async () => {
    setError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "environment",
        },
      });
      streamRef.current = mediaStream;
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play().catch(console.error);
        };
      }
    } catch (err) {
      console.error("Camera access error:", err);
      const errorMessages: Record<string, string> = {
        NotAllowedError:
          "Camera permission denied. Please allow camera access.",
        NotFoundError: "No camera found. Please connect a camera.",
        NotReadableError: "Camera is already in use by another application.",
      };
      const errorMsg =
        err instanceof Error && err.name in errorMessages
          ? errorMessages[err.name]
          : "Unable to access camera.";
      setError(errorMsg);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, []);

  useEffect(() => {
    if (isOpen) void startCamera();
    else stopCamera();
    return stopCamera;
  }, [isOpen, startCamera, stopCamera]);

  const handleCapture = () => {
    if (
      !videoRef.current ||
      !videoRef.current.videoWidth ||
      !videoRef.current.videoHeight
    ) {
      console.error("Video not ready for capture");
      return;
    }
    const canvas = document.createElement("canvas");
    const sourceWidth = videoRef.current.videoWidth;
    const sourceHeight = videoRef.current.videoHeight;
    const cropSize = Math.min(sourceWidth, sourceHeight);
    const cropX = Math.floor((sourceWidth - cropSize) / 2);
    const cropY = Math.floor((sourceHeight - cropSize) / 2);
    canvas.width = cropSize;
    canvas.height = cropSize;
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      console.error("Could not get canvas context");
      return;
    }
    ctx.drawImage(
      videoRef.current,
      cropX,
      cropY,
      cropSize,
      cropSize,
      0,
      0,
      cropSize,
      cropSize,
    );
    const imageData = canvas.toDataURL("image/jpeg", 0.95);
    stopCamera();
    onCapture(imageData);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <CameraModalHeader onClose={onClose} />
        <CameraModalPreview
          videoRef={videoRef}
          error={error}
          scanning={scanning}
          onRetry={startCamera}
        />
        <CameraModalControls
          disabled={!!error || scanning || !stream}
          scanning={scanning}
          onCancel={onClose}
          onCapture={handleCapture}
        />
      </div>
    </div>
  );
};
