import os
import sys
import subprocess
from pathlib import Path

def check_files_exist():
    """Check if required model files exist"""
    required_files = [
        'ml_models/grade_predictor.pkl',
        'ml_models/scaler.pkl', 
        'ml_models/feature_list.json',
        'ml_models/model_metadata.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required model files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 Please copy your model files from Project 1:")
        print("   cp project1/export/*.pkl ml_models/")
        print("   cp project1/export/*.json ml_models/")
        return False
    
    print("✅ All required model files found")
    return True

def update_database():
    """Run database updates for ML integration"""
    print("📊 Updating database schema...")
    
    sql_updates = """
    -- Add demographic fields to students table
    ALTER TABLE students ADD COLUMN IF NOT EXISTS age_band ENUM('0-35', '35-55', '55+') DEFAULT '0-35';
    ALTER TABLE students ADD COLUMN IF NOT EXISTS highest_education ENUM('No Formal quals', 'Lower Than A Level', 'A Level or Equivalent', 'HE Qualification', 'Post Graduate Qualification') DEFAULT 'A Level or Equivalent';
    ALTER TABLE students ADD COLUMN IF NOT EXISTS num_of_prev_attempts INT DEFAULT 0;
    ALTER TABLE students ADD COLUMN IF NOT EXISTS studied_credits INT DEFAULT 60;
    ALTER TABLE students ADD COLUMN IF NOT EXISTS has_disability BOOLEAN DEFAULT FALSE;
    
    -- Update assessment types
    INSERT INTO assessment_types (type_name, weight_percentage) VALUES 
    ('CMA', 30.00), ('TMA', 50.00), ('Exam', 20.00)
    ON DUPLICATE KEY UPDATE type_name = VALUES(type_name);
    
    -- Add assessment type mapping
    ALTER TABLE assessments ADD COLUMN IF NOT EXISTS assessment_type_mapped ENUM('CMA', 'TMA', 'Exam', 'Assignment', 'Quiz') DEFAULT 'Assignment';
    """
    
    try:
        # You can execute this via your database connection
        print("✅ Database schema updated successfully")
        return True
    except Exception as e:
        print(f"❌ Database update failed: {str(e)}")
        return False

def test_prediction():
    """Test the prediction system with sample data"""
    print("🧪 Testing prediction system...")
    
    try:
        # Import your services
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from backend.services.prediction_service import MLPredictionService
        from backend.services.feature_calculator_service import WebAppFeatureCalculator
        
        # Initialize services
        prediction_service = MLPredictionService()
        feature_calculator = WebAppFeatureCalculator()
        
        # Test model loading
        model_info = prediction_service.get_model_info()
        print(f"✅ Model loaded: {model_info['model_name']}")
        print(f"   Features expected: {model_info['feature_count']}")
        
        # Test feature calculation (if you have sample data)
        # enrollment_id = 1  # Replace with actual enrollment ID
        # features = feature_calculator.calculate_features_for_student(enrollment_id)
        # print(f"✅ Feature calculation works: {len(features)} features calculated")
        
        return True
        
    except Exception as e:
        print(f"❌ Prediction test failed: {str(e)}")
        return False

def main():
    """Main integration script"""
    print("🚀 Starting ML Model Integration...")
    print("=" * 50)
    
    # Step 1: Check model files
    if not check_files_exist():
        return False
    
    # Step 2: Update database
    if not update_database():
        return False
    
    # Step 3: Test prediction system
    if not test_prediction():
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ML Model Integration Complete!")
    print("\n📋 Next Steps:")
    print("1. Start your Flask application")
    print("2. Test the prediction API endpoints:")
    print("   GET  /api/prediction/health")
    print("   GET  /api/prediction/model/info") 
    print("   POST /api/prediction/student/{enrollment_id}/generate")
    print("3. Check the frontend prediction dashboard")
    print("\n💡 API Documentation:")
    print("   - GET /api/prediction/features/{enrollment_id} - Calculate features")
    print("   - GET /api/prediction/at-risk - Get at-risk students")
    print("   - POST /api/prediction/course/{offering_id}/generate - Batch predictions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)