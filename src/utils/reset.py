# src/utils/reset.py
import os
import shutil
from config.settings import Settings

def reset_models(models_directory='models'):
    """
    Deletes all model files in the specified directory.
    If the directory does not exist, it creates one.
    """
    if os.path.exists(models_directory):
        try:
            shutil.rmtree(models_directory)
            print(f"All models in '{models_directory}' have been deleted.")
        except Exception as e:
            print(f"Error deleting models: {e}")
    os.makedirs(models_directory, exist_ok=True)
    print(f"Directory '{models_directory}' is ready.")

def reset_generation(settings: Settings):
    """
    Resets the generation count to 1 in the settings.
    """
    settings.set('generation', 1)
    print("Generation count has been reset to 1.")

def reset_game(settings: Settings, models_directory='models'):
    """
    Performs a complete game reset:
    - Deletes all models.
    - Resets generation to 1.
    """
    reset_models(models_directory)
    reset_generation(settings)
    print("Game has been reset to generation 1.")
