import pyaudio
import socket

print('started audio stream')
sock = socket.socket()
sock.bind(("0.0.0.0", 8000))
sock.listen(20)
client_sock, addr = sock.accept()
print("accepted")

chunk = 1024
format = pyaudio.paInt16
channels = 2
rate = 44100

p = pyaudio.PyAudio()
p.get_default_input_device_info()
stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

print("* streaming audio")

while True:
    # Read audio data from the microphone
    data = stream.read(chunk)
    # Send the audio data to the server
    client_sock.send(data)
    print("Sending")
    # print(f"sent chunk: {len(data)}")

stream.stop_stream()
stream.close()
p.terminate()