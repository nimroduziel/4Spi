import socket
import pyaudio

sock = socket.socket()
sock.connect(("10.100.102.8", 8000))

print("sound started")

chunk = 1024
format = pyaudio.paInt16
channels = 2
rate = 44100

p = pyaudio.PyAudio()

audio_stream = p.open(format=format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk)

print("waiting")

while True:
    try:
        data = sock.recv(chunk)
        print(f"recived: {len(data)}")
        # Output the audio data to the speakers
        audio_stream.write(data)

    except Exception as e:
        pass
        print(f"audio problem: {e}")