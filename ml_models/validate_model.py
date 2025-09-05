#!/usr/bin/env python
"""
Simple validation script to check if the exported model works.
Run this to ensure the model was saved correctly.
"""

import sys
import json
import joblib
import numpy as np
from pathlib import Path

def validate_model():
    """Validate the exported model package"""
    print("Validating exported model...")
    
    # Check all required files exist
    required_files = [
        "grade_predictor.pkl",
        "scaler.pkl",
        "feature_list.json",
        "model_metadata.json"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"ERROR: Required file missing: {file}")
            return False
        else:
            print(f"[OK] Found: {file}")
    
    # Load components
    try:
        model = joblib.load("grade_predictor.pkl")
        print("[OK] Model loaded successfully")
        
        scaler = joblib.load("scaler.pkl")
        print("[OK] Scaler loaded successfully")
        
        with open("feature_list.json", 'r') as f:
            feature_order = json.load(f)
        print(f"[OK] Feature list loaded: {len(feature_order)} features")
        
        # Test with random data
        test_features = np.random.rand(1, len(feature_order))
        scaled_features = scaler.transform(test_features)
        prediction = model.predict(scaled_features)
        print(f"[OK] Test prediction successful: {prediction[0]}")
        
    except Exception as e:
        print(f"ERROR during validation: {e}")
        return False
    
    print("\nValidation completed successfully!")
    print("Model is ready for future web application integration.")
    return True

if __name__ == "__main__":
    success = validate_model()
    sys.exit(0 if success else 1)