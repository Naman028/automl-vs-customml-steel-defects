/**
 * ============================================
 * BACKEND API ENDPOINTS FOR VERTEX AI INTEGRATION
 * ============================================
 *
 * VERTEX AI AUTOML ENDPOINT:
 * ----------------------------
 * POST https://YOUR_PROJECT_REGION-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_REGION/endpoints/YOUR_AUTOML_ENDPOINT_ID:predict
 *
 * Headers:
 *   Authorization: Bearer YOUR_ACCESS_TOKEN
 *   Content-Type: application/json
 *
 * Request Body:
 * {
 *   "instances": [{
 *     "content": "BASE64_ENCODED_IMAGE_DATA"
 *   }],
 *   "parameters": {
 *     "confidenceThreshold": 0.5,
 *     "maxPredictions": 5
 *   }
 * }
 *
 * Response Format:
 * {
 *   "predictions": [{
 *     "displayNames": ["Crazing", "Inclusion"],
 *     "confidences": [0.92, 0.87],
 *     "ids": ["1", "2"]
 *   }],
 *   "deployedModelId": "YOUR_MODEL_ID",
 *   "model": "projects/YOUR_PROJECT_ID/locations/YOUR_REGION/models/YOUR_MODEL_ID"
 * }
 *
 *
 * CUSTOM ML MODEL ENDPOINT (Cloud Run / Cloud Functions):
 * --------------------------------------------------------
 * POST https://YOUR_CLOUD_RUN_URL/predict
 *
 * Headers:
 *   Authorization: Bearer YOUR_IDENTITY_TOKEN
 *   Content-Type: application/json
 *
 * Request Body:
 * {
 *   "image": "BASE64_ENCODED_IMAGE_DATA",
 *   "model_type": "custom",
 *   "threshold": 0.5
 * }
 *
 * Response Format:
 * {
 *   "predictions": {
 *     "defect_type": "Crazing",
 *     "confidence": 0.94,
 *     "inference_time_ms": 78,
 *     "cost_usd": 0.8,
 *     "bounding_boxes": [],
 *     "metadata": {
 *       "model_version": "v2.1",
 *       "timestamp": "2025-01-02T10:30:00Z"
 *     }
 *   }
 * }
 *
 *
 * INTEGRATION HELPER FUNCTIONS:
 * ------------------------------
 * Replace the mock scanImage function below with these API calls:
 *
 * // AutoML Prediction
 * const automlPredict = async (imageBase64: string) => {
 *   const response = await fetch(
 *     `https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/endpoints/${AUTOML_ENDPOINT}:predict`,
 *     {
 *       method: 'POST',
 *       headers: {
 *         'Authorization': `Bearer ${accessToken}`,
 *         'Content-Type': 'application/json'
 *       },
 *       body: JSON.stringify({
 *         instances: [{ content: imageBase64 }],
 *         parameters: { confidenceThreshold: 0.5, maxPredictions: 5 }
 *       })
 *     }
 *   );
 *   return await response.json();
 * };
 *
 * // Custom ML Prediction
 * const customPredict = async (imageBase64: string) => {
 *   const response = await fetch(
 *     `${CUSTOM_ML_ENDPOINT}/predict`,
 *     {
 *       method: 'POST',
 *       headers: {
 *         'Authorization': `Bearer ${identityToken}`,
 *         'Content-Type': 'application/json'
 *       },
 *       body: JSON.stringify({
 *         image: imageBase64,
 *         model_type: 'custom',
 *         threshold: 0.5
 *       })
 *     }
 *   );
 *   return await response.json();
 * };
 *
 * ============================================
 */

export interface SteelDefect {
  name: string;
  displayName: string;
  description: string;
  severity: "Low" | "Medium" | "High";
  imageUrl: string;
}

export interface PredictionResult {
  model: string;
  defect: string;
  confidence: number;
  time: number;
  cost: number;
  topK?: Array<{ label: string; confidence: number }>;
  inferenceTime?: number;
  memoryUsage?: number;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1Score?: number;
}

export interface MetricComparison {
  metric: string;
  automl: string;
  custom: string;
  winner: "AutoML" | "Custom";
}

