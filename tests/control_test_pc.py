import math
import time
import threading

import pyaudio
import pygame
from pygame.locals import *
import socket
import pickle
import cv2
from datetime import datetime

movement_input_dict = {"speed": 0, "angle": 0, "rb": False, "lb": False, "exit": False}
movement_input_dict_copy = movement_input_dict.copy()

ip_to_send = "10.100.102.30"

PORT = 5000
BUTTONS_PORT = 5001
SOUND_PORT = 5002
STREAM_PORT = 8000


sock = socket.socket()
sock.connect((ip_to_send, BUTTONS_PORT))
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
    sock.connect((ip_to_send, STREAM_PORT))

    data = b''
    new = True
    image_size = 0
    at_start = True
    i = 0

    while not movement_input_dict["exit"]:

        if data != b'' and at_start:
            cv2.namedWindow("image", cv2.WINDOW_NORMAL)
            widht = 1920
            height = 1080
            cv2.resizeWindow("image", widht, height)
            cv2.moveWindow("image", 0, 0)
            at_start = False

        data += sock.recv(4096)
        if new and data != b'':
            image_size = int.from_bytes(data[:3], 'big')
            data = data[3:]
            new = False
            # print(f"image_size: {image_size}")

        if len(data) >= image_size != 0:
            # print(len(data[:image_size]))

            image = pickle.loads(data[:image_size])
            # for pygame
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
                print(f"{dt_string}.jpg")
                print("saved image")

            if key_input == 27:  # if self.exit
                break

            data = data[image_size:]
            new = True

    cv2.destroyAllWindows()


def sound_stream():
    sock = socket.socket()
    sock.connect((ip_to_send, SOUND_PORT))

    print("sound started")

    chunk = 1024
    format = pyaudio.paInt16
    channels = 2
    rate = 44100

    p = pyaudio.PyAudio()
    p.get_default_output_device_info()

    audio_stream = p.open(format=format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk)

    print("waiting")

    while not movement_input_dict["exit"]:
        try:
            data = sock.recv(chunk)
            # Output the audio data to the speakers
            audio_stream.write(data)

        except Exception as e:
            pass
            #print(f"audio problem: {e}")


stream_thread = threading.Thread(target=stream, args=())
sound_stream_thread = threading.Thread(target=sound_stream, args=())

stream_thread.start()
sound_stream_thread.start()


while not movement_input_dict["exit"]:
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
                movement_input_dict["exit"] = True
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

    #print(movement_input_dict.values() != movement_input_dict_copy.values())
    if movement_input_dict != movement_input_dict_copy:
        print(f"sent:{movement_input_dict}")
        sock.send(pickle.dumps(movement_input_dict))
        time.sleep(0.1)
        movement_input_dict_copy = movement_input_dict.copy()
