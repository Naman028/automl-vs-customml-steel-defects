import { BACKEND_URL } from "./constants";
import { ComparisonMetricsResponse } from "./types";

const isNumberOrNull = (value: unknown): value is number | null =>
  value === null || typeof value === "number";

const validateComparisonMetrics = (
  payload: unknown
): ComparisonMetricsResponse => {
  if (!payload || typeof payload !== "object") {
    throw new Error("Invalid comparison payload: not an object");
  }

  const p = payload as Record<string, any>;
  if (
    !p.automl ||
    !p.custom ||
    !p.wins ||
    !Array.isArray(p.comparison_rows) ||
    !p.summary
  ) {
    throw new Error("Invalid comparison payload: missing top-level fields");
  }

  const corePaths = [
    p.automl?.core?.accuracy,
    p.automl?.core?.precision,
    p.automl?.core?.recall,
    p.automl?.core?.f1,
    p.automl?.core?.confidence,
    p.automl?.core?.inference_ms?.mean,
    p.custom?.core?.accuracy,
    p.custom?.core?.precision,
    p.custom?.core?.recall,
    p.custom?.core?.f1,
    p.custom?.core?.confidence,
    p.custom?.core?.inference_ms?.mean,
  ];

  if (corePaths.some((v) => !isNumberOrNull(v))) {
    throw new Error("Invalid comparison payload: core metric types are incorrect");
  }

  return p as ComparisonMetricsResponse;
};

export const getComparisonMetrics =
  async (signal?: AbortSignal): Promise<ComparisonMetricsResponse> => {
    const response = await fetch(`${BACKEND_URL}/compare/metrics`, {
      method: "GET",
      signal,
      cache: "no-store",
      headers: {
        "Cache-Control": "no-cache",
        Pragma: "no-cache",
      },
    });
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Failed to load comparison metrics: ${response.status} - ${errorText}`
      );
    }
    return validateComparisonMetrics(await response.json());
  };
