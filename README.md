# 🐾 Doorcam Pet Detection System

> An advanced AI-powered door security system with intelligent pet detection and pose classification

## 🌟 Features

### 🔒 Smart Door Control
- **Person Detection**: Automatically unlocks door when authorized persons are detected
- **Pet Safety**: Locks door when pets get too close based on their size and pose
- **Distance-based Logic**: Different thresholds for different pet poses (front, side, back, upside down)

### 🐾 Advanced Pet Detection
- **Jetson Inference Integration**: Uses pre-trained models for cats, dogs, and birds
- **Custom Pet Training**: Train the system to recognize your specific pets
- **Pose Classification**: Detects pet orientation (front-facing, side profile, etc.)
- **Size-based Distance Estimation**: Larger detected area = closer proximity

### 🎨 Modern Training GUI
- **Beautiful Interface**: Modern dark theme with customtkinter
- **Live Camera Feed**: Real-time camera preview for training
- **Multi-angle Training**: Capture photos from different poses
- **Progress Tracking**: Visual feedback on training data collected
- **Pet Management**: Add, view, and delete trained pets

### ⚙️ Configuration Management
- **Adjustable Thresholds**: Fine-tune detection sensitivity
- **Pose-specific Settings**: Different distance limits for each pose
- **Camera Settings**: Configure device, resolution, FPS
- **Easy-to-use GUI**: Modern interface for all settings

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train Your Pet (First Time)
```bash
python launcher.py train
```
- Enter your pet's name
- Select the current pose/angle
- Start camera and capture photos from different angles
- Save training data when done

### 3. Run the Door Camera System
```bash
python launcher.py run
```

### 4. Adjust Settings (Optional)
```bash
python launcher.py config
```

## 📋 System Components

### Core Files
- **`enhanced_doorcam.py`** - Main detection system with pet intelligence
- **`pet_training_gui.py`** - Modern GUI for collecting training data  
- **`pet_trainer.py`** - Custom pet detection using trained data
- **`config.py`** - Configuration management system
- **`config_manager.py`** - GUI for adjusting settings
- **`launcher.py`** - Unified launcher for all components

### Legacy
- **`doorcam.py`** - Original implementation (basic person detection)

## 🎯 How Pet Detection Works

### Distance Thresholds by Pose

| Pose Type | Close (Lock) | Medium (Warn) | Far (Safe) |
|-----------|--------------|---------------|------------|
| Front Facing | 250,000 px | 150,000 px | 50,000 px |
| Side Profile | 180,000 px | 100,000 px | 40,000 px |
| Back Facing | 200,000 px | 120,000 px | 45,000 px |
| Upside Down Front | 220,000 px | 130,000 px | 48,000 px |
| Upside Down Side | 160,000 px | 95,000 px | 38,000 px |

### Detection Logic
1. **Jetson Inference** detects standard pets (cats, dogs, birds)
2. **Custom Detector** identifies your specific trained pets
3. **Pose Classification** determines pet orientation
4. **Distance Calculation** estimates proximity based on detected area
5. **Action Decision** locks door if pet is too close for safety

## 🔧 Configuration

### Distance Thresholds
Adjust when the door should lock based on pet proximity:
- **Close**: Door locks immediately
- **Medium**: Warning issued, monitoring continues  
- **Far**: Pet is safe distance, no action needed

### Detection Settings
- **Confidence Threshold**: Minimum confidence for pet detection (0.0-1.0)
- **Overlap Threshold**: Maximum overlap between detections (0.0-1.0)

### Camera Settings
- **Device**: Camera device path (e.g., `/dev/video0` or `0`)
- **Resolution**: Video capture resolution
- **FPS**: Frames per second for detection

## 📱 Using the Training GUI

### Step-by-Step Training Process

1. **Launch Training GUI**
   ```bash
   python launcher.py train
   ```

2. **Enter Pet Information**
   - Type your pet's name (e.g., "Buddy", "Whiskers")
   - This name will be used for detection

3. **Select Current Pose**
   - Choose from 6 different pose options
   - Each pose has different distance thresholds

4. **Capture Training Photos**
   - Start the camera feed
   - Position your pet in the selected pose
   - Click "Capture Photo" to save the image
   - Repeat for multiple angles and poses

5. **Save Training Data**
   - Click "Save Training Data" when done
   - System will process images and extract features
   - Your pet will now be detected by the door camera

### Pose Types Explained

- **🐕 Front Facing**: Pet looking directly at camera
- **🦮 Side Profile**: Pet's side view (appears larger)
- **🐕‍🦺 Back Facing**: Pet looking away from camera  
- **🙃 Upside Down Front**: Pet upside down, facing camera
- **🔄 Upside Down Side**: Pet upside down, side view
- **🐕 Standing/Sitting**: Pet in normal standing/sitting position

## 🛠️ Advanced Usage

### Command Line Options
```bash
python launcher.py [command]

Commands:
  train    - Launch Pet Training GUI
  run      - Start Enhanced Door Camera
  config   - Open Configuration Manager
  status   - Show system status
  help     - Show help message
```

