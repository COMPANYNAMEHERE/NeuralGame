# config/settings.py

import os

class Settings:
    def __init__(self):
        # Initialize default settings
        self.settings = {
            'screen_width': 800,
            'screen_height': 600,
            'learning_rate': 0.001,
            'hidden_size': 128,
            'iteration_time': 60,
            'batch_size': 32,
            'mutation_rate': 0.05,
            'gravity': 1000.0,  # Updated to match slider's initial value
            'max_torque': 50000.0,  # Example mid-point value
            'max_motor_velocity': 10.0,
            'save_interval': 100,
            'enable_transparency': False,
            'enable_recording': False,  # New setting for enabling recording
            'video_output_folder': os.path.join('src', 'recordings'),  # New setting for video output
            'running': False,
            'generation': 1  # Start from generation 1
        }

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value

    def default_settings(self):
        # Return a copy of default settings
        return {
            'learning_rate': 0.001,
            'hidden_size': 128,
            'iteration_time': 60,
            'batch_size': 32,
            'mutation_rate': 0.05,
            'gravity': 1000.0,  # Ensure the new setting is included
            'max_torque': 50000.0,  # Ensure the new setting is included
            'max_motor_velocity': 10.0,
            'save_interval': 100,
            'enable_transparency': False,
            'enable_recording': False,  # Ensure the new setting is included
            'video_output_folder': os.path.join('src', 'recordings')  # Ensure default is included
            # Add other default settings as needed
        }
