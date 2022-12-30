import math
import time
import threading
import pygame
from pygame.locals import *
import socket
import pickle
import subprocess


movement_input_dict = {"speed": 0, "angle": 0, "rb": False, "lb": False}

port_to_send = 5001
ip_to_send = "10.100.102.30"

sock = socket.socket()
sock.connect((ip_to_send, port_to_send))
run = True

pygame.init()

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print(joystick.get_name())


right_val = 0
left_val = 0

y_axis_val = 0
x_axis_val = 0


def calc_angle(x, y):

    try:
        angle = math.degrees(math.asin(x/y))

        if angle * x < 0:
            angle = -angle
    except:
        angle = math.degrees(math.asin(x))

    return angle


def stream():
    sock = socket.socket()
    sock.bind(("0.0.0.0", 8000))
    sock.listen(20)
    cli_sock, addr = sock.accept()

    pygame.init()

    window_size = (640, 480)

    data = b''
    screen = pygame.display.set_mode(window_size)
    running = True
    new = True
    image_size = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        data += cli_sock.recv(4096)
        if new and data != b'':
            image_size = int.from_bytes(data[:3], 'big')
            data = data[3:]
            new = False
            print(f"image_size: {image_size}")

        if len(data) >= image_size != 0:
            print(len(data))
            print("image")
            with open("image.jpg", "wb") as f:
                f.write(data[:image_size])
            data = data[image_size:]
            new = True

            image = pygame.image.load("image.jpg")
            screen.blit(image, (0, 0))
            pygame.display.flip()


stream_thread = threading.Thread(target=stream, args=())
stream_thread.start()


while run:
    for event in pygame.event.get():
        if event.type == JOYAXISMOTION:
            if event.axis == 5:
                right_val = int((event.value * 100 + 100)/2)

            elif event.axis == 4:
                left_val = int((event.value * 100 + 100)/2)

            elif event.axis == 0:
                if abs(event.value) > 0.1:
                    if event.value > 1:
                        x_axis_val = 1
                    elif event.value < -1:
                        x_axis_val = -1
                    else:
                        x_axis_val = event.value
                else:
                    x_axis_val = 0
            elif event.axis == 1:
                if event.value < 0 and abs(event.value) > 0.1:
                    if event.value > 1:
                        y_axis_val = 1
                    elif event.value < -1:
                        y_axis_val = -1
                    else:
                        y_axis_val = event.value
                else:
                    y_axis_val = 0
                y_axis_val = y_axis_val * -1

            movement_input_dict["angle"] = int(calc_angle(x_axis_val, y_axis_val))
            movement_input_dict["speed"] = (right_val - left_val)

        elif event.type == JOYBUTTONDOWN:
            if event.button == 0:
                buttons.a = True
            elif event.button == 1:
                buttons.b = True
            elif event.button == 2:
                buttons.x = True
            elif event.button == 3:
                buttons.y = True
            elif event.button == 4:
                movement_input_dict["lb"] = True
            elif event.button == 5:
                movement_input_dict["rb"] = True
            elif event.button == 7:
                buttons.exit = True
                run = False
                pygame.quit()

        elif event.type == JOYBUTTONUP:
            if event.button == 0:
                buttons.a = False
            elif event.button == 1:
                buttons.b = False
            elif event.button == 2:
                buttons.x = False
            elif event.button == 3:
                buttons.y = False
            elif event.button == 4:
                movement_input_dict["lb"] = False
            elif event.button == 5:
                movement_input_dict["rb"] = False

        elif event.type == JOYDEVICEADDED:
            joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            for joystick in joysticks:
                print(joystick.get_name())
        elif event.type == JOYDEVICEREMOVED:
            joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

    #print(movement_input_dict)
    sock.send(pickle.dumps(movement_input_dict))
    time.sleep(0.1)
