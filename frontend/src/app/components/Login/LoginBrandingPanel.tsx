import React from "react";

export const LoginBrandingPanel: React.FC = () => {
  return (
    <div className="hidden md:flex flex-col justify-center text-white p-12 bg-gradient-to-br from-slate-800 via-slate-900 to-slate-950 dark:from-slate-900 dark:via-slate-950 dark:to-black rounded-2xl shadow-2xl border border-slate-700/50">
      <div className="mb-8">
        <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mb-6 border border-white/20">
          <span className="text-4xl"></span>
        </div>
        <h1 className="text-5xl mb-4 tracking-tight">METAL DEFECT AI</h1>
        <p className="text-xl opacity-90 mb-8 text-slate-300">
          Advanced Multi-Metal Defect Detection System
        </p>
      </div>
      <div className="space-y-3 text-sm opacity-90 mb-8">
        <p className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
          Real-time metal surface scanning
        </p>
        <p className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
          8+ metal type identification
        </p>
        <p className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-white"></span>6 defect
          type classifications
        </p>
        <p className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
          AutoML vs Custom model comparison
        </p>
        <p className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
          Integrated AI assistant chatbot
        </p>
      </div>
      <div className="p-4 bg-white/10 rounded-xl backdrop-blur-sm border border-white/10">
        <p className="text-xs opacity-75">Powered by Google Cloud Vertex AI</p>
      </div>
    </div>
  );
};
