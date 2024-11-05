# src/utils/recorder.py

import os
import threading
import pygame
import subprocess
import shutil
import logging
from datetime import datetime
from typing import Callable, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class ScreenRecorder:
    """
    A class to record Pygame screen screenshots at regular intervals and convert them into a video using FFmpeg.

    Public Methods:
    - start_recording()
    - stop_recording(on_complete: Optional[Callable[[str], None]] = None, on_error: Optional[Callable[[str], None]] = None)
    """

    def __init__(self, screen: pygame.Surface, get_size_callback: Callable[[], tuple], video_output_folder: str, screenshot_interval: float = 1.0):
        """
        Initializes the ScreenRecorder.

        :param screen: The Pygame screen surface to capture.
        :param get_size_callback: A callback function to get the current screen size.
        :param video_output_folder: The directory where the video will be saved.
        :param screenshot_interval: Time interval between screenshots in seconds.
        """
        self.screen = screen
        self.get_size = get_size_callback
        self.video_output_folder = video_output_folder
        self.screenshot_interval = screenshot_interval

        self.recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.conversion_thread: Optional[threading.Thread] = None

        self.screenshot_folder = self._create_screenshot_folder()
        self.frame_count = 0
        self.start_time = None
        self.screen_size = self.get_size()

        self.lock = threading.Lock()
        self.stop_event = threading.Event()

        logger.info(f"Initialized ScreenRecorder with video output folder: {self.video_output_folder}")

    def start_recording(self) -> None:
        """
        Starts the recording process.
        """
        with self.lock:
            if self.recording:
                logger.warning("Recording is already in progress.")
                return
            self.recording = True
            self.stop_event.clear()
            self.start_time = datetime.now()
            self.recording_thread = threading.Thread(target=self._record, daemon=True)
            self.recording_thread.start()
            logger.info(f"Recording started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def stop_recording(self, on_complete: Optional[Callable[[str], None]] = None, on_error: Optional[Callable[[str], None]] = None) -> None:
        """
        Stops the recording process and converts the screenshots into a video.

        :param on_complete: Callback function called when conversion is complete.
        :param on_error: Callback function called when an error occurs.
        """
        with self.lock:
            if not self.recording:
                logger.warning("No recording is in progress to stop.")
                return
            self.recording = False
            self.stop_event.set()
            if self.recording_thread and self.recording_thread.is_alive():
                logger.info("Stopping recording thread...")
                self.recording_thread.join(timeout=10)
                if self.recording_thread.is_alive():
                    logger.warning("Recording thread did not finish within the timeout period. Forcing termination.")
            logger.info("Recording stopped.")
            self.conversion_thread = threading.Thread(target=self._convert_to_video, args=(on_complete, on_error), daemon=True)
            self.conversion_thread.start()

    def _record(self) -> None:
        """
        Records screenshots at regular intervals in a separate thread.
        """
        logger.debug("Recording thread started.")
        while not self.stop_event.is_set():
            current_size = self.get_size()
            if current_size != self.screen_size:
                logger.warning(f"Screen size changed from {self.screen_size} to {current_size}. Stopping recording.")
                self.recording = False
                break
            self._take_screenshot()
            self.stop_event.wait(self.screenshot_interval)
        logger.debug("Recording thread exiting.")

    def _take_screenshot(self) -> None:
        """
        Takes a screenshot and saves it to the screenshot folder.
        Discards screenshots that are entirely white.
        """
        filename = os.path.join(self.screenshot_folder, f"screenshot_{self.frame_count:05d}.png")
        try:
            temp_surface = self.screen.copy()
            avg_color = pygame.transform.average_color(temp_surface)
            if avg_color[:3] == (255, 255, 255):  # Ignore alpha if present
                logger.debug(f"Discarding white screenshot number: {self.frame_count}")
                return
            pygame.image.save(temp_surface, filename)
            self.frame_count += 1
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save screenshot {filename}: {e}")

    def _convert_to_video(self, on_complete: Optional[Callable[[str], None]] = None, on_error: Optional[Callable[[str], None]] = None) -> None:
        """
        Uses FFmpeg to convert the screenshots into a video.

        :param on_complete: Callback function called when conversion is complete.
        :param on_error: Callback function called when an error occurs.
        """
        if not self.frame_count:
            error_msg = "No screenshots were captured. Video conversion aborted."
            logger.error(error_msg)
            if on_error:
                on_error(error_msg)
            return

        timestamp = self.start_time.strftime('%Y%m%d_%H%M%S') if self.start_time else 'unknown_time'
        video_filename = os.path.join(self.video_output_folder, f"recording_{timestamp}.mp4")
        input_pattern = os.path.join(self.screenshot_folder, 'screenshot_%05d.png')

        command = [
            'ffmpeg',
            '-y',  # Overwrite output files without asking
            '-framerate', '30',
            '-i', input_pattern,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            video_filename
        ]

        logger.info(f"Converting screenshots to video: {video_filename}")
        logger.debug(f"FFmpeg command: {' '.join(command)}")

        try:
            # Suppress FFmpeg output by redirecting to DEVNULL
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Video conversion successful. Video saved at: {video_filename}")
            if on_complete:
                on_complete(video_filename)
            self._cleanup_screenshots()
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg failed with error code {e.returncode}."
            logger.error(error_msg)
            if on_error:
                on_error(error_msg)
        except FileNotFoundError:
            error_msg = "FFmpeg is not installed or not found in the system's PATH."
            logger.error(error_msg)
            if on_error:
                on_error(error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred during video conversion: {e}"
            logger.error(error_msg)
            if on_error:
                on_error(error_msg)

    def _create_screenshot_folder(self) -> str:
        """
        Creates the temporary screenshots folder.

        :return: Path to the temporary screenshots folder.
        """
        temporary_dir = os.path.join(os.path.dirname(__file__), 'temporary')
        try:
            os.makedirs(temporary_dir, exist_ok=True)
            logger.info(f"Temporary screenshots will be saved to: {temporary_dir}")
            return temporary_dir
        except Exception as e:
            logger.error(f"Failed to create temporary screenshot folder at {temporary_dir}: {e}")
            raise

    def _cleanup_screenshots(self) -> None:
        """
        Deletes the screenshot images after video conversion.
        Retries deletion up to 3 times in case of failure.
        """
        retries = 3
        for attempt in range(1, retries + 1):
            try:
                shutil.rmtree(self.screenshot_folder)
                logger.info(f"Cleaned up screenshots successfully from {self.screenshot_folder}.")
                return
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed to clean up screenshots: {e}")
                time.sleep(1)
        logger.error(f"Failed to clean up screenshots after {retries} attempts.")

    def is_recording(self) -> bool:
        """
        Checks if the recorder is currently recording.

        :return: True if recording, False otherwise.
        """
        with self.lock:
            return self.recording

    def get_recording_duration(self) -> Optional[float]:
        """
        Returns the duration of the current recording in seconds.

        :return: Duration in seconds, or None if not recording.
        """
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return None


# Public Classes
__all__ = ['ScreenRecorder']
