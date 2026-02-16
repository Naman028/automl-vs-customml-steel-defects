import React, { useState } from "react";
import { usePredictionHistory } from "../../contexts/PredictionHistoryContext";
import { HistoricalPrediction } from "../../services/api";
import { HistoryDetailModal } from "./HistoryDetailModal";
import { HistorySummaryStats } from "./HistorySummaryStats";
import { HistoryTable } from "./HistoryTable";
import { HistoryWinRate } from "./HistoryWinRate";

export const HistoricalAnalytics: React.FC = () => {
  const { history } = usePredictionHistory();
  const [selectedPrediction, setSelectedPrediction] =
    useState<HistoricalPrediction | null>(null);

  const automlWins =
    history.length > 0
      ? history.filter((h) => h.winner === "AutoML").length
      : 0;
  const customWins =
    history.length > 0
      ? history.filter((h) => h.winner === "Custom").length
      : 0;
  const ties =
    history.length > 0 ? history.filter((h) => h.winner === "Tie").length : 0;

  const avgAutomlConfidence =
    history.length > 0
      ? history.reduce((sum, h) => sum + h.automlConfidence, 0) / history.length
      : 0;
  const avgCustomConfidence =
    history.length > 0
      ? history.reduce((sum, h) => sum + h.customConfidence, 0) / history.length
      : 0;

  return (
    <div className="space-y-6">
      {selectedPrediction && (
        <HistoryDetailModal
          prediction={selectedPrediction}
          onClose={() => setSelectedPrediction(null)}
        />
      )}

      <HistorySummaryStats
        automlWins={automlWins}
        customWins={customWins}
        avgAutomlConfidence={avgAutomlConfidence}
        avgCustomConfidence={avgCustomConfidence}
        total={history.length}
      />

      <HistoryTable history={history} onSelect={setSelectedPrediction} />

      <HistoryWinRate
        automlWins={automlWins}
        customWins={customWins}
        ties={ties}
        total={history.length}
      />
    </div>
  );
};
