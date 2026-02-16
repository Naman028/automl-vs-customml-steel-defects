import React from "react";
import { getCostAnalysis } from "../../services/api";
import { CostCharts } from "./CostCharts";
import { CostRoiAnalysis } from "./CostRoiAnalysis";
import { CostSummaryCards } from "./CostSummaryCards";

export const CostAnalysis: React.FC = () => {
  const costData = getCostAnalysis();

  return (
    <div className="space-y-6">
      <CostSummaryCards costData={costData} />
      <CostCharts costData={costData} />
      <CostRoiAnalysis costData={costData} />
    </div>
  );
};