export interface HistoricalPrediction {
  id: string;
  timestamp: Date;
  imageName: string;
  imageData?: string; // Add image data for display
  automlDefect: string;
  customDefect: string;
  automlConfidence: number;
  customConfidence: number;
  automlTime?: number;
  customTime?: number;
  automlCost?: number;
  customCost?: number;
  winner: "AutoML" | "Custom" | "Tie";
}

export interface ModelPerformanceMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  avgInferenceTime: number;
  totalPredictions: number;
  avgConfidence: number;
}

export type WinnerType = "automl" | "custom" | "tie" | "none";

export interface ModelMetricsSchema {
  metadata: {
    model_name: string;
    run_id: string;
    timestamp: number;
    dataset_version: string;
    sample_count: number;
    classes: string[];
  };
  core: {
    accuracy: number | null;
    precision: number | null;
    recall: number | null;
    f1: number | null;
    confidence: number | null;
    inference_ms: {
      mean: number | null;
      p50: number | null;
      p95: number | null;
      min: number | null;
      max: number | null;
    };
  };
  ops: {
    training_time: string | number | null;
    model_size_mb: number | null;
    gpu_required: boolean | null;
    setup_complexity: string | null;
    false_positive_rate: number | null;
  };
  explainability: {
    feature_importance: Array<{
      feature: string;
      importance: number;
      description?: string;
    }>;
    focus_areas: string[];
    advantages: string[];
  };
  details: {
    confusion_matrix: number[][];
    y_true?: number[];
    y_pred?: number[];
    probabilities?: number[][];
    per_class_metrics?: Array<{
      class_name: string;
      precision: number;
      recall: number;
      f1: number;
      support: number;
    }>;
    pr_curves?: Record<
      string,
      {
        precision: number[];
        recall: number[];
        thresholds: number[];
      }
    >;
    threshold_metrics?: {
      thresholds: number[];
      precision: number[];
      recall: number[];
      coverage?: number[];
    };
    dataset_counts?: {
      train: number;
      val: number;
      test: number;
      total: number;
    };
  };
}

export interface ComparisonMetricsResponse {
  automl: ModelMetricsSchema;
  custom: ModelMetricsSchema;
  wins: {
    automl: number;
    custom: number;
  };
  per_metric_winners: Record<string, WinnerType>;
  comparison_rows: Array<{
    key: string;
    metric: string;
    automl: string;
    custom: string;
    winner: WinnerType;
  }>;
  summary: {
    winner: WinnerType;
    reason: string;
  };
}

export interface CostAnalysis {
  automl: {
    setupCost: number;
    monthlyInferenceCost: number;
    trainingCost: number;
    totalMonthly: number;
  };
  custom: {
    setupCost: number;
    monthlyInferenceCost: number;
    trainingCost: number;
    totalMonthly: number;
  };
  savings: number;
  savingsPercentage: number;
}

export interface MetalType {
  name: string;
  displayName: string;
  description: string;
  properties: string;
  imageUrl: string;
  color: string;
}

// Mock metal types data
export const metalTypes: MetalType[] = [
  {
    name: "steel",
    displayName: "Steel",
    description: "Iron-carbon alloy",
    properties: "High strength, durable",
    imageUrl: "/metals/steel.jpg",
    color: "from-gray-600 to-gray-800",
  },
  {
    name: "aluminum",
    displayName: "Aluminum",
    description: "Lightweight metal",
    properties: "Corrosion resistant",
    imageUrl: "/metals/aluminium.jpg",
    color: "from-blue-400 to-blue-600",
  },
  {
    name: "copper",
    displayName: "Copper",
    description: "Conductive metal",
    properties: "Excellent conductivity",
    imageUrl: "/metals/copper.jpg",
    color: "from-orange-600 to-red-700",
  },
  {
    name: "titanium",
    displayName: "Titanium",
    description: "High-performance alloy",
    properties: "Strong, lightweight",
    imageUrl: "/metals/titanium.jpg",
    color: "from-purple-600 to-indigo-700",
  },
  {
    name: "brass",
    displayName: "Brass",
    description: "Copper-zinc alloy",
    properties: "Decorative, malleable",
    imageUrl: "/metals/brass.jpg",
    color: "from-yellow-600 to-amber-700",
  },
  {
    name: "stainless_steel",
    displayName: "Stainless Steel",
    description: "Corrosion-resistant steel",
    properties: "Anti-corrosive, hygienic",
    imageUrl: "/metals/Stainless_steel.jpg",
    color: "from-slate-500 to-zinc-700",
  },
  {
    name: "bronze",
    displayName: "Bronze",
    description: "Copper-tin alloy",
    properties: "Wear resistant",
    imageUrl: "/metals/bronze.jpg",
    color: "from-amber-700 to-orange-800",
  },
  {
    name: "nickel",
    displayName: "Nickel",
    description: "Corrosion-resistant",
    properties: "Heat resistant",
    imageUrl: "/metals/nickel.jpg",
    color: "from-emerald-600 to-teal-700",
  },
];

