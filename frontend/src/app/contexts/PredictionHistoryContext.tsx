import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { HistoricalPrediction } from "../services/api";

interface PredictionHistoryContextType {
  history: HistoricalPrediction[];
  addPrediction: (
    prediction: Omit<HistoricalPrediction, "id" | "timestamp">,
  ) => void;
  addBatchPredictions: (
    predictions: Array<Omit<HistoricalPrediction, "id" | "timestamp">>,
  ) => void;
  clearHistory: () => void;
}

const PredictionHistoryContext = createContext<
  PredictionHistoryContextType | undefined
>(undefined);

export const PredictionHistoryProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [history, setHistory] = useState<HistoricalPrediction[]>([]);

  const addPrediction = useCallback(
    (prediction: Omit<HistoricalPrediction, "id" | "timestamp">) => {
      const newPrediction: HistoricalPrediction = {
        ...prediction,
        id: `pred-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date(),
      };

      setHistory((prev) => [newPrediction, ...prev]); // Add to beginning
    },
    [],
  );

  const addBatchPredictions = useCallback(
    (predictions: Array<Omit<HistoricalPrediction, "id" | "timestamp">>) => {
      const newPredictions: HistoricalPrediction[] = predictions.map(
        (prediction, index) => ({
          ...prediction,
          id: `pred-${Date.now()}-${index}-${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date(),
        }),
      );

      setHistory((prev) => [...newPredictions, ...prev]); // Add to beginning
    },
    [],
  );

  const clearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  return (
    <PredictionHistoryContext.Provider
      value={{ history, addPrediction, addBatchPredictions, clearHistory }}
    >
      {children}
    </PredictionHistoryContext.Provider>
  );
};

export const usePredictionHistory = () => {
  const context = useContext(PredictionHistoryContext);
  if (!context) {
    throw new Error(
      "usePredictionHistory must be used within PredictionHistoryProvider",
    );
  }
  return context;
};