### Direct Component Access
```bash
# Run components directly
python enhanced_doorcam.py      # Main detection system
python pet_training_gui.py      # Training GUI only
python config_manager.py        # Settings GUI only
```

### System Status Check
```bash
python launcher.py status
```
Shows:
- Number of trained pets
- Configuration status
- Camera availability
- System health

## 🎨 GUI Themes

The system uses a modern dark theme with:
- **Dark Mode**: Easy on the eyes for long training sessions
- **Blue Accent**: Professional and calming color scheme
- **Responsive Layout**: Adapts to different screen sizes
- **Intuitive Icons**: Clear visual indicators for all actions

## 🔍 Troubleshooting

### Camera Issues
- Ensure camera is connected and not in use by other applications
- Try different camera device numbers (0, 1, 2, etc.)
- Check camera permissions on your system

### Detection Issues  
- Ensure good lighting for training photos
- Capture photos from multiple angles for each pose
- Use consistent backgrounds during training
- Adjust confidence thresholds if needed

### Performance Issues
- Reduce camera resolution if system is slow
- Lower FPS for better processing time
- Ensure adequate GPU memory for Jetson inference

## 📊 System Requirements

### Hardware
- **Camera**: USB or built-in camera
- **GPU**: NVIDIA Jetson device (Nano, TX2, Xavier, etc.) recommended, raspberry pi models are okay too!
- **RAM**: Minimum 4GB, 8GB recommended
- **Storage**: 2GB free space for training data

### Software
- **Python**: 3.6 or higher
- **OpenCV**: 4.5.0+
- **Jetson Inference**: 1.4.0+
- **CustomTkinter**: 5.0.0+

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

Just a fun project... No licencing!

## 🆘 Support

Need help? 
- Check this README for common issues
- Run `python launcher.py status` to check system health
- Review the configuration in `pet_config.json`
- Ensure all dependencies are installed with `pip install -r requirements.txt`

## 🏛️ Original Project Background

This project started as a simple door recognition system using Jetson Inference. The original goal was to create a door that opens when it recognizes a person, helping to prevent pets from entering restricted rooms and reducing door slamming from air currents.

Using the Jetson Inference library (https://github.com/dusty-nv/jetson-inference), the system detects objects in real-time camera feeds. The enhanced version now includes sophisticated pet detection, pose classification, and distance-based safety measures.

---

*🐾 Built with ❤️ for pet safety and smart home security*
```python
from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput

net = detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = videoSource("/dev/video0")      # '/dev/video0' for V4L2
door_locked = True
while True:
    img = camera.Capture()
    
    if img is None: # capture timeout
        continue
    if not camera.IsStreaming():
        break
    detections = net.Detect(img)
    
    for detection in detections:
        print(detection.ClassID)
        print(net.GetClassDesc(detection.ClassID))
        print(detection.Area)
        if detection.ClassID == 1 and detection.Area > 300000 and door_locked:
            print("unlocking door") # This is where the unlocking and locking actually happens.
            door_locked = False
```
Now, lets break down code. THe code starts off with importing all the necassary libraries for it to run. We imported detectNet and videoSource, and videoOutput. Then we defined a few variables to help us out in the while loop. the "net" variable helps us define detections, and holds the libraries. The "camera" variable is how we define the input, and the "door_locked" prevents the code from opening the door every frame that it sees a person. 
```python
from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput

net = detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = videoSource("/dev/video0")      # '/dev/video0' for V4L2
door_locked = True
```
Now, we have the main loop. The while loop starts off by defining img as the input from the camera per frame. Then we made sure that even is the camera isnt detecting anything, keep running. THen we said that if the camera is not streaming, then stop. Then, we defined detections with the help of "net", and "img".
``` python
while True:
    img = camera.Capture()
    
    if img is None: # capture timeout
        continue
    if not camera.IsStreaming():
        break
    detections = net.Detect(img)

```
Next, we made a for loop inside the mainloop that defines detection in detections, so that we can define individual classes. In order the debug the code, we made the first 3 print statements. They display the classID, and its description, and the Area of the frame that its detected on. Then we made the for loop that is supposed to open and close the door. Since we don't have live motors present, and the extra camera, this camera is capable of unlocking the door, once. This is where I made sure that the area is big enough so that the camera doesn't recognis random movement. Then we made it so that it only open ths door once  using the boolean variable "door_locked".
```python
for detection in detections:
        print(detection.ClassID)
        print(net.GetClassDesc(detection.ClassID))
        print(detection.Area)
        if detection.ClassID == 1 and detection.Area > 300000 and door_locked:
            print("unlocking door") # This is where the unlocking and locking actually happens.
            door_locked = False
```
## Running the program 
1) Start by ssh remote connecting to your nano on vs code.
2) Then have your camera plugged into your nano.
3) Copy the full code above.
4) Paste it into a .py file, and run it. Make sure you are in the right directory.
5) The code is incomplete, allowing you to use it and have it connect to whatever motor you have, and have the freedom to use it for any purpose.
6) Have the camera mounted, and you are good to go!
7) You can also watch this vdeo tutorial! https://youtu.be/JdIJrjob7OY !
   
