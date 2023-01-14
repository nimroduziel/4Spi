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


class CarMovement:

    def __init__(self, buttons):
        self.right_speed = 0
        self.left_speed = 0
        self.buttons = buttons

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
        self.button_dict = {"speed": 0, "angle": 0, "rb": False, "lb": False, "exit": False}
        self.vid = cv2.VideoCapture(-1)

    def movement(self):

        sock = socket.socket()
        sock.bind(("0.0.0.0", BUTTONS_PORT))
        sock.listen(20)
        client_sock, addr = sock.accept()
        print("accepted movement")

        car_movement = CarMovement(self.button_dict)

        while not self.button_dict["exit"]:

            data = pickle.loads(client_sock.recv(1024))
            self.button_dict = data
            car_movement.buttons = data
            car_movement.to_string()
            car_movement.move_car()

        client_sock.close()

    def stream(self):
        """"
        sock = socket.socket()
        sock.bind(("0.0.0.0", 8000))
        sock.listen(20)
        cli_sock, addr = sock.accept()

        while not self.button_dict["exit"]:
            try:
                ret, frame = self.vid.read()
                print(f"old size: {frame.shape}")
                frame = cv2.GaussianBlur(frame, (15, 15), 0)
                print(f"new size: {frame.shape}")
                data = pickle.dumps(frame)

                chunk_size = 4096
                chunck_lst = []
                for i in range(0, len(data), chunk_size):
                    chunck_lst.append(data[i:i + chunk_size])

                cli_sock.send(len(data).to_bytes(3, 'big'))

                for i in chunck_lst:
                    cli_sock.send(i)
            except:
                break

        """
        BUFF_SIZE = 65536
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
        host_ip = '10.100.102.30'  # socket.gethostbyname(host_name)
        print(host_ip)
        port = 9999
        socket_address = (host_ip, port)
        server_socket.bind(socket_address)
        print('Listening at:', socket_address)

        fps, st, frames_to_count, cnt = (0, 0, 20, 0)

        while not self.button_dict["exit"]:
            msg, client_addr = server_socket.recvfrom(BUFF_SIZE)
            print('GOT connection from ', client_addr)
            WIDTH = 400
            while (self.vid.isOpened()):
                _, frame = self.vid.read()
                frame = imutils.resize(frame, width=WIDTH)
                encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                message = base64.b64encode(buffer)
                server_socket.sendto(message, client_addr)
                cnt += 1

        server_socket.close()
        self.vid.release()

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

        while not self.button_dict["exit"]:
            # Read audio data from the microphone
            data = stream.read(chunk)
            # Send the audio data to the server
            client_sock.send(data)
            #print(f"sent chunk: {len(data)}")

        stream.stop_stream()
        stream.close()
        p.terminate()

    def start_threads(self):
        movement_thread = threading.Thread(target=self.movement, args=())
        stream_thread = threading.Thread(target=self.stream, args=())
        sound_stream_thread = threading.Thread(target=self.sound_stream, args=())

        movement_thread.start()
        stream_thread.start()
        sound_stream_thread.start()

        movement_thread.join()
        stream_thread.join()
        sound_stream_thread.join()

    def registration(self):
        # connect to server
        # registretion
        pass


def main():

    car = Car()
    car.registration()
    car.start_threads()

    GPIO.cleanup()
    print("GPIO Clean up")


if __name__ == '__main__':
    main()
