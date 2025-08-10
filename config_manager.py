#!/usr/bin/env python3
"""
Configuration Manager for Doorcam Pet Detection System
=====================================================

A simple GUI for managing detection thresholds and system settings.
"""

import customtkinter as ctk
from pathlib import Path
from config import PetConfig
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ConfigManagerGUI:
    """GUI for managing system configuration"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("⚙️ Doorcam Configuration Manager")
        self.root.geometry("800x600")
        
        self.config = PetConfig()
        self.pose_vars = {}
        self.distance_vars = {}
        
        self.setup_gui()
        self.load_current_settings()
        
    def setup_gui(self):
        """Setup the configuration GUI"""
        # Title
        title_label = ctk.CTkLabel(
            self.root, 
            text="⚙️ System Configuration", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollable frame for settings
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Distance Thresholds Section
        self.create_distance_threshold_section()
        
        # Detection Settings Section
        self.create_detection_settings_section()
        
        # Camera Settings Section
        self.create_camera_settings_section()
        
        # Control buttons
        self.create_control_buttons()
        
    def create_distance_threshold_section(self):
        """Create distance threshold configuration section"""
        # Section title
        distance_title = ctk.CTkLabel(
            self.scroll_frame,
            text="📏 Distance Thresholds (pixels)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        distance_title.pack(pady=(0, 15), anchor="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Adjust when the door should lock based on pet proximity and pose",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc_label.pack(anchor="w", pady=(0, 20))
        
        # Distance threshold controls
        poses = [
            ("Front Facing", "front_facing"),
            ("Side Profile", "side_profile"),
            ("Back Facing", "back_facing"),
            ("Upside Down Front", "upside_down_front"),
            ("Upside Down Side", "upside_down_side")
        ]
        
        distance_types = [
            ("Close (Lock door)", "close"),
            ("Medium (Warning)", "medium"),
            ("Far (Safe)", "far")
        ]
        
        for pose_name, pose_key in poses:
            # Pose frame
            pose_frame = ctk.CTkFrame(self.scroll_frame)
            pose_frame.pack(fill="x", pady=(0, 15))
            
            # Pose title
            pose_title = ctk.CTkLabel(
                pose_frame,
                text=f"📐 {pose_name}",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            pose_title.pack(pady=(10, 5), anchor="w", padx=15)
            
            # Distance controls
            controls_frame = ctk.CTkFrame(pose_frame)
            controls_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            self.distance_vars[pose_key] = {}
            
            for i, (distance_name, distance_key) in enumerate(distance_types):
                control_frame = ctk.CTkFrame(controls_frame)
                control_frame.pack(fill="x", pady=2)
                
                # Label
                label = ctk.CTkLabel(
                    control_frame,
                    text=distance_name,
                    width=150
                )
                label.pack(side="left", padx=10, pady=5)
                
                # Entry
                var = ctk.StringVar()
                entry = ctk.CTkEntry(
                    control_frame,
                    textvariable=var,
                    width=100,
                    placeholder_text="pixels"
                )
                entry.pack(side="left", padx=10, pady=5)
                
                self.distance_vars[pose_key][distance_key] = var
    
    def create_detection_settings_section(self):
        """Create detection settings section"""
        # Section title
        detection_title = ctk.CTkLabel(
            self.scroll_frame,
            text="🎯 Detection Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        detection_title.pack(pady=(20, 15), anchor="w")
        
        # Settings frame
        settings_frame = ctk.CTkFrame(self.scroll_frame)
        settings_frame.pack(fill="x", pady=(0, 15))
        
        # Confidence threshold
        conf_frame = ctk.CTkFrame(settings_frame)
        conf_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        conf_label = ctk.CTkLabel(conf_frame, text="🎯 Confidence Threshold:", width=200)
        conf_label.pack(side="left", padx=10, pady=10)
        
        self.confidence_var = ctk.StringVar()
        conf_entry = ctk.CTkEntry(conf_frame, textvariable=self.confidence_var, width=100, placeholder_text="0.7")
        conf_entry.pack(side="left", padx=10, pady=10)
        
        # Overlap threshold
        overlap_frame = ctk.CTkFrame(settings_frame)
        overlap_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        overlap_label = ctk.CTkLabel(overlap_frame, text="📊 Overlap Threshold:", width=200)
        overlap_label.pack(side="left", padx=10, pady=10)
        
        self.overlap_var = ctk.StringVar()
        overlap_entry = ctk.CTkEntry(overlap_frame, textvariable=self.overlap_var, width=100, placeholder_text="0.3")
        overlap_entry.pack(side="left", padx=10, pady=10)
    
    def create_camera_settings_section(self):
        """Create camera settings section"""
        # Section title
        camera_title = ctk.CTkLabel(
            self.scroll_frame,
            text="📹 Camera Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        camera_title.pack(pady=(20, 15), anchor="w")
        
        # Settings frame
        camera_frame = ctk.CTkFrame(self.scroll_frame)
        camera_frame.pack(fill="x", pady=(0, 15))
        
        # Camera device
        device_frame = ctk.CTkFrame(camera_frame)
        device_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        device_label = ctk.CTkLabel(device_frame, text="📹 Camera Device:", width=200)
        device_label.pack(side="left", padx=10, pady=10)
        
        self.camera_device_var = ctk.StringVar()
        device_entry = ctk.CTkEntry(device_frame, textvariable=self.camera_device_var, width=150, placeholder_text="/dev/video0")
        device_entry.pack(side="left", padx=10, pady=10)
        
        # FPS
        fps_frame = ctk.CTkFrame(camera_frame)
        fps_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        fps_label = ctk.CTkLabel(fps_frame, text="🎬 FPS:", width=200)
        fps_label.pack(side="left", padx=10, pady=10)
        
        self.fps_var = ctk.StringVar()
        fps_entry = ctk.CTkEntry(fps_frame, textvariable=self.fps_var, width=100, placeholder_text="30")
        fps_entry.pack(side="left", padx=10, pady=10)
    
    def create_control_buttons(self):
        """Create control buttons"""
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Reset to defaults
        reset_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Reset to Defaults",
            command=self.reset_to_defaults,
            width=150,
            height=40
        )
        reset_btn.pack(side="left", padx=20, pady=15)
        
        # Save settings
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            width=150,
            height=40,
            fg_color="#28a745",
            hover_color="#218838"
        )
        save_btn.pack(side="right", padx=20, pady=15)
        
        # Test camera
        test_btn = ctk.CTkButton(
            button_frame,
            text="📹 Test Camera",
            command=self.test_camera,
            width=150,
            height=40
        )
        test_btn.pack(side="right", padx=(20, 10), pady=15)
    
    def load_current_settings(self):
        """Load current settings into the GUI"""
        # Load distance thresholds
        for pose_key, pose_vars in self.distance_vars.items():
            for distance_key, var in pose_vars.items():
                threshold = self.config.get_distance_threshold(pose_key, distance_key)
                var.set(str(threshold))
        
        # Load detection settings
        self.confidence_var.set(str(self.config.get("detection_thresholds.confidence_threshold", 0.7)))
        self.overlap_var.set(str(self.config.get("detection_thresholds.overlap_threshold", 0.3)))
        
        # Load camera settings
        self.camera_device_var.set(self.config.get("camera_settings.device", "/dev/video0"))
        self.fps_var.set(str(self.config.get("camera_settings.fps", 30)))
    
    def save_settings(self):
        """Save current settings"""
        try:
            # Save distance thresholds
            for pose_key, pose_vars in self.distance_vars.items():
                for distance_key, var in pose_vars.items():
                    try:
                        value = int(var.get())
                        self.config.update_distance_threshold(pose_key, distance_key, value)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid value for {pose_key} {distance_key}")
                        return
            
            # Save detection settings
            try:
                confidence = float(self.confidence_var.get())
                overlap = float(self.overlap_var.get())
                
                if not (0 <= confidence <= 1):
                    raise ValueError("Confidence must be between 0 and 1")
                if not (0 <= overlap <= 1):
                    raise ValueError("Overlap must be between 0 and 1")
                
                self.config.set("detection_thresholds.confidence_threshold", confidence)
                self.config.set("detection_thresholds.overlap_threshold", overlap)
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid detection settings: {str(e)}")
                return
            
            # Save camera settings
            self.config.set("camera_settings.device", self.camera_device_var.get())
            
            try:
                fps = int(self.fps_var.get())
                if fps <= 0:
                    raise ValueError("FPS must be positive")
                self.config.set("camera_settings.fps", fps)
            except ValueError:
                messagebox.showerror("Error", "Invalid FPS value")
                return
            
            messagebox.showinfo("Success", "✅ Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to defaults?"):
            # Delete config file to force defaults
            config_file = Path("pet_config.json")
            if config_file.exists():
                config_file.unlink()
            
            # Reload config
            self.config = PetConfig()
            self.load_current_settings()
            
            messagebox.showinfo("Reset", "✅ Settings reset to defaults")
    
    def test_camera(self):
        """Test camera connection"""
        try:
            import cv2
            device = self.camera_device_var.get() or "/dev/video0"
            
            # Try to parse device as integer if it's just a number
            try:
                device = int(device.split('video')[-1]) if 'video' in device else int(device)
            except ValueError:
                pass
            
            camera = cv2.VideoCapture(device)
            
            if camera.isOpened():
                ret, frame = camera.read()
                if ret:
                    messagebox.showinfo("Camera Test", "✅ Camera is working correctly!")
                else:
                    messagebox.showwarning("Camera Test", "⚠️ Camera opened but couldn't capture frame")
                camera.release()
            else:
                messagebox.showerror("Camera Test", "❌ Could not open camera")
                
        except Exception as e:
            messagebox.showerror("Camera Test", f"❌ Camera test failed: {str(e)}")
    
    def run(self):
        """Start the configuration manager"""
        self.root.mainloop()

def main():
    """Run the configuration manager"""
    app = ConfigManagerGUI()
    app.run()

if __name__ == "__main__":
    main()
