import React from "react";
import { metalTypes } from "../../services/api";
import { MetalTypesHeader } from "./MetalTypesHeader";
import { MetalTypesCarousel } from "./MetalTypesCarousel";

export const MetalTypes: React.FC = () => {
  return (
    <div className="relative bg-white dark:bg-slate-900 rounded-2xl shadow-xl overflow-hidden transition-all duration-500 border border-slate-200/50 dark:border-slate-700/50">
      <MetalTypesHeader />

      <div className="p-8">
        <MetalTypesCarousel items={metalTypes} />
      </div>
    </div>
  );
};
