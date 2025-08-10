import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import json
import os
from pathlib import Path
import numpy as np
import threading
import time
from typing import Dict, List
import pickle

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernPetTrainerGUI:
    """Modern GUI for collecting pet training data"""
    
    def __init__(self):
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("🐾 Pet Training Studio - Doorcam AI")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Data storage
        self.data_dir = Path("pet_training_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Current session data
        self.current_pet_name = ""
        self.current_pose = "front_facing"
        self.captured_images = []
        self.camera = None
        self.is_camera_active = False
        
        # Pose options
        self.pose_options = [
            ("Front Facing", "front_facing", "🐕 Pet looking directly at camera"),
            ("Side Profile", "side_profile", "🦮 Pet's side view"),
            ("Back Facing", "back_facing", "🐕‍🦺 Pet looking away from camera"),
            ("Upside Down Front", "upside_down_front", "🙃 Pet upside down, facing camera"),
            ("Upside Down Side", "upside_down_side", "🔄 Pet upside down, side view"),
            ("Standing/Sitting", "standing", "🐕 Pet in standing or sitting position")
        ]
        
        self.setup_gui()
        self.load_existing_pets()
        
    def setup_gui(self):
        """Setup the modern GUI layout"""
        # Create main container with padding
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container, 
            text="🐾 Pet Training Studio", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create main layout with two columns
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True)
        
        # Left column - Pet configuration and camera
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right column - Captured images and progress
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        
    def setup_left_panel(self, parent):
        """Setup left panel with pet configuration and camera"""
        # Pet configuration section
        config_frame = ctk.CTkFrame(parent)
        config_frame.pack(fill="x", pady=(0, 20))
        
        config_title = ctk.CTkLabel(config_frame, text="🏷️ Pet Configuration", font=ctk.CTkFont(size=20, weight="bold"))
        config_title.pack(pady=(15, 10))
        
        # Pet name input
        name_frame = ctk.CTkFrame(config_frame)
        name_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(name_frame, text="Pet Name:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.pet_name_entry = ctk.CTkEntry(
            name_frame, 
            placeholder_text="Enter your pet's name (e.g., Buddy, Whiskers)",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.pet_name_entry.pack(fill="x", pady=(5, 0))
        
        # Pet dimensions input
        dimensions_frame = ctk.CTkFrame(config_frame)
        dimensions_frame.pack(fill="x", padx=20, pady=(15, 15))
        
        ctk.CTkLabel(dimensions_frame, text="Pet Dimensions (when standing):", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        
        # Height and Length inputs
        dim_inputs_frame = ctk.CTkFrame(dimensions_frame)
        dim_inputs_frame.pack(fill="x", pady=(10, 0))
        
        # Height
        height_frame = ctk.CTkFrame(dim_inputs_frame)
        height_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(height_frame, text="Height (inches):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.pet_height_entry = ctk.CTkEntry(height_frame, placeholder_text="e.g., 24", width=80)
        self.pet_height_entry.pack(anchor="w", pady=(5, 0))
        
        # Length  
        length_frame = ctk.CTkFrame(dim_inputs_frame)
        length_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(length_frame, text="Length (inches):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.pet_length_entry = ctk.CTkEntry(length_frame, placeholder_text="e.g., 30", width=80)
        self.pet_length_entry.pack(anchor="w", pady=(5, 0))
        
        # Pet type selection
        pet_type_frame = ctk.CTkFrame(config_frame)
        pet_type_frame.pack(fill="x", padx=20, pady=(15, 15))
        
        ctk.CTkLabel(pet_type_frame, text="Pet Type:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.pet_type_var = ctk.StringVar(value="dog")
        pet_types = [("🐕 Dog", "dog"), ("🐱 Cat", "cat"), ("🐦 Bird", "bird"), ("🐰 Other", "other")]
        
        pet_type_buttons_frame = ctk.CTkFrame(pet_type_frame)
        pet_type_buttons_frame.pack(fill="x", pady=(10, 0))
        
        self.pet_type_buttons = {}
        for i, (display_name, pet_type) in enumerate(pet_types):
            btn = ctk.CTkButton(
                pet_type_buttons_frame,
                text=display_name,
                command=lambda pt=pet_type: self.select_pet_type(pt),
                width=100,
                height=35
            )
            btn.pack(side="left", padx=5)
            self.pet_type_buttons[pet_type] = btn
        
        self.select_pet_type("dog")  # Default selection
        
        # Pose selection
        pose_frame = ctk.CTkFrame(config_frame)
        pose_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(pose_frame, text="Current Pose:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        
        # Create pose buttons in a grid
        pose_grid = ctk.CTkFrame(pose_frame)
        pose_grid.pack(fill="x", pady=(10, 0))
        
        self.pose_buttons = {}
        for i, (display_name, pose_key, description) in enumerate(self.pose_options):
            btn = ctk.CTkButton(
                pose_grid,
                text=display_name,
                command=lambda pk=pose_key: self.select_pose(pk),
                width=120,
                height=35
            )
            row, col = i // 2, i % 2
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.pose_buttons[pose_key] = btn
            
            # Configure grid weights
            pose_grid.columnconfigure(col, weight=1)
        
        # Current pose description
        self.pose_description = ctk.CTkLabel(
            pose_frame, 
            text="🐕 Pet looking directly at camera",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.pose_description.pack(pady=(10, 0))
        
        # Camera section
        camera_frame = ctk.CTkFrame(parent)
        camera_frame.pack(fill="both", expand=True)
        
        camera_title = ctk.CTkLabel(camera_frame, text="📸 Camera Feed", font=ctk.CTkFont(size=20, weight="bold"))
        camera_title.pack(pady=(15, 10))
        
        # Camera controls
        camera_controls = ctk.CTkFrame(camera_frame)
        camera_controls.pack(fill="x", padx=20, pady=(0, 15))
        
        self.start_camera_btn = ctk.CTkButton(
            camera_controls,
            text="🎥 Start Camera",
            command=self.toggle_camera,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.start_camera_btn.pack(side="left", padx=(0, 10))
        
        self.capture_btn = ctk.CTkButton(
            camera_controls,
            text="📷 Capture Photo",
            command=self.capture_photo,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            state="disabled"
        )
        self.capture_btn.pack(side="left", padx=(0, 10))
        
        self.save_session_btn = ctk.CTkButton(
            camera_controls,
            text="💾 Save Training Data",
            command=self.save_training_session,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.save_session_btn.pack(side="right")
        
        # Camera display
        self.camera_label = ctk.CTkLabel(camera_frame, text="📹 Camera will appear here", font=ctk.CTkFont(size=16))
        self.camera_label.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Update pose selection
        self.select_pose("front_facing")
        
    def setup_right_panel(self, parent):
        """Setup right panel with captured images and progress"""
        # Progress section
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        progress_title = ctk.CTkLabel(progress_frame, text="📊 Training Progress", font=ctk.CTkFont(size=20, weight="bold"))
        progress_title.pack(pady=(15, 10))
        
        # Statistics
        stats_frame = ctk.CTkFrame(progress_frame)
        stats_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.stats_label = ctk.CTkLabel(
            stats_frame, 
            text="📈 No photos captured yet",
            font=ctk.CTkFont(size=14)
        )
        self.stats_label.pack(pady=10)
        
        # Captured images section
        images_frame = ctk.CTkFrame(parent)
        images_frame.pack(fill="both", expand=True)
        
        images_title = ctk.CTkLabel(images_frame, text="🖼️ Captured Images", font=ctk.CTkFont(size=20, weight="bold"))
        images_title.pack(pady=(15, 10))
        
        # Scrollable frame for images
        self.images_scroll = ctk.CTkScrollableFrame(images_frame, height=400)
        self.images_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Existing pets section
        existing_frame = ctk.CTkFrame(parent)
        existing_frame.pack(fill="x", pady=(20, 0))
        
        existing_title = ctk.CTkLabel(existing_frame, text="🏠 Trained Pets", font=ctk.CTkFont(size=18, weight="bold"))
        existing_title.pack(pady=(15, 10))
        
        self.existing_pets_frame = ctk.CTkFrame(existing_frame)
        self.existing_pets_frame.pack(fill="x", padx=20, pady=(0, 15))
        
    def select_pet_type(self, pet_type):
        """Select pet type"""
        self.pet_type_var.set(pet_type)
        
        # Update button colors
        for ptype, btn in self.pet_type_buttons.items():
            if ptype == pet_type:
                btn.configure(fg_color="#1f538d")  # Active color
            else:
                btn.configure(fg_color="#3b82f6")  # Default color
    
    def select_pose(self, pose_key):
        """Select a pose for training"""
        self.current_pose = pose_key
        
        # Update button colors
        for key, btn in self.pose_buttons.items():
            if key == pose_key:
                btn.configure(fg_color="#1f538d")  # Active color
            else:
                btn.configure(fg_color="#3b82f6")  # Default color
        
        # Update description
        for display_name, key, description in self.pose_options:
            if key == pose_key:
                self.pose_description.configure(text=description)
                break
    
    def toggle_camera(self):
        """Start or stop camera"""
        if not self.is_camera_active:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Start camera feed"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Could not open camera")
                return
            
            self.is_camera_active = True
            self.start_camera_btn.configure(text="🛑 Stop Camera")
            self.capture_btn.configure(state="normal")
            
            # Start camera update thread
            self.camera_thread = threading.Thread(target=self.update_camera_feed, daemon=True)
            self.camera_thread.start()
            
        except Exception as e:
            messagebox.showerror("Camera Error", f"Failed to start camera: {str(e)}")
    
    def stop_camera(self):
        """Stop camera feed"""
        self.is_camera_active = False
        if self.camera:
            self.camera.release()
        
        self.start_camera_btn.configure(text="🎥 Start Camera")
        self.capture_btn.configure(state="disabled")
        self.camera_label.configure(image="", text="📹 Camera stopped")
    
    def update_camera_feed(self):
        """Update camera feed in GUI"""
        while self.is_camera_active and self.camera:
            ret, frame = self.camera.read()
            if ret:
                # Convert frame to display format
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (480, 360))
                
                # Convert to PhotoImage
                image = Image.fromarray(frame_resized)
                photo = ImageTk.PhotoImage(image)
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.camera_label.configure(image=photo, text=""))
                self.root.after(0, lambda: setattr(self.camera_label, 'image', photo))  # Keep reference
            
            time.sleep(1/30)  # 30 FPS
    
    def capture_photo(self):
        """Capture current camera frame"""
        if not self.camera or not self.is_camera_active:
            messagebox.showwarning("Warning", "Camera is not active")
            return
        
        pet_name = self.pet_name_entry.get().strip()
        if not pet_name:
            messagebox.showwarning("Warning", "Please enter a pet name first")
            return
        
        # Get pet dimensions
        try:
            pet_height = float(self.pet_height_entry.get().strip()) if self.pet_height_entry.get().strip() else 0
            pet_length = float(self.pet_length_entry.get().strip()) if self.pet_length_entry.get().strip() else 0
        except ValueError:
            messagebox.showwarning("Warning", "Please enter valid numbers for pet dimensions")
            return
        
        if pet_height <= 0 or pet_length <= 0:
            messagebox.showwarning("Warning", "Please enter pet height and length in inches")
            return
        
        ret, frame = self.camera.read()
        if ret:
            # Store the captured image with dimensions
            timestamp = int(time.time() * 1000)
            image_data = {
                'pet_name': pet_name,
                'pose': self.current_pose,
                'timestamp': timestamp,
                'frame': frame,
                'height_inches': pet_height,
                'length_inches': pet_length,
                'pet_type': self.pet_type_var.get()
            }
            self.captured_images.append(image_data)
            
            # Add to GUI display
            self.add_captured_image_to_display(frame, pet_name, self.current_pose)
            
            # Update statistics
            self.update_statistics()
            
            messagebox.showinfo("Success", f"📸 Photo captured for {pet_name} ({self.current_pose})\nDimensions: {pet_height}\" H x {pet_length}\" L")
        else:
            messagebox.showerror("Error", "Failed to capture photo")
    
    def add_captured_image_to_display(self, frame, pet_name, pose):
        """Add captured image to the display"""
        # Create frame for this image
        img_frame = ctk.CTkFrame(self.images_scroll)
        img_frame.pack(fill="x", pady=5)
        
        # Convert and resize image for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (120, 90))
        image = Image.fromarray(frame_resized)
        photo = ImageTk.PhotoImage(image)
        
        # Image display
        img_label = ctk.CTkLabel(img_frame, image=photo, text="")
        img_label.image = photo  # Keep reference
        img_label.pack(side="left", padx=10, pady=10)
        
        # Info label
        info_text = f"🐾 {pet_name}\n📐 {pose.replace('_', ' ').title()}\n⏰ {time.strftime('%H:%M:%S')}"
        info_label = ctk.CTkLabel(img_frame, text=info_text, justify="left")
        info_label.pack(side="left", padx=(0, 10), pady=10)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            img_frame,
            text="🗑️",
            width=30,
            height=30,
            command=lambda: self.delete_captured_image(img_frame, len(self.captured_images)-1)
        )
        delete_btn.pack(side="right", padx=10, pady=10)
    
    def delete_captured_image(self, img_frame, index):
        """Delete a captured image"""
        if 0 <= index < len(self.captured_images):
            del self.captured_images[index]
            img_frame.destroy()
            self.update_statistics()
    
    def update_statistics(self):
        """Update training statistics"""
        if not self.captured_images:
            self.stats_label.configure(text="📈 No photos captured yet")
            return
        
        # Count by pose
        pose_counts = {}
        for img_data in self.captured_images:
            pose = img_data['pose']
            pose_counts[pose] = pose_counts.get(pose, 0) + 1
        
        total = len(self.captured_images)
        stats_text = f"📈 Total Photos: {total}\n\n"
        
        for pose_key, count in pose_counts.items():
            pose_name = pose_key.replace('_', ' ').title()
            stats_text += f"📐 {pose_name}: {count}\n"
        
        self.stats_label.configure(text=stats_text)
    
    def save_training_session(self):
        """Save all captured training data"""
        if not self.captured_images:
            messagebox.showwarning("Warning", "No images to save")
            return
        
        pet_name = self.pet_name_entry.get().strip()
        if not pet_name:
            messagebox.showwarning("Warning", "Please enter a pet name")
            return
        
        try:
            # Create pet directory
            pet_dir = self.data_dir / pet_name
            pet_dir.mkdir(exist_ok=True)
            
            # Save images and extract features
            features_by_pose = {}
            
            for i, img_data in enumerate(self.captured_images):
                # Save image
                image_filename = f"{img_data['pose']}_{img_data['timestamp']}.jpg"
                image_path = pet_dir / image_filename
                cv2.imwrite(str(image_path), img_data['frame'])
                
                # Extract features (simple HOG features)
                gray = cv2.cvtColor(img_data['frame'], cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (128, 128))
                
                # Create HOG descriptor
                hog = cv2.HOGDescriptor()
                features = hog.compute(resized)
                
                if features is not None:
                    pose = img_data['pose']
                    if pose not in features_by_pose:
                        features_by_pose[pose] = []
                    features_by_pose[pose].append(features.flatten())
            
            # Save pet profile with dimensions
            profile = {
                'name': pet_name,
                'total_images': len(self.captured_images),
                'poses': list(features_by_pose.keys()),
                'created_at': time.time(),
                'image_count_by_pose': {pose: len(features) for pose, features in features_by_pose.items()},
                'height_inches': self.captured_images[0]['height_inches'] if self.captured_images else 0,
                'length_inches': self.captured_images[0]['length_inches'] if self.captured_images else 0,
                'pet_type': self.captured_images[0]['pet_type'] if self.captured_images else 'unknown'
            }
            
            # Save profile JSON
            profile_path = self.data_dir / "pet_profiles.json"
            profiles = {}
            if profile_path.exists():
                with open(profile_path, 'r') as f:
                    profiles = json.load(f)
            
            profiles[pet_name] = profile
            
            with open(profile_path, 'w') as f:
                json.dump(profiles, f, indent=4)
            
            # Save features
            features_path = self.data_dir / f"{pet_name}_features.pkl"
            with open(features_path, 'wb') as f:
                pickle.dump(features_by_pose, f)
            
            # Clear current session
            self.captured_images.clear()
            self.update_statistics()
            
            # Clear images display
            for widget in self.images_scroll.winfo_children():
                widget.destroy()
            
            # Refresh existing pets display
            self.load_existing_pets()
            
            messagebox.showinfo("Success", f"✅ Training data saved for {pet_name}!\n\nTotal images: {len(self.captured_images)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save training data: {str(e)}")
    
    def load_existing_pets(self):
        """Load and display existing trained pets"""
        # Clear existing display
        for widget in self.existing_pets_frame.winfo_children():
            widget.destroy()
        
        profile_path = self.data_dir / "pet_profiles.json"
        if not profile_path.exists():
            no_pets_label = ctk.CTkLabel(self.existing_pets_frame, text="No trained pets yet")
            no_pets_label.pack(pady=10)
            return
        
        try:
            with open(profile_path, 'r') as f:
                profiles = json.load(f)
            
            if not profiles:
                no_pets_label = ctk.CTkLabel(self.existing_pets_frame, text="No trained pets yet")
                no_pets_label.pack(pady=10)
                return
            
            for pet_name, profile in profiles.items():
                pet_frame = ctk.CTkFrame(self.existing_pets_frame)
                pet_frame.pack(fill="x", padx=10, pady=5)
                
                # Pet info
                info_text = f"🐾 {pet_name}\n📊 {profile.get('total_images', 0)} images\n📐 {len(profile.get('poses', []))} poses"
                info_label = ctk.CTkLabel(pet_frame, text=info_text, justify="left")
                info_label.pack(side="left", padx=15, pady=10)
                
                # Delete button
                delete_btn = ctk.CTkButton(
                    pet_frame,
                    text="🗑️ Delete",
                    width=80,
                    height=30,
                    fg_color="#dc3545",
                    hover_color="#c82333",
                    command=lambda name=pet_name: self.delete_pet(name)
                )
                delete_btn.pack(side="right", padx=15, pady=10)
                
        except Exception as e:
            error_label = ctk.CTkLabel(self.existing_pets_frame, text=f"Error loading pets: {str(e)}")
            error_label.pack(pady=10)
    
    def delete_pet(self, pet_name):
        """Delete a trained pet"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete training data for {pet_name}?"):
            try:
                # Remove from profiles
                profile_path = self.data_dir / "pet_profiles.json"
                if profile_path.exists():
                    with open(profile_path, 'r') as f:
                        profiles = json.load(f)
                    
                    if pet_name in profiles:
                        del profiles[pet_name]
                        
                        with open(profile_path, 'w') as f:
                            json.dump(profiles, f, indent=4)
                
                # Remove features file
                features_path = self.data_dir / f"{pet_name}_features.pkl"
                if features_path.exists():
                    features_path.unlink()
                
                # Remove pet directory
                pet_dir = self.data_dir / pet_name
                if pet_dir.exists():
                    import shutil
                    shutil.rmtree(pet_dir)
                
                # Refresh display
                self.load_existing_pets()
                messagebox.showinfo("Success", f"Training data for {pet_name} has been deleted")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete pet data: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        finally:
            # Cleanup
            if self.is_camera_active:
                self.stop_camera()

def main():
    """Run the Pet Training GUI"""
    app = ModernPetTrainerGUI()
    app.run()

if __name__ == "__main__":
    main()
