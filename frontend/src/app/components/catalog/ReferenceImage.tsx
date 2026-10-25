import React, { useState } from "react";

type ReferenceImageProps = {
  src: string;
  alt: string;
  className?: string;
};

export function ReferenceImage({ src, alt, className }: ReferenceImageProps) {
  const [failedSource, setFailedSource] = useState<string | null>(null);
  if (failedSource === src) {
    return (
      <div
        role="img"
        aria-label={`${alt} reference image unavailable`}
        className={`${className ?? ""} flex items-center justify-center bg-slate-200 p-6 text-center text-sm text-slate-700 dark:bg-slate-800 dark:text-slate-300`}
      >
        Reference image not bundled
      </div>
    );
  }
  return (
    <img
      src={src}
      alt={alt}
      className={className}
      onError={() => setFailedSource(src)}
    />
  );
}
