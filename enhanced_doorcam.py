import cv2
from jetson_inference import detectNet
from jetson_utils import videoSource
from pet_trainer import PetDetector
from config import PetConfig

class EnhancedDoorCam:
    def __init__(self):
        # Initialize Jetson inference
        self.net = detectNet("ssd-mobilenet-v2", threshold=0.5)
        self.camera = videoSource("/dev/video0")
        
        # Pet detection system
        self.pet_detector = PetDetector()
        self.config = PetConfig()
        
        # Door state
        self.door_locked = True
        
        # COCO class IDs for common pets
        self.PET_CLASSES = {
            16: "bird",
            17: "cat", 
            18: "dog"
        }
        
        # Distance thresholds based on angle/pose
        self.DISTANCE_THRESHOLDS = {
            'front_facing': {
                'close': 250000,    # Very close - lock door
                'medium': 150000,   # Medium distance - monitor
                'far': 50000        # Far away - safe
            },
            'side_profile': {
                'close': 350000,    # Adjusted for side profile
                'medium': 100000,
                'far': 40000
            },
            'back_facing': {
                'close': 200000,
                'medium': 120000,
                'far': 45000
            },
            'upside_down_front': {
                'close': 220000,
                'medium': 130000,
                'far': 48000
            },
            'upside_down_side': {
                'close': 160000,
                'medium': 95000,
                'far': 38000
            }
        }

    def classify_pet_pose(self, detection, img):
        """Classify the pose/angle of detected pet using basic heuristics"""
        # Extract bounding box
        bbox = (detection.Left, detection.Top, detection.Right, detection.Bottom)
        
        # Calculate aspect ratio
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        aspect_ratio = width / height
        
        # Simple heuristics for pose classification
        # This is a basic implementation - you could use more sophisticated ML models
        if aspect_ratio > 1.5:
            return 'side_profile'
        elif aspect_ratio < 0.8:
            return 'upside_down_front'
        elif bbox[1] > img.height * 0.6:  # Bottom of image
            return 'upside_down_side'
        elif aspect_ratio > 1.2:
            return 'back_facing'
        else:
            return 'front_facing'

    def should_lock_door(self, detection, pose, class_name):
        """Determine if door should be locked based on pet detection"""
        area = detection.Area
        thresholds = self.DISTANCE_THRESHOLDS.get(pose, self.DISTANCE_THRESHOLDS['front_facing'])
        
        # Check if pet is too close
        if area > thresholds['close']:
            print(f"🔒 LOCKING DOOR: {class_name} detected too close ({area} pixels, pose: {pose})")
            return True
        elif area > thresholds['medium']:
            print(f"⚠️ WARNING: {class_name} detected at medium distance ({area} pixels, pose: {pose})")
            return False
        else:
            print(f"✅ SAFE: {class_name} detected far away ({area} pixels, pose: {pose})")
            return False

    def detect_custom_pets(self, img):
        """Detect custom trained pets"""
        custom_detections = self.pet_detector.detect_pets(img)
        return custom_detections

    def run(self):
        """Main detection loop"""
        print("🎥 Starting Enhanced Door Camera System...")
        print("🐕 Pet detection enabled with pose classification")
        print("🔒 Door will lock when pets get too close")
        
        while True:
            img = self.camera.Capture()
            
            if img is None:
                continue
            if not self.camera.IsStreaming():
                break
                
            # Standard Jetson inference detection
            detections = self.net.Detect(img)
            
            # Check for custom trained pets
            custom_pets = self.detect_custom_pets(img)
            
            door_should_lock = False
            
            # Process standard detections
            for detection in detections:
                class_id = detection.ClassID
                class_name = self.net.GetClassDesc(class_id)
                
                # Check if it's a pet
                if class_id in self.PET_CLASSES:
                    pet_type = self.PET_CLASSES[class_id]
                    pose = self.classify_pet_pose(detection, img)
                    
                    print(f"🐾 Detected {pet_type} ({class_name}) - Area: {detection.Area}, Pose: {pose}")
                    
                    if self.should_lock_door(detection, pose, pet_type):
                        door_should_lock = True
                
                # Original person detection logic
                elif class_id == 1 and detection.Area > 300000:
                    print("👤 Person detected - unlocking door")
                    self.door_locked = False
            
            # Process custom pet detections
            for custom_detection in custom_pets:
                pet_name = custom_detection['name']
                confidence = custom_detection['confidence']
                area = custom_detection['area']
                pose = custom_detection['pose']
                
                print(f"🏠 Custom pet detected: {pet_name} (confidence: {confidence:.2f}, area: {area}, pose: {pose})")
                
                if self.should_lock_door_custom(area, pose, pet_name):
                    door_should_lock = True
            
            # Update door state
            if door_should_lock and not self.door_locked:
                print("🔒 LOCKING DOOR due to pet proximity")
                self.door_locked = True
                # TODO: Add actual door locking mechanism here
            
            # Small delay to prevent excessive processing
            cv2.waitKey(1)

    def should_lock_door_custom(self, area, pose, pet_name):
        """Check if door should lock for custom detected pets"""
        thresholds = self.DISTANCE_THRESHOLDS.get(pose, self.DISTANCE_THRESHOLDS['front_facing'])
        
        if area > thresholds['close']:
            print(f"🔒 LOCKING DOOR: {pet_name} detected too close ({area} pixels, pose: {pose})")
            return True
        elif area > thresholds['medium']:
            print(f"⚠️ WARNING: {pet_name} detected at medium distance ({area} pixels, pose: {pose})")
            return False
        else:
            print(f"✅ SAFE: {pet_name} detected far away ({area} pixels, pose: {pose})")
            return False

if __name__ == "__main__":
    door_cam = EnhancedDoorCam()
    try:
        door_cam.run()
    except KeyboardInterrupt:
        print("\n🛑 Door camera system stopped")
