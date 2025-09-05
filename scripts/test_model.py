# Save this as test_model.py and run it to check your model

import pickle
import json
import numpy as np

def test_model():
    """Test the model to understand its output format"""
    
    print("Testing ML Model...")
    print("="*60)
    
    # Load model
    try:
        with open('ml_models/grade_predictor.pkl', 'rb') as f:
            model = pickle.load(f)
        print("✓ Model loaded successfully")
        print(f"  Model type: {type(model).__name__}")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return
    
    # Load scaler
    try:
        with open('ml_models/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        print("✓ Scaler loaded successfully")
    except Exception as e:
        print(f"✗ Error loading scaler: {e}")
        return
    
    # Load feature list
    try:
        with open('ml_models/feature_list.json', 'r') as f:
            feature_list = json.load(f)
        print(f"✓ Feature list loaded: {len(feature_list)} features")
    except Exception as e:
        print(f"✗ Error loading feature list: {e}")
        return
    
    # Check model classes
    if hasattr(model, 'classes_'):
        print(f"\nModel Classes: {model.classes_}")
        print(f"Number of classes: {len(model.classes_)}")
    
    # Create test data
    print("\nTesting with sample data...")
    
    # Test 1: All zeros (worst case)
    test_features_zeros = np.zeros((1, len(feature_list)))
    scaled_zeros = scaler.transform(test_features_zeros)
    pred_zeros = model.predict(scaled_zeros)[0]
    prob_zeros = model.predict_proba(scaled_zeros)[0]
    print(f"\nTest 1 - All zeros:")
    print(f"  Prediction: {pred_zeros}")
    print(f"  Probabilities: {prob_zeros}")
    
    # Test 2: Random normal data
    np.random.seed(42)
    test_features_normal = np.random.randn(1, len(feature_list))
    scaled_normal = scaler.transform(test_features_normal)
    pred_normal = model.predict(scaled_normal)[0]
    prob_normal = model.predict_proba(scaled_normal)[0]
    print(f"\nTest 2 - Random normal data:")
    print(f"  Prediction: {pred_normal}")
    print(f"  Probabilities: {prob_normal}")
    
    # Test 3: High values (best case)
    test_features_high = np.ones((1, len(feature_list))) * 100
    scaled_high = scaler.transform(test_features_high)
    pred_high = model.predict(scaled_high)[0]
    prob_high = model.predict_proba(scaled_high)[0]
    print(f"\nTest 3 - High values:")
    print(f"  Prediction: {pred_high}")
    print(f"  Probabilities: {prob_high}")
    
    # Check if it's binary classification
    print("\nModel Analysis:")
    if hasattr(model, 'classes_') and len(model.classes_) == 2:
        print("✓ This appears to be a binary classification model")
        print(f"  Classes: {model.classes_}")
        print("  Likely Pass/Fail prediction")
    else:
        print("✓ This appears to be a multi-class classification model")
    
    # Print feature importance if available
    if hasattr(model, 'feature_importances_'):
        print(f"\nTop 10 Important Features:")
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:10]
        for i, idx in enumerate(indices):
            print(f"  {i+1}. {feature_list[idx]}: {importances[idx]:.4f}")

if __name__ == "__main__":
    test_model()