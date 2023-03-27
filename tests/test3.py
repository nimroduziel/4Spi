import socket
import io
import picamera

# Set up a socket to listen for connections
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)


camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
stream = io.BytesIO()

print("camera ready")

# Continuously capture frames and send them to the client
for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
    # Reset the stream position to the beginning
    stream.seek(0)

    # Read the image data from the stream
    image_data = stream.read()
    print("got image")

    # Send the image data to the client
    connection = server_socket.accept()[0]
    print(connection)
    print("connected")
    connection.sendall(image_data)

    # Reset the stream for the next frame
    stream.seek(0)
    stream.truncate()