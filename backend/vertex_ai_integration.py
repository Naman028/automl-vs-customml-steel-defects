"""
Vertex AI AutoML Integration for Industrial Defect Detection
This module provides integration with Google Cloud Vertex AI AutoML Vision
"""
import os
import base64
from typing import Dict
from google.cloud import aiplatform
from PIL import Image
import io

from label_normalization import automl_to_short_code, normalize_automl_label

# Configuration - Set via environment variables for GCP deployment
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
REGION = os.getenv("GCP_REGION", "us-central1")
AUTOML_ENDPOINT_ID = os.getenv("VERTEX_AI_AUTOML_ENDPOINT_ID", "")

def predict_with_automl(image: Image.Image) -> Dict:
    """
    Predict defect type using Vertex AI AutoML Vision endpoint
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary with prediction results matching the custom model format
    """
    if not PROJECT_ID or not AUTOML_ENDPOINT_ID:
        raise ValueError("Vertex AI configuration not set. Set GCP_PROJECT_ID and VERTEX_AI_AUTOML_ENDPOINT_ID environment variables.")
    
    try:
        # Convert image to base64
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=REGION)
        
        # Get the endpoint
        endpoint = aiplatform.Endpoint(AUTOML_ENDPOINT_ID)
        
        # Prepare prediction request
        instances = [{"content": image_base64}]
        parameters = {
            "confidenceThreshold": 0.5,
            "maxPredictions": 5
        }
        
        # Make prediction
        response = endpoint.predict(instances=instances, parameters=parameters)
        
        # Parse response
        predictions = response.predictions[0] if response.predictions else {}
        
        # Extract top prediction
        if "displayNames" in predictions and len(predictions["displayNames"]) > 0:
            top_class = predictions["displayNames"][0]
            top_confidence = predictions["confidences"][0] if "confidences" in predictions else 0.5
        else:
            top_class = "Unknown"
            top_confidence = 0.0
        
        top_class = normalize_automl_label(top_class)
        raw_class = automl_to_short_code(top_class)

        all_probs: Dict[str, float] = {}
        for i in range(min(len(predictions.get("displayNames", [])), len(predictions.get("confidences", [])))):
            label = normalize_automl_label(predictions["displayNames"][i])
            all_probs[label] = all_probs.get(label, 0.0) + float(predictions["confidences"][i])
        
        return {
            "predicted_class": top_class,
            "confidence": float(top_confidence),
            "all_probabilities": all_probs,
            "raw_top_class": raw_class,
            "threshold": 0.5,
            "inference_time_ms": 0,  # Vertex AI doesn't provide this directly
            "model_type": "automl"
        }
    except Exception as e:
        raise Exception(f"Vertex AI prediction error: {str(e)}")
