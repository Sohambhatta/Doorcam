#!/usr/bin/env python3
"""
🚪 Door Motor Controller
========================

Controls dual motors for door opening/closing with synchronized string management.
One motor pulls to open, the other loosens. When closing, roles reverse.
"""

import time
import threading
from typing import Optional, Callable
from enum import Enum

# Uncomment these imports when running on actual hardware
# import RPi.GPIO as GPIO  # For Raspberry Pi
# import Jetson.GPIO as GPIO  # For Jetson Nano

class DoorState(Enum):
    """Door states"""
    CLOSED = "closed"
    OPENING = "opening"
    OPEN = "open"
    CLOSING = "closing"
    STOPPED = "stopped"
    ERROR = "error"

class MotorController:
    """Dual motor controller for door operation"""
    
    def __init__(self, 
                 motor1_pin1: int = 18, motor1_pin2: int = 19,  # Motor 1 (opening motor)
                 motor2_pin1: int = 20, motor2_pin2: int = 21,  # Motor 2 (closing motor)
                 enable_pin1: int = 12, enable_pin2: int = 13,  # PWM enable pins
                 simulation_mode: bool = True):
        """
        Initialize motor controller
        
        Args:
            motor1_pin1, motor1_pin2: Motor 1 direction pins
            motor2_pin1, motor2_pin2: Motor 2 direction pins  
            enable_pin1, enable_pin2: PWM speed control pins
            simulation_mode: If True, simulate motors without GPIO
        """
        self.motor1_pin1 = motor1_pin1
        self.motor1_pin2 = motor1_pin2
        self.motor2_pin1 = motor2_pin1
        self.motor2_pin2 = motor2_pin2
        self.enable_pin1 = enable_pin1
        self.enable_pin2 = enable_pin2
        
        self.simulation_mode = simulation_mode
        self.door_state = DoorState.CLOSED
        self.is_moving = False
        self.stop_requested = False
        
        # Motor speeds (0-100)
        self.opening_speed = 75
        self.closing_speed = 70
        self.loosening_speed = 80  # Slightly faster to prevent tension
        
        # Timing
        self.full_open_time = 3.0  # Seconds to fully open door
        self.full_close_time = 3.5  # Seconds to fully close door
        
        # Callbacks
        self.state_change_callback: Optional[Callable[[DoorState], None]] = None
        
        if not simulation_mode:
            self.setup_gpio()
        else:
            print("🎮 Motor controller in simulation mode")
    
    def setup_gpio(self):
        """Setup GPIO pins for motor control"""
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            
            # Setup motor pins
            GPIO.setup([self.motor1_pin1, self.motor1_pin2, 
                       self.motor2_pin1, self.motor2_pin2], GPIO.OUT)
            GPIO.setup([self.enable_pin1, self.enable_pin2], GPIO.OUT)
            
            # Setup PWM for speed control
            self.pwm1 = GPIO.PWM(self.enable_pin1, 1000)  # 1kHz
            self.pwm2 = GPIO.PWM(self.enable_pin2, 1000)
            
            self.pwm1.start(0)
            self.pwm2.start(0)
            
            print("✅ GPIO setup complete")
            
        except ImportError:
            print("⚠️  RPi.GPIO not available, falling back to simulation mode")
            self.simulation_mode = True
        except Exception as e:
            print(f"❌ GPIO setup failed: {e}")
            self.simulation_mode = True
    
    def set_state_callback(self, callback: Callable[[DoorState], None]):
        """Set callback for door state changes"""
        self.state_change_callback = callback
    
    def _notify_state_change(self, new_state: DoorState):
        """Notify about state change"""
        self.door_state = new_state
        print(f"🚪 Door state: {new_state.value.upper()}")
        
        if self.state_change_callback:
            self.state_change_callback(new_state)
    
    def _set_motor_speed(self, motor_num: int, speed: int, direction: str):
        """
        Set motor speed and direction
        
        Args:
            motor_num: 1 or 2
            speed: 0-100
            direction: 'forward', 'reverse', or 'stop'
        """
        if self.simulation_mode:
            action = "STOP" if speed == 0 else f"{direction.upper()} at {speed}%"
            print(f"🔧 Motor {motor_num}: {action}")
            return
        
        # Real GPIO control
        if motor_num == 1:
            pin1, pin2, pwm = self.motor1_pin1, self.motor1_pin2, self.pwm1
        else:
            pin1, pin2, pwm = self.motor2_pin1, self.motor2_pin2, self.pwm2
        
        if direction == 'forward':
            self.GPIO.output(pin1, self.GPIO.HIGH)
            self.GPIO.output(pin2, self.GPIO.LOW)
        elif direction == 'reverse':
            self.GPIO.output(pin1, self.GPIO.LOW)
            self.GPIO.output(pin2, self.GPIO.HIGH)
        else:  # stop
            self.GPIO.output(pin1, self.GPIO.LOW)
            self.GPIO.output(pin2, self.GPIO.LOW)
            speed = 0
        
        pwm.ChangeDutyCycle(speed)
    
    def _stop_all_motors(self):
        """Stop both motors immediately"""
        self._set_motor_speed(1, 0, 'stop')
        self._set_motor_speed(2, 0, 'stop')
        self.is_moving = False
    
    def open_door(self) -> bool:
        """
        Open the door
        
        Returns:
            True if operation started successfully
        """
        if self.is_moving:
            print("⚠️  Door is already moving")
            return False
        
        if self.door_state == DoorState.OPEN:
            print("ℹ️  Door is already open")
            return True
        
        if self.door_state == DoorState.ERROR:
            print("❌ Door is in error state, cannot open")
            return False
        
        print("🔓 Starting door opening sequence...")
        self._notify_state_change(DoorState.OPENING)
        self.is_moving = True
        self.stop_requested = False
        
        # Start opening in a separate thread
        thread = threading.Thread(target=self._opening_sequence, daemon=True)
        thread.start()
        
        return True
    
    def close_door(self) -> bool:
        """
        Close the door
        
        Returns:
            True if operation started successfully
        """
        if self.is_moving:
            print("⚠️  Door is already moving")
            return False
        
        if self.door_state == DoorState.CLOSED:
            print("ℹ️  Door is already closed")
            return True
        
        if self.door_state == DoorState.ERROR:
            print("❌ Door is in error state, cannot close")
            return False
        
        print("🔒 Starting door closing sequence...")
        self._notify_state_change(DoorState.CLOSING)
        self.is_moving = True
        self.stop_requested = False
        
        # Start closing in a separate thread
        thread = threading.Thread(target=self._closing_sequence, daemon=True)
        thread.start()
        
        return True
    
    def emergency_stop(self):
        """Emergency stop - immediately halt all motor movement"""
        print("🛑 EMERGENCY STOP activated!")
        self.stop_requested = True
        self._stop_all_motors()
        self._notify_state_change(DoorState.STOPPED)
    
    def _opening_sequence(self):
        """Execute door opening sequence"""
        try:
            print("🔧 Motor 1 (opener): PULLING to open door")
            print("🔧 Motor 2 (closer): LOOSENING string")
            
            # Motor 1 pulls to open, Motor 2 loosens at slightly higher speed
            self._set_motor_speed(1, self.opening_speed, 'forward')
            self._set_motor_speed(2, self.loosening_speed, 'reverse')
            
            # Run for the calculated time
            start_time = time.time()
            while time.time() - start_time < self.full_open_time:
                if self.stop_requested:
                    self._stop_all_motors()
                    self._notify_state_change(DoorState.STOPPED)
                    return
                time.sleep(0.1)
            
            # Stop all motors
            self._stop_all_motors()
            self._notify_state_change(DoorState.OPEN)
            print("✅ Door opened successfully")
            
        except Exception as e:
            print(f"❌ Error during opening: {e}")
            self._stop_all_motors()
            self._notify_state_change(DoorState.ERROR)
    
    def _closing_sequence(self):
        """Execute door closing sequence"""
        try:
            print("🔧 Motor 2 (closer): PULLING to close door")
            print("🔧 Motor 1 (opener): LOOSENING string")
            
            # Motor 2 pulls to close, Motor 1 loosens at slightly higher speed
            self._set_motor_speed(2, self.closing_speed, 'forward')
            self._set_motor_speed(1, self.loosening_speed, 'reverse')
            
            # Run for the calculated time
            start_time = time.time()
            while time.time() - start_time < self.full_close_time:
                if self.stop_requested:
                    self._stop_all_motors()
                    self._notify_state_change(DoorState.STOPPED)
                    return
                time.sleep(0.1)
            
            # Stop all motors
            self._stop_all_motors()
            self._notify_state_change(DoorState.CLOSED)
            print("✅ Door closed successfully")
            
        except Exception as e:
            print(f"❌ Error during closing: {e}")
            self._stop_all_motors()
            self._notify_state_change(DoorState.ERROR)
    
    def get_status(self) -> dict:
        """Get current motor controller status"""
        return {
            'door_state': self.door_state.value,
            'is_moving': self.is_moving,
            'simulation_mode': self.simulation_mode,
            'opening_speed': self.opening_speed,
            'closing_speed': self.closing_speed,
            'full_open_time': self.full_open_time,
            'full_close_time': self.full_close_time
        }
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if not self.simulation_mode and hasattr(self, 'GPIO'):
            self.emergency_stop()
            time.sleep(0.5)  # Give time for motors to stop
            
            try:
                self.pwm1.stop()
                self.pwm2.stop()
                self.GPIO.cleanup()
                print("🧹 GPIO cleanup complete")
            except Exception as e:
                print(f"⚠️  GPIO cleanup error: {e}")

def demo_motor_controller():
    """Demo the motor controller"""
    print("🚪 Motor Controller Demo")
    print("=" * 30)
    
    # Create controller in simulation mode
    controller = MotorController(simulation_mode=True)
    
    def on_state_change(state):
        print(f"📢 State changed to: {state.value}")
    
    controller.set_state_callback(on_state_change)
    
    try:
        # Demo sequence
        print("\n🔓 Opening door...")
        controller.open_door()
        time.sleep(4)  # Wait for opening to complete
        
        print("\n⏳ Waiting 2 seconds...")
        time.sleep(2)
        
        print("\n🔒 Closing door...")
        controller.close_door()
        time.sleep(4)  # Wait for closing to complete
        
        print("\n📊 Final status:")
        status = controller.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
        controller.emergency_stop()
    finally:
        controller.cleanup()

if __name__ == "__main__":
    demo_motor_controller()
