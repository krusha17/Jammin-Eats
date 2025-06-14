import os
from pygame import mixer
from src.core.constants import ASSETS_DIR


def load_sounds():
    """Load all game sounds with error handling"""
    sounds = {}

    try:
        # Load sound effects
        try:
            sounds["pickup_sound"] = mixer.Sound(
                os.path.join(ASSETS_DIR, "sounds", "characters", "food_throw.wav")
            )
            sounds["engine_sound"] = mixer.Sound(
                os.path.join(ASSETS_DIR, "sounds", "vehicles", "engine_idle.wav")
            )
            sounds["button_sound"] = mixer.Sound(
                os.path.join(ASSETS_DIR, "sounds", "ui", "button_click.wav")
            )
        except Exception as e:
            print(f"Error loading sound: {e}")
            sounds["pickup_sound"] = None
            sounds["engine_sound"] = None
            sounds["button_sound"] = None

        # Try to create background music - fallback to looping a sound if needed
        try:
            mixer.music.load(
                os.path.join(ASSETS_DIR, "sounds", "characters", "food_throw.wav")
            )  # Placeholder for background music
            mixer.music.set_volume(0.5)
            mixer.music.play(-1)  # Loop indefinitely
            sounds["music_loaded"] = True
        except Exception as e:
            print(f"Error loading background music: {e}")
            print("No background music found, continuing without it")
            sounds["music_loaded"] = False

    except Exception as e:
        print(f"Error loading sounds: {e}")
        print("Continuing without audio")
        sounds = {
            "pickup_sound": None,
            "engine_sound": None,
            "button_sound": None,
            "music_loaded": False,
        }

    return sounds


def play_sound(sound_name, sounds_dict):
    """Play a sound if it exists in the sounds dictionary"""
    if sounds_dict and sound_name in sounds_dict and sounds_dict[sound_name]:
        sounds_dict[sound_name].play()
        return True
    return False


def stop_all_sounds():
    """Stop all currently playing sounds"""
    mixer.stop()  # Stop all sound effects
    mixer.music.stop()  # Stop background music


def set_music_volume(volume):
    """Set background music volume (0.0 to 1.0)"""
    mixer.music.set_volume(max(0.0, min(1.0, volume)))  # Clamp between 0 and 1
