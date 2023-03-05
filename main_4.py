import cv2
import pyaudio
import wave
import pyautogui
import numpy as np
from moviepy.editor import *
from multiprocessing import Process, Queue

def record_video(queue, max_record_seconds):
    # Get screen dimensions and frame rate
    screen_size = pyautogui.size()
    screen_fps = cv2.VideoCapture(0).get(cv2.CAP_PROP_FPS)

    # Define video codec and output file format
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, screen_fps, screen_size)

    # Record video for specified maximum seconds
    for i in range(int(max_record_seconds * screen_fps)):
        # Take screenshot of the desktop
        img = pyautogui.screenshot()

        # Convert screenshot to OpenCV format
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Write frame to video output file
        out.write(frame)

    # Release video capture and output objects
    out.release()

    # Put a message in the queue to indicate that the video recording has finished
    queue.put('video done')

def record_audio(queue, max_record_seconds):
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

    # Put a message in the queue to indicate that the audio recording has finished
    queue.put('audio done')

if __name__ == '__main__':
    # Set maximum record time to 10 seconds
    MAX_RECORD_TIME = 10

    # Create a queue to hold messages from the recording processes
    queue = Queue()

    # Start video and audio recording processes
    video_process = Process(target=record_video, args=(queue, MAX_RECORD_TIME))
    audio_process = Process(target=record_audio, args=(queue, MAX_RECORD_TIME))
    video_process.start()
    audio_process.start()

    # Wait for both processes to finish
    video_done = False
    audio_done = False
    while not video_done or not audio_done:
        msg = queue.get()
        if msg == 'video done':
            video_done = True
        elif msg == 'audio done':
            audio_done = True

    # Load video and audio files using MoviePy
    video_clip = VideoFileClip('output.avi')
    audio_clip = AudioFileClip('output.wav')

    # Combine video and audio files
    final_clip = video_clip.set_audio(audio_clip)

    # Write final video file to disk
    final_clip.write_videofile("output_final.mp4", codec='libx264', audio_codec='aac')

