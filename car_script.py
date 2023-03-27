import math
import time

import RPi.GPIO as GPIO
import socket
import threading
import pickle
import cv2
import pyaudio

import imutils
import numpy as np
import base64


PORT = 5000
BUTTONS_PORT = 5001
SOUND_PORT = 5002
STREAM_PORT = 8000

GPIO.setmode(GPIO.BCM)

MOTOR1A = 24
MOTOR1B = 23
MOTOR1E = 25

MOTOR2A = 27
MOTOR2B = 4
MOTOR2E = 22


# left motor
GPIO.setup(MOTOR1A, GPIO.OUT)
GPIO.setup(MOTOR1B, GPIO.OUT)
GPIO.setup(MOTOR1E, GPIO.OUT)

# right motor
GPIO.setup(MOTOR2A, GPIO.OUT)
GPIO.setup(MOTOR2B, GPIO.OUT)
GPIO.setup(MOTOR2E, GPIO.OUT)

# left
p = GPIO.PWM(MOTOR1E, 2000)

# right
p2 = GPIO.PWM(MOTOR2E, 2000)

p.start(0)
p2.start(0)

SERVER_IP = "10.100.102.62"


class CarMovement:

    def __init__(self):
        self.right_speed = 0
        self.left_speed = 0
        self.buttons = {"speed": 0, "angle": 0, "rb": False, "lb": False, "exit": False}

    def calc_spins(self):
        self.right_speed = self.buttons['speed']
        self.left_speed = self.buttons['speed']

        if not self.buttons['rb'] and not self.buttons['lb']:
            if self.buttons['angle'] > 0:
                self.right_speed = self.buttons['speed'] * math.cos(math.radians(self.buttons['angle']))

            elif self.buttons['angle'] < 0:
                self.left_speed = self.buttons['speed'] * math.cos(math.radians(self.buttons['angle']))

        elif self.buttons['rb'] and not self.buttons['lb'] and self.buttons['speed'] > 0:
            self.right_speed = - self.right_speed

        elif self.buttons['lb'] and not self.buttons['rb'] and self.buttons['speed'] < 0:
            self.right_speed = - self.right_speed

        if self.buttons['speed'] < 0 and not self.buttons['lb']:
            self.right_speed, self.left_speed = self.left_speed, self.right_speed

    def change_left(self):
        if self.left_speed > 0:
            GPIO.output(MOTOR1A, GPIO.HIGH)
            GPIO.output(MOTOR1B, GPIO.LOW)
            GPIO.output(MOTOR1E, GPIO.HIGH)

        elif self.left_speed < 0:
            GPIO.output(MOTOR1A, GPIO.LOW)
            GPIO.output(MOTOR1B, GPIO.HIGH)
            GPIO.output(MOTOR1E, GPIO.HIGH)

        else:
            GPIO.output(MOTOR1A, GPIO.LOW)
            GPIO.output(MOTOR1B, GPIO.LOW)
            GPIO.output(MOTOR1E, GPIO.HIGH)

    def change_right(self):
        if self.right_speed > 0:
            GPIO.output(MOTOR2A, GPIO.HIGH)
            GPIO.output(MOTOR2B, GPIO.LOW)
            GPIO.output(MOTOR2E, GPIO.HIGH)

        elif self.right_speed < 0:
            GPIO.output(MOTOR2A, GPIO.LOW)
            GPIO.output(MOTOR2B, GPIO.HIGH)
            GPIO.output(MOTOR2E, GPIO.HIGH)

        else:
            GPIO.output(MOTOR2A, GPIO.LOW)
            GPIO.output(MOTOR2B, GPIO.LOW)
            GPIO.output(MOTOR2E, GPIO.HIGH)

    def move_car(self):
        self.calc_spins()
        self.change_left()
        self.change_right()

        print(f"left: {self.left_speed}, right: {self.right_speed}")
        p.ChangeDutyCycle(abs(self.left_speed))
        p2.ChangeDutyCycle(abs(self.right_speed))

    def to_string(self):
        print(f"speed: {self.buttons['speed']}, angle: {self.buttons['angle']}, right_speed: {self.right_speed}, "
              f"left_speed: {self.left_speed}, rb: {self.buttons['rb']}, lb: {self.buttons['lb']}, "
              f"exit: {self.buttons['exit']}")


class Car:
    def __init__(self):
        self.car_movement = CarMovement()
        self.vid = cv2.VideoCapture(-1)
        self.main_sock = socket.socket()
        self.main_sock.connect((SERVER_IP, 8000))

    def movement(self):

        sock = socket.socket()
        sock.bind(("0.0.0.0", BUTTONS_PORT))
        sock.listen(20)
        client_sock, addr = sock.accept()
        print("accepted movement")

        while not self.car_movement.buttons["exit"]:
            try:
                data = pickle.loads(client_sock.recv(1024))
                self.car_movement.buttons = data
            except:
                print("failed")

            self.car_movement.to_string()
            self.car_movement.move_car()

        client_sock.close()

    def stream(self, stream_socket, stream_addr):
        BUFF_SIZE = 65536

        fps, st, frames_to_count, cnt = (0, 0, 20, 0)

        WIDTH = 400
        while not self.car_movement.buttons["exit"]:
            _, frame = self.vid.read()
            frame = imutils.resize(frame, width=WIDTH)
            encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)
            stream_socket.sendto(message, stream_addr)
            cnt += 1

        server_socket.close()
        self.vid.release()
        print("stream ended")

    def sound_stream(self):
        print('started audio stream')
        sock = socket.socket()
        sock.bind(("0.0.0.0", SOUND_PORT))
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

        while not self.car_movement.buttons["exit"]:
            # Read audio data from the microphone
            data = stream.read(chunk)
            # Send the audio data to the server
            client_sock.send(data)
            #print(f"sent chunk: {len(data)}")

        stream.stop_stream()
        stream.close()
        p.terminate()

    def start_threads(self):

        stream_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        stream_port = int(sock.recv(1024).decode())
        stream_addr = (SERVER_IP, stream_port)
        stream_socket.sendto(b"hello", stream_addr)

        movement_thread = threading.Thread(target=self.movement, args=())
        stream_thread = threading.Thread(target=self.stream, args=())
        sound_stream_thread = threading.Thread(target=self.sound_stream, args=(stream_socket, stream_addr))

        movement_thread.start()
        stream_thread.start()
        sound_stream_thread.start()

        movement_thread.join()
        stream_thread.join()
        sound_stream_thread.join()

    def registration(self):
        # connect to server
        # registretion
        with open("id.txt", "r") as f:
            self.main_sock.send(f.read().encode())

        ans = self.main_sock.recv(1024).decode()
        if ans == "accepted":
            return True
        else:
            return False


def main():

    car = Car()
    if car.registration():
        car.start_threads()

    GPIO.cleanup()
    print("GPIO Clean up")


if __name__ == '__main__':
    main()
