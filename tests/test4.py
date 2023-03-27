import socket
import numpy as np
import cv2

# Set up a socket to connect to the server
client_socket = socket.socket()
client_socket.connect(('10.100.102.50', 8000))
client_socket.settimeout(0.2)
print("connected")

try:
    while True:
        # Read the image data from the server
        image_data = b''
        while True:
            try:
                chunk = client_socket.recv(1024)
                image_data += chunk
            except:
                break

        with open("image.jpeg", "wb") as f:
            f.write(image_data)

        # Decode the image data as a NumPy array
        image_array = np.frombuffer(image_data, dtype=np.uint8)

        # Decode the NumPy array as an OpenCV image
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Display the image in a window
        cv2.imshow('Video', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    client_socket.close()
