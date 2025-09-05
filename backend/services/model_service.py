import pickle
import json
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelService:
    """Service for ML model operations"""
    
    _instance = None
    _model = None
    _scaler = None
    _metadata = None
    
    def __new__(cls):
        """Singleton pattern for model service"""
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the model service"""
        try:
            # Load model
            with open('ml_models/grade_predictor.pkl', 'rb') as f:
                self._model = pickle.load(f)
            logger.info("Model loaded successfully")
            
            # Load scaler
            with open('ml_models/scaler.pkl', 'rb') as f:
                self._scaler = pickle.load(f)
            logger.info("Scaler loaded successfully")
            
            # Load metadata
            with open('ml_models/model_metadata.json', 'r') as f:
                self._metadata = json.load(f)
            logger.info(f"Model metadata loaded: {self._metadata['model_name']}")
            
            # Load feature list
            with open('ml_models/feature_list.json', 'r') as f:
                self._feature_list = json.load(f)
            logger.info(f"Feature list loaded: {len(self._feature_list)} features")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def predict(self, features: np.ndarray) -> Tuple[str, float, str]:
        """
        Make a prediction using the loaded model
        
        Args:
            features: Feature array (1, n_features)
            
        Returns:
            Tuple of (predicted_grade, confidence, risk_level)
        """
        try:
            # Scale features
            features_scaled = self._scaler.transform(features)
            
            # Get prediction and probabilities
            prediction = self._model.predict(features_scaled)[0]
            probabilities = self._model.predict_proba(features_scaled)[0]
            
            # Convert prediction to grade
            grade = self._convert_to_grade(prediction)
            
            # Calculate confidence (max probability)
            confidence = float(max(probabilities))
            
            # Determine risk level
            risk_level = self._calculate_risk_level(prediction, confidence)
            
            return grade, confidence, risk_level
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def batch_predict(self, feature_list: List[np.ndarray]) -> List[Tuple[str, float, str]]:
        """
        Make predictions for multiple students
        
        Args:
            feature_list: List of feature arrays
            
        Returns:
            List of (predicted_grade, confidence, risk_level) tuples
        """
        results = []
        for features in feature_list:
            try:
                result = self.predict(features)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in batch prediction: {str(e)}")
                results.append(('Error', 0.0, 'unknown'))
        
        return results
    
    def _convert_to_grade(self, prediction: int) -> str:
        """Convert numeric prediction to letter grade"""
        # Assuming binary classification (pass/fail)
        # Modify this based on your actual model output
        if prediction == 1:
            return 'Pass'
        else:
            return 'Fail'
    
    def _calculate_risk_level(self, prediction: int, confidence: float) -> str:
        """Calculate risk level based on prediction and confidence"""
        if prediction == 1:  # Pass prediction
            if confidence > 0.8:
                return 'low'
            elif confidence > 0.6:
                return 'medium'
            else:
                return 'high'
        else:  # Fail prediction
            if confidence > 0.8:
                return 'high'
            elif confidence > 0.6:
                return 'medium'
            else:
                return 'medium'  # Less confident fail = still concerning
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            'model_name': self._metadata.get('model_name', 'Unknown'),
            'model_type': self._metadata.get('model_type', 'Unknown'),
            'version': self._metadata.get('export_date', 'Unknown'),
            'feature_count': len(self._feature_list),
            'training_complete': self._metadata.get('training_complete', False),
            'loaded_at': datetime.now().isoformat()
        }
    
    def get_feature_list(self) -> List[str]:
        """Get the list of required features"""
        return self._feature_list
    
    def validate_features(self, features: np.ndarray) -> bool:
        """Validate that features match expected shape"""
        expected_features = len(self._feature_list)
        actual_features = features.shape[1] if len(features.shape) > 1 else features.shape[0]
        
        if actual_features != expected_features:
            logger.error(f"Feature mismatch: expected {expected_features}, got {actual_features}")
            return False
        
        return True
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance scores"""
        try:
            with open('ml_models/feature_importance.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Feature importance file not found")
            return {}
    
    def explain_prediction(self, features: np.ndarray, prediction: str, 
                         confidence: float) -> Dict:
        """
        Provide explanation for a prediction
        
        Args:
            features: Feature values used for prediction
            prediction: The predicted outcome
            confidence: Confidence score
            
        Returns:
            Dictionary with explanation details
        """
        feature_importance = self.get_feature_importance()
        feature_values = features.flatten()
        
        # Get top contributing features
        important_features = []
        for i, (feature_name, value) in enumerate(zip(self._feature_list, feature_values)):
            importance = feature_importance.get(feature_name, 0)
            if importance > 0.05:  # Only include features with >5% importance
                important_features.append({
                    'name': feature_name,
                    'value': float(value),
                    'importance': float(importance),
                    'impact': 'positive' if value > 0 else 'negative'
                })
        
        # Sort by importance
        important_features.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'top_factors': important_features[:5],  # Top 5 factors
            'explanation': self._generate_explanation(prediction, confidence, important_features)
        }
    
    def _generate_explanation(self, prediction: str, confidence: float, 
                            factors: List[Dict]) -> str:
        """Generate human-readable explanation"""
        if prediction == 'Pass':
            if confidence > 0.8:
                explanation = "The model predicts a strong likelihood of passing based on excellent performance indicators."
            else:
                explanation = "The model predicts passing, but some areas need attention."
        else:
            if confidence > 0.8:
                explanation = "The model indicates significant risk of not passing. Immediate intervention recommended."
            else:
                explanation = "The model shows concerns about passing. Additional support may help improve outcomes."
        
        # Add top factor
        if factors:
            top_factor = factors[0]['name'].replace('_', ' ')
            explanation += f" The most influential factor is {top_factor}."
        
        return explanation