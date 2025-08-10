#!/usr/bin/env python3
"""
🎯 Pet Distance Calculator
=========================

Calculates pixel thresholds based on actual pet dimensions and camera setup.
This ensures more accurate distance-based door control.
"""

import math
from typing import Dict

class PetDistanceCalculator:
    """Calculate pixel thresholds based on real pet dimensions"""
    
    def __init__(self, camera_height_ft: float = 8.0, camera_fov_degrees: float = 62.2):
        """
        Initialize the distance calculator
        
        Args:
            camera_height_ft: Height of camera from ground in feet (default: 8ft)
            camera_fov_degrees: Camera field of view in degrees (default: 62.2° for typical webcam)
        """
        self.camera_height_ft = camera_height_ft
        self.camera_fov_rad = math.radians(camera_fov_degrees)
        
        # Standard camera resolution (can be adjusted)
        self.camera_width_px = 1920
        self.camera_height_px = 1080
        
        # Pose multipliers - how much larger/smaller pets appear in different poses
        self.POSE_MULTIPLIERS = {
            'front_facing': 1.0,      # Baseline - pet facing camera directly
            'side_profile': 1.4,      # Side view appears larger
            'back_facing': 0.9,       # Back view slightly smaller than front
            'upside_down_front': 0.8, # Upside down, compressed appearance
            'upside_down_side': 1.2,  # Upside down side, still larger but compressed
            'standing': 1.1           # Standing/sitting, slightly larger profile
        }
        
        # Safety distances in feet (how close is too close)
        self.SAFETY_DISTANCES = {
            'close': 3.0,    # 3 feet - immediate door lock
            'medium': 5.0,   # 5 feet - warning zone  
            'far': 8.0       # 8 feet - safe zone
        }
    
    def inches_to_feet(self, inches: float) -> float:
        """Convert inches to feet"""
        return inches / 12.0
    
    def calculate_pixels_per_foot_at_distance(self, distance_ft: float) -> float:
        """Calculate how many pixels represent one foot at a given distance"""
        # Field of view width at given distance
        fov_width_ft = 2 * distance_ft * math.tan(self.camera_fov_rad / 2)
        
        # Pixels per foot
        pixels_per_foot = self.camera_width_px / fov_width_ft
        return pixels_per_foot
    
    def calculate_pet_pixel_area(self, height_inches: float, length_inches: float, 
                                distance_ft: float, pose: str = 'front_facing') -> float:
        """
        Calculate expected pixel area for a pet at a given distance
        
        Args:
            height_inches: Pet height in inches
            length_inches: Pet length in inches  
            distance_ft: Distance from camera in feet
            pose: Pet pose/orientation
            
        Returns:
            Expected pixel area
        """
        # Convert dimensions to feet
        height_ft = self.inches_to_feet(height_inches)
        length_ft = self.inches_to_feet(length_inches)
        
        # Get pixels per foot at this distance
        pixels_per_foot = self.calculate_pixels_per_foot_at_distance(distance_ft)
        
        # Calculate base pixel dimensions
        height_px = height_ft * pixels_per_foot
        length_px = length_ft * pixels_per_foot
        
        # Apply pose multiplier
        pose_multiplier = self.POSE_MULTIPLIERS.get(pose, 1.0)
        
        # For side profiles, length becomes more prominent
        if 'side' in pose:
            effective_width = length_px * pose_multiplier
            effective_height = height_px
        else:
            # For front/back views, use a more square-like calculation
            effective_width = (length_px * 0.7) * pose_multiplier  # Pets appear narrower from front
            effective_height = height_px * pose_multiplier
        
        # Calculate pixel area
        pixel_area = effective_width * effective_height
        return pixel_area
    
    def calculate_thresholds_for_pet(self, height_inches: float, length_inches: float, 
                                   pet_type: str = 'dog') -> Dict[str, Dict[str, float]]:
        """
        Calculate pixel thresholds for all poses based on pet dimensions
        
        Args:
            height_inches: Pet height in inches
            length_inches: Pet length in inches
            pet_type: Type of pet (affects some calculations)
            
        Returns:
            Dictionary of pose -> distance_type -> pixel_threshold
        """
        thresholds = {}
        
        # Pet type adjustments
        type_multipliers = {
            'dog': 1.0,      # Baseline
            'cat': 0.8,      # Cats are generally more compact
            'bird': 0.6,     # Birds are smaller and more compact
            'other': 1.0     # Default to dog-like
        }
        
        type_multiplier = type_multipliers.get(pet_type.lower(), 1.0)
        
        for pose in self.POSE_MULTIPLIERS.keys():
            thresholds[pose] = {}
            
            for distance_type, distance_ft in self.SAFETY_DISTANCES.items():
                # Calculate pixel area at this distance and pose
                pixel_area = self.calculate_pet_pixel_area(
                    height_inches * type_multiplier, 
                    length_inches * type_multiplier,
                    distance_ft, 
                    pose
                )
                
                # Add some buffer for detection accuracy (±20%)
                pixel_area *= 1.2
                
                thresholds[pose][distance_type] = int(pixel_area)
        
        return thresholds
    
    def get_recommended_thresholds(self, pet_profiles: Dict) -> Dict[str, Dict[str, float]]:
        """
        Get recommended thresholds based on all trained pets
        
        Args:
            pet_profiles: Dictionary of pet profiles with dimensions
            
        Returns:
            Consolidated thresholds considering all pets
        """
        if not pet_profiles:
            # Return default thresholds if no pets trained
            return self.calculate_thresholds_for_pet(24, 30, 'dog')
        
        # Calculate thresholds for each pet
        all_thresholds = []
        for pet_name, profile in pet_profiles.items():
            height = profile.get('height_inches', 24)
            length = profile.get('length_inches', 30)
            pet_type = profile.get('pet_type', 'dog')
            
            pet_thresholds = self.calculate_thresholds_for_pet(height, length, pet_type)
            all_thresholds.append(pet_thresholds)
        
        # Take the maximum threshold for each pose/distance combination
        # (most conservative approach - accommodate the largest pet)
        consolidated = {}
        
        for pose in self.POSE_MULTIPLIERS.keys():
            consolidated[pose] = {}
            for distance_type in self.SAFETY_DISTANCES.keys():
                max_threshold = max(
                    thresholds[pose][distance_type] 
                    for thresholds in all_thresholds
                )
                consolidated[pose][distance_type] = max_threshold
        
        return consolidated
    
    def explain_calculation(self, height_inches: float, length_inches: float, 
                          pose: str, distance_ft: float) -> str:
        """
        Provide a human-readable explanation of the pixel calculation
        
        Returns:
            Explanation string
        """
        pixel_area = self.calculate_pet_pixel_area(height_inches, length_inches, distance_ft, pose)
        pixels_per_foot = self.calculate_pixels_per_foot_at_distance(distance_ft)
        
        explanation = f"""
🧮 Pixel Calculation Breakdown:
Pet Dimensions: {height_inches}" H x {length_inches}" L
Distance: {distance_ft} feet from camera
Pose: {pose.replace('_', ' ').title()}

Camera Setup:
- Camera height: {self.camera_height_ft} feet
- Field of view: {math.degrees(self.camera_fov_rad):.1f}°
- Resolution: {self.camera_width_px}x{self.camera_height_px}

At {distance_ft} feet:
- Pixels per foot: {pixels_per_foot:.1f}
- Pose multiplier: {self.POSE_MULTIPLIERS.get(pose, 1.0)}x
- Expected pixel area: {int(pixel_area)}

This means when your pet is {distance_ft} feet away in {pose.replace('_', ' ')} pose,
they should occupy approximately {int(pixel_area)} pixels in the camera view.
        """
        return explanation.strip()

def main():
    """Demo the pixel calculation system"""
    calculator = PetDistanceCalculator()
    
    print("🎯 Pet Distance Calculator Demo")
    print("=" * 40)
    
    # Example pet dimensions
    test_pets = [
        {"name": "Medium Dog", "height": 24, "length": 30, "type": "dog"},
        {"name": "Large Cat", "height": 12, "length": 20, "type": "cat"},
        {"name": "Small Bird", "height": 8, "length": 10, "type": "bird"}
    ]
    
    for pet in test_pets:
        print(f"\n🐾 {pet['name']} ({pet['height']}\" H x {pet['length']}\" L)")
        thresholds = calculator.calculate_thresholds_for_pet(
            pet['height'], pet['length'], pet['type']
        )
        
        print("Distance Thresholds:")
        for pose, distances in thresholds.items():
            print(f"  📐 {pose.replace('_', ' ').title()}:")
            for dist_type, pixels in distances.items():
                feet = calculator.SAFETY_DISTANCES[dist_type]
                print(f"    {dist_type.title()}: {pixels:,} pixels ({feet}ft)")

if __name__ == "__main__":
    main()
