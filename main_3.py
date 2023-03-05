import cv2
import pyaudio
import wave
import threading
import pyautogui
import numpy as np
from moviepy.editor import *


# Define video recording function
def record_video(max_record_seconds):
    # Define video codec and output file format
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1920, 1080))

    # Record video for specified maximum seconds
    for i in range(int(max_record_seconds * 20)):
        # Take screenshot of the desktop
        img = pyautogui.screenshot()

        # Convert screenshot to OpenCV format
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Write frame to video output file
        out.write(frame)

    # Release video capture and output objects
    out.release()

# Define audio recording function
def record_audio(max_record_seconds):
    # Initialize PyAudio object
    audio = pyaudio.PyAudio()

    # Define audio recording parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    # Record audio for specified maximum seconds
    frames = []
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    for i in range(0, int(RATE / CHUNK * max_record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    audio.terminate()

    # Save recorded audio to file
    wf = wave.open("output.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Set maximum record time to 10 seconds
MAX_RECORD_TIME = 120

# Start video and audio recording threads
video_thread = threading.Thread(target=record_video, args=(MAX_RECORD_TIME,))
audio_thread = threading.Thread(target=record_audio, args=(MAX_RECORD_TIME,))
video_thread.start()
audio_thread.start()

# Wait for both threads to finish
video_thread.join()
audio_thread.join()

# Load video and audio files using MoviePy
video_clip = VideoFileClip('output.avi')
audio_clip = AudioFileClip('output.wav')

# Combine video and audio files
final_clip = video_clip.set_audio(audio_clip)

# Write final video file to disk
final_clip.write_videofile("output_final.mp4", codec='libx264', audio_codec='aac')

