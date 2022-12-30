import math
import time

import RPi.GPIO as GPIO
import socket
import threading
import pickle
import cv2
import subprocess

PORT = 5000
MOVEMENT_PORT = 5001
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

    def __init__(self):
        self.speed = 0
        self.angle = 0
        self.right_speed = 0
        self.left_speed = 0
        self.rb = False
        self.lb = False

    def calc_spins(self):
        self.right_speed = self.speed
        self.left_speed = self.speed

        if not self.rb and not self.lb:
            if self.angle > 0:
                self.right_speed = self.speed * math.cos(math.radians(self.angle))

            elif self.angle < 0:
                self.left_speed = self.speed * math.cos(math.radians(self.angle))

        elif self.rb and not self.lb and self.speed > 0:
            self.right_speed = - self.right_speed

        elif self.lb and not self.rb and self.speed < 0:
            self.right_speed = - self.right_speed

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

        p.ChangeDutyCycle(abs(self.left_speed))
        p2.ChangeDutyCycle(abs(self.right_speed))


class Car:
    def __init__(self):
        pass

    def movement(self):
        movement = CarMovement()

        sock = socket.socket()
        sock.bind(("0.0.0.0", MOVEMENT_PORT))
        sock.listen(20)
        client_sock, addr = sock.accept()

        while True:
            try:
                data = pickle.loads(client_sock.recv(1024))

                movement.speed = data["speed"]
                movement.angle = data["angle"]
                movement.rb = data["rb"]
                movement.lb = data["lb"]

                movement.move_car()

            except Exception as e:
                print(e)
                break

        client_sock.close()
        sock.close()

    def stream(self):
        sock = socket.socket()
        sock.connect(("10.100.102.8", STREAM_PORT))

        vid = cv2.VideoCapture(0)

        while True:
            ret, frame = vid.read()

            cv2.imwrite("image_copy.jpg", frame) # a lot of time, need to change

            with open("image_copy.jpg", "rb") as f:
                data = f.read()

            chunk_size = 4096
            chunck_lst = []
            for i in range(0, len(data), chunk_size):
                chunck_lst.append(data[i:i + chunk_size])

            print(len(chunck_lst))
            sock.send(len(data).to_bytes(3, 'big'))
            print(f"sent: {len(data)}")

            for i in chunck_lst:
                sock.send(i)
            print("sent")

    def sound(self):
        sock = socket.socket()
        sock.bind(("0.0.0.0", SOUND_PORT))
        sock.listen(20)
        client_sock, addr = sock.accept()

    def start_threads(self):
        movement_thread = threading.Thread(target=self.movement, args=())
        stream_thread = threading.Thread(target=self.stream, args=())
        sound_thread = threading.Thread(target=self.sound, args=())

        movement_thread.start()
        stream_thread.start()
        #sound_thread.start()

        movement_thread.join()
        stream_thread.join()
        #sound_thread.join()

    def registration(self):
        # connect to server
        # registretion
        pass

    def close(self):
        # close all threads
        pass


def main():

    car = Car()
    car.registration()
    car.start_threads()

    GPIO.cleanup()
    print("GPIO Clean up")


if __name__ == '__main__':
    main()
