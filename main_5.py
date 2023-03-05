import av
import numpy as np
import pyaudio
import threading
import time
import cv2

# Define constants
screen_width = 1920
screen_height = 1080
frame_rate = 30
channels = 2
sample_rate = 44100
block_size = 1024
duration = 10

# Initialize PyAudio object
pa = pyaudio.PyAudio()

# Initialize video stream writer
container = av.open('output.mp4', mode='w')
video_stream = container.add_stream('libx264', rate=frame_rate)
video_stream.width = screen_width
video_stream.height = screen_height

# Initialize audio stream writer
audio_stream = container.add_stream('aac', rate=sample_rate, layout='stereo')

# Define video capture thread function
def video_capture():
    # Initialize video capture device
    capture_device = av.open('desktop')
    capture_device.streams.video[0].thread_type = 'AUTO'
    
    # Capture video frames
    for frame in capture_device.decode(video=0):
        # Convert frame to numpy array
        img = frame.to_image()
        img = np.array(img)
        
        # Resize frame
        img = cv2.resize(img, (screen_width, screen_height))
        
        # Write frame to video stream
        frame = av.VideoFrame.from_ndarray(img, format='bgr24')
        packet = video_stream.encode(frame)
        container.mux(packet)

        # Exit loop if duration has elapsed
        if time.time() - start_time > duration:
            break

    # Close capture device and video stream writer
    capture_device.close()
    container.close()

# Define audio capture thread function
def audio_capture():
    # Initialize audio capture device
    capture_device = pa.open(format=pyaudio.paInt16,
                             channels=channels,
                             rate=sample_rate,
                             input=True,
                             frames_per_buffer=block_size)

    # Capture audio frames
    while True:
        data = capture_device.read(block_size)
        frame = av.AudioFrame.from_ndarray(data, format='s16', layout='stereo', rate=sample_rate)
        packet = audio_stream.encode(frame)
        container.mux(packet)

        # Exit loop if duration has elapsed
        if time.time() - start_time > duration:
            break

    # Close capture device
    capture_device.stop_stream()
    capture_device.close()

# Start recording
start_time = time.time()
video_thread = threading.Thread(target=video_capture)
audio_thread = threading.Thread(target=audio_capture)
video_thread.start()
audio_thread.start()

# Wait for recording to finish
video_thread.join()
audio_thread.join()

# Close PyAudio object
pa.terminate()

# Merge video and audio files
video_stream.close()
audio_stream.close()
container.close()

# Load video and audio files using MoviePy
video_clip = VideoFileClip('output.mp4')
audio_clip = AudioFileClip('output.aac')

# Combine video and audio files
final_clip = video_clip.set_audio(audio_clip)

# Write final video file to disk
final_clip.write_videofile("output_final.mp4", codec='libx264', audio_codec='aac')
