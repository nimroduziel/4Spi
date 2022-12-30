import socket
import pygame
import cv2
import pickle
from datetime import datetime

sock = socket.socket()
sock.bind(("0.0.0.0", 4004))
sock.listen(20)
cli_sock, addr = sock.accept()

"""
pygame.init()

window_size = (640, 480)

screen = pygame.display.set_mode(window_size)
"""

data = b''
running = True
new = True
image_size = 0
at_start = True
i = 0

while running:
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    """
    if data != b'' and at_start:
        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        widht = 1920
        height = 1080
        cv2.resizeWindow("image", widht, height)
        cv2.moveWindow("image", 0, 0)
        at_start = False

    data += cli_sock.recv(4096)
    if new and data != b'':
        image_size = int.from_bytes(data[:3], 'big')
        data = data[3:]
        new = False
        # print(f"image_size: {image_size}")

    if len(data) >= image_size != 0:
        # print(len(data[:image_size]))

        image = pickle.loads(data[:image_size])
        # for pygame
        """
        cv2.imwrite("image.jpg", image)
        image = pygame.image.load("image.jpg")
        screen.blit(image, (0, 0))
        pygame.display.flip()
        """
        cv2.imshow("image", image)

        key_input = cv2.waitKey(1)
        if key_input != -1:
            print(key_input)

        if key_input == ord('q'):  # if self.x
            i += 1
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y %H-%M-%S")
            print(dt_string)
            cv2.imwrite(f"{dt_string}.jpg", image)
            print(f"{dt_string }.jpg")
            print("saved image")

        if key_input == 27:  # if self.exit
            break

        data = data[image_size:]
        new = True

cv2.destroyAllWindows()

