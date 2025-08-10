# 🐾 Doorcam Pet Detection System

> An advanced AI-powered door security system with intelligent pet detection, dimension-based calculations, and dual motor control

## 🌟 Key Features

### 🤖 **Smart Dual Motor Control**
- **Synchronized Operation**: Two motors work together - one pulls while the other loosens
- **String Management**: Prevents string tangling with coordinated motor speeds
- **Safety First**: Emergency stop and error handling built-in

### 🔬 **Dimension-Based Pet Detection**
- **Real Pet Measurements**: Enter your pet's actual height and length in inches
- **Scientific Calculations**: Converts real dimensions to pixel thresholds at 8ft distance
- **Pose-Aware Multipliers**: Side profiles get 1.4x larger thresholds (because they appear bigger)
- **Pet Type Adjustments**: Different calculations for dogs, cats, birds

### 🧠 **Intelligent Door Logic**
- **Person + No Pets = OPEN**: Door opens only when person detected AND no pets too close
- **Pet Too Close = IMMEDIATE CLOSE**: Door closes instantly when pets get dangerously close
- **Safety Priority**: Pet safety overrides person access

### 🎨 **Enhanced Training GUI**
- **Pet Dimensions Input**: Enter height/length in inches during training
- **Pet Type Selection**: Choose dog, cat, bird, or other
- **Real-time Calculations**: See your pet's calculated thresholds instantly

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python install.py
```

### 2. Train Your Pet with Dimensions
```bash
python launcher.py train
```
**Important**: Enter your pet's real dimensions:
- **Height**: How tall when standing (inches)
- **Length**: From nose to tail (inches) 
- **Type**: Dog, cat, bird, or other

### 3. Run the Smart Door System
```bash
python launcher.py run
```

## 📏 **How Dimension-Based Detection Works**

### Real-World Measurements Matter!
Instead of guessing pixel sizes, we calculate them based on:

1. **Your Pet's Actual Size** (height × length in inches)
2. **Camera Position** (8 feet high, 62° field of view)
3. **Safety Distances** (3ft=close, 5ft=medium, 8ft=far)
4. **Pose Multipliers** (side view appears larger)

### Pose-Specific Multipliers
- **Front Facing**: 1.0x (baseline)
- **Side Profile**: 1.4x (appears much larger) 
- **Back Facing**: 0.9x (slightly smaller)
- **Standing**: 1.1x (taller profile)
- **Upside Down**: 0.8-1.2x (compressed appearance)

### Example Calculation
**Medium Dog (24" tall × 30" long)**:
- At 3 feet: ~1.2M pixels (CLOSE - door locks)
- At 5 feet: ~425K pixels (MEDIUM - warning)
- At 8 feet: ~166K pixels (FAR - safe)

**Side Profile gets 1.4x larger thresholds** because dogs appear wider from the side!

## 🔧 **Dual Motor System**

### How It Works
```
OPENING SEQUENCE:
🔧 Motor 1 (Opener): PULLS string to open door (75% speed)
🔧 Motor 2 (Closer): LOOSENS string to prevent tension (80% speed)

CLOSING SEQUENCE:  
🔧 Motor 2 (Closer): PULLS string to close door (70% speed)
🔧 Motor 1 (Opener): LOOSENS string to prevent tension (80% speed)
```

### Motor Wiring (when ready for hardware)
```python
# GPIO Pin Configuration
motor1_pins = [18, 19]  # Opening motor direction
motor2_pins = [20, 21]  # Closing motor direction  
enable_pins = [12, 13]  # PWM speed control
```

## 🎯 **Smart Door Logic**

### Opening Conditions (ALL must be true)
✅ Person detected (class_id=1, area > 300k pixels)  
✅ NO pets detected too close  
✅ Door currently closed

### Closing Conditions (ANY can trigger)
🐾 Pet detected too close (based on dimensions + pose)  
🐾 Custom trained pet too close

### Safety Features
- **2-second delay** between door actions (prevents rapid cycling)
- **Emergency stop** capability
- **Error state handling**
- **Pet safety overrides** person access

## 📊 **System Components**

### Core Files
- **`enhanced_doorcam.py`** - Main system with smart door logic
- **`pet_training_gui.py`** - GUI for training pets with dimensions
- **`pet_distance_calculator.py`** - Dimension-to-pixel calculations
- **`motor_controller.py`** - Dual motor control system
- **`pet_trainer.py`** - Custom pet detection
- **`launcher.py`** - Unified system launcher

### Utilities
- **`demo.py`** - Demonstration without hardware
- **`install.py`** - Dependency installer
- **`config_manager.py`** - Settings GUI
- **`config.py`** - Configuration management

## 📱 **Updated Training Process**

### Step-by-Step with Dimensions

1. **Launch Training GUI**
   ```bash
   python launcher.py train
   ```

2. **Enter Pet Information**
   - **Name**: Your pet's name
   - **Height**: Standing height in inches (e.g., 24")  
   - **Length**: Nose to tail in inches (e.g., 30")
   - **Type**: Dog, cat, bird, or other

3. **Select Pose & Capture**
   - Choose current pose (front, side, back, etc.)
   - Capture multiple photos from that angle
   - System automatically calculates thresholds

4. **Save Training Data** 
   - Click "Save Training Data"
   - System stores dimensions and calculates pixel thresholds
   - Ready for detection!

## 🧮 **Calculation Examples**

### Small Cat (12" H × 20" L)
- **Front Facing Close**: 252K pixels (3ft)
- **Side Profile Close**: 504K pixels (3ft) - Notice 2x larger!
- **Safe Distance**: 35K pixels (8ft)

### Large Dog (28" H × 36" L) 
- **Front Facing Close**: 1.6M pixels (3ft)
- **Side Profile Close**: 3.2M pixels (3ft) - Much larger detection area!
- **Safe Distance**: 230K pixels (8ft)

## 🎮 **Testing Without Hardware**

```bash
# Test distance calculations
python pet_distance_calculator.py

# Test motor control (simulation)
python motor_controller.py  

# Test complete system (simulation)  
python demo.py

# Check system status
python launcher.py status
```

## 🔍 **Troubleshooting**

### Motor Issues
- Check GPIO wiring (pins 18,19,20,21,12,13)
- Verify power supply for motors
- Test in simulation mode first: `motor_controller.py`

### Distance Detection Issues
- Verify pet dimensions are accurate (measure your pet!)
- Check camera height (default: 8 feet)
- Test calculations: `python pet_distance_calculator.py`

### Door Logic Issues  
- Check thresholds: `python launcher.py status`
- Verify person detection area > 300k pixels
- Ensure pets aren't blocking person detection

---

*🐾 Built with ❤️ for pet safety and smart home security*  
*🔬 Now with scientific dimension-based detection!*
