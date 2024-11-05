# config/settings.py
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
            'gravity': 9.81,
            'max_torque': 1000.0,
            'max_motor_velocity': 10.0,
            'save_interval': 100,
            'enable_transparency': False,
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
            'gravity': 9.81,
            'max_torque': 1000.0,
            'max_motor_velocity': 10.0,
            'save_interval': 100,
            'enable_transparency': False
            # Add other default settings as needed
        }
