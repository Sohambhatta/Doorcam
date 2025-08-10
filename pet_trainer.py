import json
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import pickle

class PetDetector:
    """Custom pet detection system using trained data from GUI"""
    
    def __init__(self, data_dir: str = "pet_training_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Load trained pet data
        self.pet_profiles = self.load_pet_profiles()
        
        # Simple feature extractor (you could replace with more sophisticated methods)
        self.feature_extractor = cv2.HOGDescriptor()
        
    def load_pet_profiles(self) -> Dict[str, Dict]:
        """Load all pet profiles from training data"""
        profiles = {}
        profile_file = self.data_dir / "pet_profiles.json"
        
        if profile_file.exists():
            with open(profile_file, 'r') as f:
                profiles = json.load(f)
        
        # Load feature data for each pet
        for pet_name in profiles.keys():
            feature_file = self.data_dir / f"{pet_name}_features.pkl"
            if feature_file.exists():
                with open(feature_file, 'rb') as f:
                    profiles[pet_name]['features'] = pickle.load(f)
        
        return profiles
    
    def extract_features(self, image_region: np.ndarray) -> np.ndarray:
        """Extract HOG features from image region"""
        # Resize to standard size
        resized = cv2.resize(image_region, (128, 128))
        
        # Convert to grayscale if needed
        if len(resized.shape) == 3:
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        else:
            gray = resized
            
        # Extract HOG features
        features = self.feature_extractor.compute(gray)
        return features.flatten() if features is not None else np.array([])
    
    def detect_pets(self, img) -> List[Dict[str, Any]]:
        """Detect custom trained pets in the image"""
        detections = []
        
        if not self.pet_profiles:
            return detections
        
        # Convert jetson image to opencv format if needed
        if hasattr(img, 'height') and hasattr(img, 'width'):
            # Convert from CUDA/Jetson format to numpy
            try:
                cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            except Exception:
                # Fallback - assume it's already in the right format
                cv_image = np.array(img)
        else:
            cv_image = img
        
        # Use sliding window approach (simplified)
        height, width = cv_image.shape[:2]
        window_sizes = [(100, 100), (150, 150), (200, 200), (250, 250)]
        
        for window_size in window_sizes:
            w_width, w_height = window_size
            step_x, step_y = w_width // 3, w_height // 3
            
            for y in range(0, height - w_height, step_y):
                for x in range(0, width - w_width, step_x):
                    window = cv_image[y:y+w_height, x:x+w_width]
                    
                    # Extract features from window
                    features = self.extract_features(window)
                    if len(features) == 0:
                        continue
                    
                    # Compare with each pet profile
                    for pet_name, profile in self.pet_profiles.items():
                        if 'features' not in profile:
                            continue
                        
                        confidence = self.compare_features(features, profile['features'])
                        
                        if confidence > 0.7:  # Threshold for detection
                            # Estimate pose based on training data and window shape
                            pose = self.estimate_pose(window, profile)
                            area = w_width * w_height
                            
                            detection = {
                                'name': pet_name,
                                'confidence': confidence,
                                'bbox': (x, y, x + w_width, y + w_height),
                                'area': area,
                                'pose': pose
                            }
                            detections.append(detection)
        
        # Remove duplicate detections
        detections = self.remove_duplicates(detections)
        return detections
    
    def compare_features(self, features1: np.ndarray, features_list: List[np.ndarray]) -> float:
        """Compare extracted features with trained features"""
        if not features_list:
            return 0.0
        
        similarities = []
        for trained_features in features_list:
            if len(features1) == len(trained_features):
                # Cosine similarity
                dot_product = np.dot(features1, trained_features)
                norm1 = np.linalg.norm(features1)
                norm2 = np.linalg.norm(trained_features)
                
                if norm1 > 0 and norm2 > 0:
                    similarity = dot_product / (norm1 * norm2)
                    similarities.append(similarity)
        
        return max(similarities) if similarities else 0.0
    
    def estimate_pose(self, window: np.ndarray, profile: Dict) -> str:
        """Estimate pet pose based on window dimensions and training data"""
        height, width = window.shape[:2]
        aspect_ratio = width / height
        
        # Use simple heuristics based on aspect ratio
        # This could be improved with more sophisticated ML models
        if aspect_ratio > 1.4:
            return 'side_profile'
        elif aspect_ratio < 0.7:
            return 'upside_down_front'
        elif aspect_ratio > 1.2:
            return 'back_facing'
        else:
            return 'front_facing'
    
    def remove_duplicates(self, detections: List[Dict]) -> List[Dict]:
        """Remove overlapping detections"""
        if not detections:
            return detections
        
        # Sort by confidence
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        filtered = []
        for detection in detections:
            bbox1 = detection['bbox']
            overlap = False
            
            for existing in filtered:
                bbox2 = existing['bbox']
                if self.calculate_overlap(bbox1, bbox2) > 0.3:  # 30% overlap threshold
                    overlap = True
                    break
            
            if not overlap:
                filtered.append(detection)
        
        return filtered
    
    def calculate_overlap(self, bbox1: tuple, bbox2: tuple) -> float:
        """Calculate overlap ratio between two bounding boxes"""
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2
        
        # Calculate intersection
        x_min = max(x1_min, x2_min)
        y_min = max(y1_min, y2_min)
        x_max = min(x1_max, x2_max)
        y_max = min(y1_max, y2_max)
        
        if x_min >= x_max or y_min >= y_max:
            return 0.0
        
        intersection = (x_max - x_min) * (y_max - y_min)
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
