import numpy as np
import cv2
import pyautogui
import pyaudio
import PIL

# Set the video codec and output file name
codec = cv2.VideoWriter_fourcc(*"XVID")
output_file = "output.avi"

# Set the screen size and FPS
screen_size = (1920, 1080)
fps = 30.0

# Set the audio parameters
audio_format = pyaudio.paInt16
audio_channels = 1
audio_rate = 44100
audio_chunk = 1024

# Create the video writer object
video_writer = cv2.VideoWriter(output_file, codec, fps, screen_size)

# Create the audio stream object
try:
    audio_stream = pyaudio.PyAudio().open(
        format=audio_format,
        channels=audio_channels,
        rate=audio_rate,
        input=True,
        frames_per_buffer=audio_chunk
    )
except Exception as e:
    print("Error opening audio stream:", e)
    audio_stream = None

# Start recording
while True:
    # Capture the screen
    screenshot = pyautogui.screenshot()

    # Convert the screenshot to a numpy array
    frame = np.array(screenshot)

    # Convert the color format from BGR to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Write the frame to the video
    video_writer.write(frame)

    # Check if audio stream is valid and read audio frames
    if audio_stream:
        try:
            audio_frames = audio_stream.read(audio_chunk)
        except Exception as e:
            print("Error reading audio frames:", e)
            audio_frames = None
    else:
        audio_frames = None

    # Write audio frames to the video file
    if audio_frames is not None:
        try:
            video_writer.write(np.frombuffer(audio_frames, dtype=np.int16).reshape(-1, 1))
        except Exception as e:
            print("Error writing audio frames:", e)

    # Break the loop if the user presses the 'q' key
    if cv2.waitKey(1) == ord("q"):
        break

# Release the video writer and audio stream objects, and destroy all windows
video_writer.release()
if audio_stream:
    audio_stream.stop_stream()
    audio_stream.close()
    pyaudio.PyAudio().terminate()
cv2.destroyAllWindows()