// Mock metal defect data
export const steelDefects: SteelDefect[] = [
  {
    name: "crazing",
    displayName: "Crazing",
    description: "Thermal cracks",
    severity: "Medium",
    imageUrl: "/defects/crazing.jpg",
  },
  {
    name: "inclusion",
    displayName: "Inclusion",
    description: "Foreign particles",
    severity: "High",
    imageUrl: "/defects/inclusion.jpg",
  },
  {
    name: "patches",
    displayName: "Patches",
    description: "Raised surfaces",
    severity: "Medium",
    imageUrl: "/defects/patches.jpg",
  },
  {
    name: "pitted",
    displayName: "Pitted",
    description: "Small holes",
    severity: "High",
    imageUrl: "/defects/pitted.jpg",
  },
  {
    name: "rolled_in_scale",
    displayName: "Rolled-in Scale",
    description: "Scale trapped",
    severity: "Medium",
    imageUrl: "/defects/rolled_in_scale.jpg",
  },
  {
    name: "scratches",
    displayName: "Scratches",
    description: "Surface marks",
    severity: "Low",
    imageUrl: "/defects/scratches.jpg",
  },
];

const BACKEND_URL = "http://localhost:8000";

const isNumberOrNull = (value: unknown): value is number | null =>
  value === null || typeof value === "number";

const validateComparisonMetrics = (payload: unknown): ComparisonMetricsResponse => {
  if (!payload || typeof payload !== "object") {
    throw new Error("Invalid comparison payload: not an object");
  }

  const p = payload as Record<string, any>;
  if (!p.automl || !p.custom || !p.wins || !Array.isArray(p.comparison_rows) || !p.summary) {
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

  const invalidCore = corePaths.some((v) => !isNumberOrNull(v));
  if (invalidCore) {
    throw new Error("Invalid comparison payload: core metric types are incorrect");
  }

  return p as ComparisonMetricsResponse;
};

export const getComparisonMetrics =
  async (): Promise<ComparisonMetricsResponse> => {
    const response = await fetch(`${BACKEND_URL}/compare/metrics`, {
      method: "GET",
      cache: "no-store",
      headers: {
        "Cache-Control": "no-cache",
        Pragma: "no-cache",
      },
    });
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to load comparison metrics: ${response.status} - ${errorText}`);
    }
    const payload = await response.json();
    return validateComparisonMetrics(payload);
  };

// Backend -> UI label mapping
const CLASS_MAP: Record<string, string> = {
  Cr: "Crazing",
  In: "Inclusion",
  Pa: "Patches",
  PS: "Pitted",
  RS: "Rolled-in Scale",
  Sc: "Scratches",
  "No defect / Unknown": "No Defect",
};

type BackendPredictResponse = {
  predicted_class: string;
  confidence: number; // 0..1
  all_probabilities: Record<string, number>;
  top_k?: Array<{ class_name: string; confidence: number }>;
  raw_top_class: string;
  threshold: number;
  inference_time_ms?: number;
};

async function dataUrlToFile(
  dataUrl: string,
  filename = "upload.jpg"
): Promise<File> {
  const res = await fetch(dataUrl);
  const blob = await res.blob();
  return new File([blob], filename, { type: blob.type || "image/jpeg" });
}

// Real API call to backend for image prediction
export const scanImage = async (
  imageData: string,
  modelSelection: "both" | "automl" | "custom" = "both"
): Promise<{
  automl: PredictionResult | null;
  custom: PredictionResult | null;
}> => {
  const file = await dataUrlToFile(imageData, "scan.jpg");
  const formData = new FormData();
  formData.append("file", file);
  
  const url = `${BACKEND_URL}/predict?model_type=${modelSelection}`;
  const response = await fetch(url, { method: "POST", body: formData });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Backend error: ${response.status} - ${errorText}`);
  }
  
  const backendResult = await response.json();
  
  // Handle both models response (AutoML may be null)
  if (backendResult.custom || backendResult.automl) {
    return {
      custom: backendResult.custom
        ? formatPredictionResult(backendResult.custom, "Custom")
        : null,
      automl: backendResult.automl
        ? formatPredictionResult(backendResult.automl, "AutoML")
        : null,
    };
  }

  // Handle single model response (backward compatibility)
  if (modelSelection === "automl") {
    const automlResult = formatPredictionResult(backendResult, "AutoML");
    return {
      custom: null,
      automl: automlResult,
    };
  }
  const customResult = formatPredictionResult(backendResult, "Custom");
  return {
    custom: customResult,
    automl: null,
  };
};

