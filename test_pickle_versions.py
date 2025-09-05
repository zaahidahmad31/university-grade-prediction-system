# test_pickle_versions.py
import pickle
import sys
import json

print(f"Python version: {sys.version}")
print(f"Pickle protocol: {pickle.HIGHEST_PROTOCOL}")

# Test loading just the metadata first
try:
    with open('ml_models/model_metadata.json', 'r') as f:
        metadata = json.load(f)
    print("✅ JSON loads fine")
    print(f"Model info: {metadata}")
except Exception as e:
    print(f"❌ JSON error: {e}")

# Test pickle loading
try:
    with open('ml_models/grade_predictor.pkl', 'rb') as f:
        # Read first few bytes to check file
        f.seek(0)
        header = f.read(10)
        print(f"File header: {header}")
        
        # Try to load
        f.seek(0)
        model = pickle.load(f)
    print("✅ Pickle loads fine")
except Exception as e:
    print(f"❌ Pickle error: {e}")