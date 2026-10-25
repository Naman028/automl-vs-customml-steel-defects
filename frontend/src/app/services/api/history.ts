import { steelDefects } from "./constants";
import { HistoricalPrediction } from "./types";

export const getHistoricalPredictions = (): HistoricalPrediction[] => {
  const history: HistoricalPrediction[] = [];
  const defects = steelDefects.map((d) => d.displayName);

  for (let i = 0; i < 15; i++) {
    const automlConf = 85 + Math.random() * 12;
    const customConf = 87 + Math.random() * 11;
    const defect = defects[Math.floor(Math.random() * defects.length)];

    history.push({
      id: `pred-${i + 1}`,
      timestamp: new Date(Date.now() - i * 3600000),
      imageName: `sample_${i + 1}.jpg`,
      automlDefect: defect,
      customDefect: defect,
      automlConfidence: Math.round(automlConf * 10) / 10,
      customConfidence: Math.round(customConf * 10) / 10,
      winner:
        automlConf > customConf
          ? "AutoML"
          : customConf > automlConf
            ? "Custom"
            : "Tie",
    });
  }

  return history;
};