// Helper function to format backend response to frontend format
function formatPredictionResult(
  backendResult: BackendPredictResponse,
  modelName: string
): PredictionResult {
  const displayName = CLASS_MAP[backendResult.predicted_class] || backendResult.predicted_class;
  const confidenceRaw =
    typeof backendResult.confidence === "number" ? backendResult.confidence : 0;
  const confidencePercent = Math.round(confidenceRaw * 100);
  const inferenceTime = backendResult.inference_time_ms || 100;
  const topK = backendResult.top_k?.map((item) => ({
    label: CLASS_MAP[item.class_name] || item.class_name,
    confidence: Math.round(item.confidence * 100),
  }));
  
  return {
    model: modelName,
    defect: displayName,
    confidence: confidencePercent,
    time: Math.round(inferenceTime),
    cost: modelName === "AutoML" ? 3.5 : 0.8,
    inferenceTime: Math.round(inferenceTime),
    memoryUsage: modelName === "AutoML" ? 450 : 120,
    topK,
  };
}

// Get historical predictions (mock data)
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

// Batch processing - calls backend batch endpoint
export const scanBatchImages = async (
  images: string[],
  modelSelection: "both" | "automl" | "custom" = "both",
): Promise<Array<{ automl: PredictionResult | null; custom: PredictionResult | null }>> => {
  try {
    // Convert data URLs to File objects
    const files = await Promise.all(
      images.map((img, idx) => dataUrlToFile(img, `batch_${idx + 1}.jpg`))
    );
    
    // Create FormData for batch upload
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });
    
    // Call backend batch API
    const response = await fetch(
      `${BACKEND_URL}/predict/batch?model_type=${modelSelection}`,
      {
        method: "POST",
        body: formData,
      },
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backend error: ${response.status} - ${errorText}`);
    }
    
    const batchResponse = await response.json();
    
    // Map backend results to frontend format
    return batchResponse.results.map((result: any) => {
      if (result.error) {
        // Return error result
        return {
          automl: null,
          custom: {
            model: "Custom",
            defect: "Error",
            confidence: 0,
            time: 0,
            cost: 0,
            inferenceTime: 0,
            memoryUsage: 0,
          },
        };
      }
      
      if (result.custom || result.automl) {
        return {
          custom: result.custom ? formatPredictionResult(result.custom, "Custom") : null,
          automl: result.automl ? formatPredictionResult(result.automl, "AutoML") : null,
        };
      }

      const displayName =
        CLASS_MAP[result.predicted_class] || result.predicted_class;
      const confidencePercent = Math.round(result.confidence * 100);
      const inferenceTime = result.inference_time_ms || 100;

      if (modelSelection === "automl") {
        return {
          automl: {
            model: "AutoML",
            defect: displayName,
            confidence: confidencePercent,
            time: Math.round(inferenceTime),
            cost: 3.5,
            inferenceTime: Math.round(inferenceTime),
            memoryUsage: 450,
          },
          custom: null,
        };
      }

      return {
        automl: null,
        custom: {
          model: "Custom",
          defect: displayName,
          confidence: confidencePercent,
          time: Math.round(inferenceTime),
          cost: 0.8,
          inferenceTime: Math.round(inferenceTime),
          memoryUsage: 120,
        },
      };
    });
  } catch (error) {
    console.error("Error calling backend batch API:", error);
    // Propagate the error so the UI can show a proper message
    throw error;
  }
};

// Mock metrics comparison data
export const metricsData: MetricComparison[] = [
  { metric: "Accuracy", automl: "91%", custom: "92%", winner: "Custom" },
  { metric: "Precision", automl: "89%", custom: "91%", winner: "Custom" },
  { metric: "Recall", automl: "90%", custom: "90%", winner: "AutoML" },
  { metric: "F1 Score", automl: "89.5%", custom: "90.5%", winner: "Custom" },
  {
    metric: "Inference Time",
    automl: "200ms",
    custom: "80ms",
    winner: "Custom",
  },
  {
    metric: "Training Time",
    automl: "2 hours",
    custom: "6 hours",
    winner: "AutoML",
  },
  { metric: "Model Size", automl: "450MB", custom: "120MB", winner: "Custom" },
  { metric: "GPU Required", automl: "Yes", custom: "No", winner: "Custom" },
  { metric: "False Positives", automl: "8%", custom: "6%", winner: "Custom" },
  {
    metric: "Setup Complexity",
    automl: "Low",
    custom: "Medium",
    winner: "AutoML",
  },
];

// Mock chatbot response for metal identification and defect analysis
export const getChatbotResponse = async (
  defect: string,
  question?: string
): Promise<string> => {
  await new Promise((resolve) => setTimeout(resolve, 800));

  const responses: Record<string, string> = {
    crazing: `🔍 CRAZING ANALYSIS: Medium severity 15-25%
Fine cracks on metal surface caused by thermal stress during cooling.

🛠️ RECOMMENDED FIX:
• Slow cooling rate to 10°C/min
• Adjust quenching temperature
• Use controlled atmosphere furnace

💰 IMPACT: $300-500/ton material loss
⚠️ If untreated: Can lead to complete structural failure

❓ Common Questions:
• "What causes crazing?" → Rapid temperature changes
• "Can it be prevented?" → Yes, with proper cooling protocols
• "Is it repairable?" → Minor cases can be ground and repolished`,

    inclusion: `🔍 INCLUSION ANALYSIS: High severity 20-35%
Foreign particles embedded in metal matrix during production.

🛠️ RECOMMENDED FIX:
• Improve melt cleanliness
• Enhanced ladle refining
• Better slag removal practices

💰 IMPACT: $800-1,200/ton material rejection
⚠️ Risk: Stress concentration points, potential cracking

❓ Common Questions:
• "What are inclusions?" → Non-metallic particles trapped in metal
• "Detection method?" → Ultrasonic testing + visual inspection
• "Prevention?" → Cleaner raw materials + better furnace practices`,

    patches: `🔍 PATCHES ANALYSIS: Medium severity 10-20%
Raised surface irregularities from uneven material distribution.

🛠️ RECOMMENDED FIX:
• Adjust rolling pressure
• Improve temperature uniformity
• Better descaling process

💰 IMPACT: $400-600/ton rework costs
⚠️ Affects: Surface finish quality and coating adhesion

❓ Common Questions:
• "Causes?" → Uneven heating or rolling pressure
• "Rework possible?" → Yes, via grinding and rerolling
• "Quality impact?" → Primarily cosmetic, some structural concern`,

    pitted: `🔍 PITTED SURFACE ANALYSIS: High severity 25-40%
Small holes/cavities from corrosion or manufacturing defects.

🛠️ RECOMMENDED FIX:
• Acid pickling treatment
• Shot peening for minor cases
• Replace severely pitted sections

💰 IMPACT: $1,000-1,500/ton material loss
⚠️ Critical: High corrosion risk, reduced load bearing

❓ Common Questions:
• "Is pitting reversible?" → No, material must be removed
• "Inspection frequency?" → Every batch for critical applications
• "Prevention?" → Proper storage, anti-corrosion coatings`,

    rolled_in_scale: `🔍 ROLLED-IN SCALE ANALYSIS: Medium severity 12-22%
Oxide scale pressed into surface during hot rolling.

🛠️ RECOMMENDED FIX:
• Improved descaling before rolling
• Higher descaling pressure
• Optimize furnace atmosphere

💰 IMPACT: $350-550/ton quality downgrade
⚠️ Issues: Paint adhesion problems, corrosion initiation sites

❓ Common Questions:
• "What is scale?" → Iron oxide formed at high temperatures
• "Removal methods?" → Pickling, shot blasting, grinding
• "Prevention?" → Better descaling equipment + timing`,

    scratches: `🔍 SCRATCHES ANALYSIS: Low severity 5-12%
Surface marks from mechanical contact during handling/processing.

🛠️ RECOMMENDED FIX:
• Improve handling procedures
• Use protective coatings
• Better storage practices
• Polish minor scratches

💰 IMPACT: $200-350/ton cosmetic downgrade
⚠️ Usually cosmetic, rarely structural concern

❓ Common Questions:
• "Acceptable depth?" → <0.5mm for most applications
• "Repair needed?" → Only for high-finish requirements
• "Prevention?" → Careful handling, protective wrapping`,
  };

  const defectKey = defect
    .toLowerCase()
    .replace(/\s+/g, "_")
    .replace(/-/g, "_");
  return responses[defectKey] || responses.crazing;
};

// AI chatbot for metal identification
export const getMetalIdentificationResponse = async (
  question: string
): Promise<string> => {
  await new Promise((resolve) => setTimeout(resolve, 800));

  const lowerQuestion = question.toLowerCase();

  if (lowerQuestion.includes("steel") || lowerQuestion.includes("iron")) {
    return `🔍 STEEL IDENTIFICATION:
Steel is an iron-carbon alloy with 0.2-2% carbon content.

🎯 Key Characteristics:
• Magnetic properties
• High tensile strength
• Gray/silver appearance
• Prone to rust without coating

📊 Common Grades:
• Carbon Steel (1018, 1045)
• Alloy Steel (4140, 4340)
• Tool Steel (O1, D2, A2)

🔬 Testing Methods:
• Magnet test (strongly magnetic)
• Spark test (white/yellow sparks)
• XRF analysis for exact composition`;
  }

  if (
    lowerQuestion.includes("aluminum") ||
    lowerQuestion.includes("aluminium")
  ) {
    return `🔍 ALUMINUM IDENTIFICATION:
Lightweight, silvery-white metal with excellent corrosion resistance.

🎯 Key Characteristics:
• Non-magnetic
• 1/3 weight of steel
• Natural oxide coating
• Soft, malleable

📊 Common Alloys:
• 6061 (structural)
• 7075 (aerospace)
• 2024 (aircraft)

🔬 Testing Methods:
• Magnet test (non-magnetic)
• Density test (2.7 g/cm³)
• Streak test (silver streak)`;
  }

  if (lowerQuestion.includes("copper")) {
    return `🔍 COPPER IDENTIFICATION:
Reddish-brown metal, excellent electrical conductor.

🎯 Key Characteristics:
• Distinctive reddish color
• Non-magnetic
• Highly conductive
• Develops green patina

📊 Common Forms:
• Pure copper (C101, C110)
• Electrical grade
• Oxygen-free copper

🔬 Testing Methods:
• Color (reddish-brown)
• Acid test (green solution)
• Conductivity test`;
  }

  if (lowerQuestion.includes("titanium")) {
    return `🔍 TITANIUM IDENTIFICATION:
Strong, lightweight, corrosion-resistant metal.

🎯 Key Characteristics:
• Silver-gray color
• Low magnetic permeability
• 45% lighter than steel
• Biocompatible

📊 Common Grades:
• Grade 2 (commercial pure)
• Grade 5 (Ti-6Al-4V)
• Grade 9 (Ti-3Al-2.5V)

🔬 Testing Methods:
• Weight comparison
• Spark test (brilliant white)
• XRF analysis`;
  }

  // Default response
  return `🤖 METAL IDENTIFICATION ASSISTANT:

I can help you identify different metals! Try asking about:

🔹 Specific metals: "What is steel?", "Tell me about aluminum"
🔹 Identification: "How to identify copper?", "What color is titanium?"
🔹 Properties: "Is brass magnetic?", "Which metal is strongest?"
🔹 Defects: Ask about specific defect types

💡 Pro tip: Upload an image and I'll analyze the metal surface for defects!`;
};
