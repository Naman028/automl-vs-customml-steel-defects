import React from "react";
import { ReferenceImage } from "./ReferenceImage";
import { steelDefects } from "../../services/api";
import { TriangleAlert, Shield } from "lucide-react";

export const SteelTypes: React.FC = () => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "High":
        return "from-red-500 to-rose-600";
      case "Medium":
        return "from-amber-500 to-orange-600";
      case "Low":
        return "from-emerald-500 to-green-600";
      default:
        return "from-slate-500 to-slate-600";
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case "High":
        return "bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-900/30";
      case "Medium":
        return "bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900/30";
      case "Low":
        return "bg-emerald-50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-900/30";
      default:
        return "bg-slate-50 dark:bg-slate-950/20 border-slate-200 dark:border-slate-900/30";
    }
  };

  return (
    <div className="relative bg-white dark:bg-slate-900 rounded-2xl shadow-xl overflow-hidden transition-all duration-500 border border-slate-200/50 dark:border-slate-700/50">
      {/* Elegant header */}
      <div className="relative px-8 py-6 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 dark:from-slate-800 dark:via-slate-700 dark:to-slate-800">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="relative flex items-center gap-4">
          <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
            <Shield className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-2xl text-white tracking-tight">
              Defect Classification
            </h2>
            <p className="text-slate-300 text-sm mt-0.5">
              AI-powered detection across all metal surfaces
            </p>
          </div>
        </div>
      </div>

      <div className="p-8">
        <div className="relative">
          <div className="flex overflow-x-auto pb-6 gap-6 scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-700">
            {steelDefects.map((defect, index) => (
              <div
                key={defect.name}
                className="flex-shrink-0 w-72 group"
                style={{
                  animation: `fadeInUp 0.6s ease-out ${index * 0.1}s both`,
                }}
              >
                <div className="relative h-full bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 transition-all duration-500 hover:shadow-2xl hover:shadow-slate-900/10 dark:hover:shadow-slate-950/50 hover:-translate-y-2">
                  {/* Image */}
                  <div className="relative h-48 overflow-hidden bg-slate-100 dark:bg-slate-950">
                    <ReferenceImage
                      src={defect.imageUrl}
                      alt={defect.displayName}
                      className="w-full h-full object-cover transition-all duration-700 group-hover:scale-110"
                    />

                    {/* Gradient overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>

                    {/* Severity badge */}
                    <div className="absolute top-3 right-3">
                      <div
                        className={`px-3 py-1.5 rounded-lg bg-gradient-to-r ${getSeverityColor(defect.severity)} backdrop-blur-md border border-white/20 shadow-lg flex items-center gap-1.5`}
                      >
                        <TriangleAlert className="w-3 h-3 text-white" />
                        <span className="text-white text-xs tracking-wider">
                          {defect.severity.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    {/* Title overlay at bottom */}
                    <div className="absolute bottom-0 left-0 right-0 p-4">
                      <h3 className="text-lg text-white tracking-tight drop-shadow-lg">
                        {defect.displayName}
                      </h3>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-5">
                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-4 leading-relaxed">
                      {defect.description}
                    </p>

                    {/* Status indicator */}
                    <div
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${getSeverityBg(defect.severity)}`}
                    >
                      <div
                        className={`w-2 h-2 rounded-full bg-gradient-to-r ${getSeverityColor(defect.severity)} ${defect.severity === "High" ? "animate-pulse" : ""}`}
                      ></div>
                      <span className="text-xs text-slate-700 dark:text-slate-300 tracking-wide">
                        {defect.severity === "High"
                          ? "Critical Alert"
                          : defect.severity === "Medium"
                            ? "Monitor Required"
                            : "Low Priority"}
                      </span>
                    </div>
                  </div>

                  {/* Hover shine */}
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-1000 pointer-events-none">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
