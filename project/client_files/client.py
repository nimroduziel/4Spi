import pygame
import socket
import rsa
import pickle

import math
import threading
import time

import pyaudio
from pygame.locals import *

import cv2
import numpy as np
import base64

import sys

pygame.init()

pygame.joystick.init()

screen = pygame.display.set_mode((640, 480))


sign_font = pygame.font.Font('freesansbold.ttf', 32)

SERVER_IP = "127.0.0.1"  # change after in amazon


exit_session = False


class Graphics:
    def __init__(self):
        self.screen = pygame.display.set_mode((600, 500))

    def restart(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((600, 500))

    def change_screen(self, width, height):
        self.screen = pygame.display.set_mode((width, height))

    def sign_screen(self, username, password, user_input_rect, pass_input_rect):
        self.screen.fill((0, 0, 0))

        user_text = sign_font.render('username:', True, (255, 255, 255), (0, 0, 0))
        user_textRect = user_text.get_rect()
        user_textRect.center = (100, 50)

        pass_text = sign_font.render('password:', True, (255, 255, 255), (0, 0, 0))
        pass_textRect = user_text.get_rect()
        pass_textRect.center = (100, 100)

        user_input_text = sign_font.render(username, True, (255, 255, 255), (0, 0, 0))
        user_input_text_textRect = user_text.get_rect()
        user_input_text_textRect.center = (280, 50)

        pass_input_text = sign_font.render(password, True, (255, 255, 255), (0, 0, 0))
        pass_input_textRect = user_text.get_rect()
        pass_input_textRect.center = (280, 100)

        self.screen.blit(user_text, user_textRect)
        self.screen.blit(pass_text, pass_textRect)
        pygame.draw.rect(self.screen, (255, 255, 255), user_input_rect, True, 5)
        pygame.draw.rect(self.screen, (255, 255, 255), pass_input_rect, True, 5)
        self.screen.blit(user_input_text, user_input_text_textRect)
        self.screen.blit(pass_input_text, pass_input_textRect)

    def draw_sign_rects(self, sign_up_rect, sign_in_rect, reason):
        up_text = sign_font.render('sign up', True, (255, 255, 255), (0, 0, 0))
        up_textRect = up_text.get_rect()
        up_textRect.center = (150, 275)

        in_text = sign_font.render('sign in', True, (255, 255, 255), (0, 0, 0))
        in_textRect = in_text.get_rect()
        in_textRect.center = (450, 275)

        reason_text = sign_font.render(reason, True, (255, 255, 255), (0, 0, 0))
        reason_textRect = reason_text.get_rect()
        reason_textRect.center = (300, 200)

        pygame.draw.rect(self.screen, (255, 255, 255), sign_up_rect, True, 10)
        pygame.draw.rect(self.screen, (255, 255, 255), sign_in_rect, True, 10)
        self.screen.blit(up_text, up_textRect)
        self.screen.blit(in_text, in_textRect)
        self.screen.blit(reason_text, reason_textRect)

    def draw_choise_rects(self, view_cars_rect, new_car_rect, videos_rect):
        self.screen.fill((0, 0, 0))

        pygame.draw.rect(self.screen, (255, 255, 255), view_cars_rect, True, 10)
        pygame.draw.rect(self.screen, (255, 255, 255), new_car_rect, True, 10)
        pygame.draw.rect(self.screen, (255, 255, 255), videos_rect, True, 10)

        view_cars = sign_font.render("View Your Cars", True, (255, 255, 255), (0, 0, 0))
        view_carsRect = view_cars.get_rect()
        view_carsRect.center = (300, 90)

        new_car = sign_font.render("Add Car", True, (255, 255, 255), (0, 0, 0))
        new_carRect = new_car.get_rect()
        new_carRect.center = (300, 240)

        videos = sign_font.render("View Videos", True, (255, 255, 255), (0, 0, 0))
        videosRect = videos.get_rect()
        videosRect.center = (300, 390)

        self.screen.blit(view_cars, view_carsRect)
        self.screen.blit(new_car, new_carRect)
        self.screen.blit(videos, videosRect)

    def draw_cars(self, cars):
        self.screen.fill((0, 0, 0))
        red = (200, 50, 50)
        green = (50, 200, 50)
        color = green
        divider = 500 / len(cars)
        x = 300
        y = divider

        for car in cars:
            if car[3] == "offline":
                color = red
            car = sign_font.render(f"{car[2]}", True, color, (0, 0, 0))
            carsRect = car.get_rect()
            carsRect.center = (x, (y + y-divider)/2)

            self.screen.blit(car, carsRect)
            if y != 0 and y != 500:
                pygame.draw.line(self.screen, (255, 255, 255), (0, y), (600, y), 5)

            y += divider
            color = green

    def draw_add_car_rects(self, name_rect, id_rect, send_button_rect, name, id):
        self.screen.fill((0, 0, 0))
        
        car_name = sign_font.render("Car Name: ", True, (255, 255, 255), (0, 0, 0))
        car_nameRect = car_name.get_rect()
        car_nameRect.center = (100, 50)

        car_id = sign_font.render("Car ID: ", True, (255, 255, 255), (0, 0, 0))
        car_idRect = car_id.get_rect()
        car_idRect.center = (100, 121)
        
        send = sign_font.render("Send", True, (255, 255, 255), (0, 0, 0))
        sendRect = send.get_rect()
        sendRect.center = (300, 370)
        
        name_text = sign_font.render(name, True, (255, 255, 255), (0, 0, 0))
        name_text_textRect = name_text.get_rect()
        name_text_textRect.center = (210, 50)

        id_text = sign_font.render(id, True, (255, 255, 255), (0, 0, 0))
        id_text_textRect = id_text.get_rect()
        id_text_textRect.center = (210, 121)
        
        self.screen.blit(car_name, car_nameRect)
        self.screen.blit(car_id, car_idRect)
        self.screen.blit(send, sendRect)
        pygame.draw.rect(self.screen, (255, 255, 255), name_rect, True, 10)
        pygame.draw.rect(self.screen, (255, 255, 255), id_rect, True, 10)
        pygame.draw.rect(self.screen, (255, 255, 255), send_button_rect, True, 10)
        self.screen.blit(name_text, name_text_textRect)
        self.screen.blit(id_text, id_text_textRect)

    def draw_return(self, ret_rect):
        ret = sign_font.render("return", True, (255, 255, 255), (0, 0, 0))
        ret_text_Rect = ret.get_rect()
        ret_text_Rect.center = (50, 475)

        pygame.draw.rect(self.screen, (255, 255, 255), ret_rect, True, 10)
        self.screen.blit(ret, ret_text_Rect)


def sign(sock, encryption_key):
    running = True
    username = ""
    password = ""
    to_change = ""
    to_send = ""
    reason = ""

    user_input_rect = pygame.Rect(190, 30, 410, 42)
    pass_input_rect = pygame.Rect(190, 80, 410, 42)
    sign_up_rect = pygame.Rect(50, 200, 200, 150)
    sign_in_rect = pygame.Rect(350, 200, 200, 150)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            elif event.type == pygame.MOUSEBUTTONDOWN and to_send == "":

                if user_input_rect.collidepoint(event.pos):
                    to_change = "username"
                elif pass_input_rect.collidepoint(event.pos):
                    to_change = "password"
                elif sign_up_rect.collidepoint(event.pos):
                    to_send = "SNUP"
                elif sign_in_rect.collidepoint(event.pos):
                    to_send = "SNIN"
                else:
                    to_change = ""

            elif event.type == pygame.KEYDOWN and to_send == "":
                if event.key == pygame.K_BACKSPACE:
                    if to_change == "username":
                        username = username[:-1]
                    elif to_change == "password":
                        password = password[:-1]
                else:
                    if to_change == "username":
                        username += event.unicode
                    elif to_change == "password":
                        password += event.unicode

        if to_send != "":
            sock.send(rsa.encrypt(f"{to_send}~{username}~{password}".encode(), encryption_key))
            ans = sock.recv(1024).decode()
            if ans == "GOOD":
                return 2
            else:
                reason = ans.split("~")[1]
                to_send = ""
                password = ""

        graphics.sign_screen(username, password, user_input_rect, pass_input_rect)
        graphics.draw_sign_rects(sign_up_rect, sign_in_rect, reason)
        pygame.display.flip()


def view_cars(sock):
    cars = pickle.loads(sock.recv(1024))
    return_rect = pygame.Rect(0, 450, 100, 50)

    divider = 500/len(cars)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if return_rect.collidepoint(event.pos):
                    sock.send(b"BACK")
                    return 2
                chosen_car = int(event.pos[1]/divider)
                print(chosen_car)
                if cars[chosen_car][3] == "online":
                    sock.send(cars[chosen_car][1].encode())
                    return 6

        graphics.draw_cars(cars)
        graphics.draw_return(return_rect)
        pygame.display.flip()


def add_car(sock):
    to_send = False
    to_change = ""
    name = ""
    id = ""

    name_rect = pygame.Rect(200, 30, 400, 42)
    id_rect = pygame.Rect(200, 100, 400, 42)
    send_button = pygame.Rect(150, 280, 300, 180)
    return_rect = pygame.Rect(0, 450, 100, 50)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if return_rect.collidepoint(event.pos):
                    sock.send(b"BACK")
                    return 2
                elif name_rect.collidepoint(event.pos):
                    to_change = "name"
                elif id_rect.collidepoint(event.pos):
                    to_change = "id"
                elif send_button.collidepoint(event.pos):
                    to_send = True
                else:
                    to_change = ""

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if to_change == "name":
                        name = name[:-1]
                    elif to_change == "id":
                        id = id[:-1]
                else:
                    if to_change == "name":
                        name += event.unicode
                    elif to_change == "id":
                        id += event.unicode

        if to_send:
            sock.send(f"{id}~{name}".encode())
            ans = sock.recv(1024).decode()
            if ans == "GOOD":
                return 2
            else:
                id = ""
            to_send = False

        graphics.draw_add_car_rects(name_rect, id_rect, send_button, name, id)
        graphics.draw_return(return_rect)
        pygame.display.flip()


def view_vids(sock):
    pass


def choose_screen(sock):
    view_cars_rect = pygame.Rect(100, 50, 400, 80)
    new_car_rect = pygame.Rect(100, 200, 400, 80)
    videos_rect = pygame.Rect(100, 350, 400, 80)

    to_send = ""

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if view_cars_rect.collidepoint(event.pos):
                    sock.send(b"VCAR")
                    return 3

                elif new_car_rect.collidepoint(event.pos):
                    sock.send(b"NCAR")
                    return 4

                elif videos_rect.collidepoint(event.pos):
                    sock.send(b"VDEO")
                    return 5

        graphics.draw_choise_rects(view_cars_rect, new_car_rect, videos_rect)
        pygame.display.flip()

    return 0


def calc_angle(x, y):
    try:
        angle = math.degrees(math.asin(x/y))

        if angle * x < 0:
            angle = -angle
    except:
        angle = math.degrees(math.asin(x))

    return angle


def movement(sock):
    global exit_session

    pygame.init()

    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        print(joystick.get_name())

    movement_input_dict = {"speed": 0, "angle": 0, "rb": False, "lb": False, "exit": False}
    movement_input_dict_copy = movement_input_dict.copy()
    print("started movement")

    right_val = 0
    left_val = 0

    y_axis_val = 0
    x_axis_val = 0

    while not exit_session:
        pygame.event.pump()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass
            elif event.type == JOYAXISMOTION:
                if event.axis == 5:
                    right_val = int((event.value * 100 + 100) / 2)

                elif event.axis == 4:
                    left_val = int((event.value * 100 + 100) / 2)

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
                if event.button == 4:
                    movement_input_dict["lb"] = True
                elif event.button == 5:
                    movement_input_dict["rb"] = True
                elif event.button == 7:
                    movement_input_dict["exit"] = True
                    exit_session = True

            elif event.type == JOYBUTTONUP:
                if event.button == 4:
                    movement_input_dict["lb"] = False
                elif event.button == 5:
                    movement_input_dict["rb"] = False

            elif event.type == JOYDEVICEADDED:
                joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
                for joystick in joysticks:
                    print(joystick.get_name())
            elif event.type == JOYDEVICEREMOVED:
                print("removed")
                joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

        if not joysticks:
            movement_input_dict["speed"] = 0

        if movement_input_dict != movement_input_dict_copy:
            print(f"sent:{movement_input_dict}, {joysticks}")
            sock.send(pickle.dumps(movement_input_dict))
            movement_input_dict_copy = movement_input_dict.copy()
            time.sleep(0.1)


def stream(stream_socket, stream_addr):
    global exit_session

    BUFF_SIZE = 65536
    fps, st, frames_to_count, cnt = (0, 0, 20, 0)

    cv2.namedWindow("RECEIVING VIDEO", cv2.WINDOW_NORMAL)
    widht = 1920
    height = 1080
    cv2.resizeWindow("RECEIVING VIDEO", widht, height)
    cv2.moveWindow("RECEIVING VIDEO", 0, 0)

    time.sleep(0.5)

    stream_socket.settimeout(0.5)

    try:
        while not exit_session:
            packet, _ = stream_socket.recvfrom(BUFF_SIZE)
            data = base64.b64decode(packet, ' /')
            npdata = np.fromstring(data, dtype=np.uint8)
            frame = cv2.imdecode(npdata, 1)
            frame = cv2.putText(frame, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("RECEIVING VIDEO", frame)
            key = cv2.waitKey(1) & 0xFF
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count / (time.time() - st))
                    st = time.time()
                    cnt = 0
                except:
                    pass
            cnt += 1
    except:
        exit_session = True

    stream_socket.close()
    cv2.destroyAllWindows()


def sound_stream():
    pass


def session(sock):
    global exit_session
    print("started session")
    BUFF_SIZE = 65536

    pygame.display.quit()

    exit_session = False

    # open all sockets and put them in a dictionary
    stream_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    stream_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

    stream_port = int(sock.recv(1024).decode())
    stream_addr = (SERVER_IP, stream_port)
    stream_socket.sendto(b"hello", stream_addr)

    # A for stream, B for movement, C for sound stream

    movement_thread = threading.Thread(target=movement, args=(sock,))
    stream_thread = threading.Thread(target=stream, args=(stream_socket, stream_addr))
    #sound_stream_thread = threading.Thread(target=sound_stream, args=())

    #movement_thread.start()
    stream_thread.start()
    #sound_stream_thread.start()

    #movement_thread.join()
    movement(sock)

    stream_thread.join()

    print("ended session")


graphics = Graphics()


def main():
    global graphics
    sock = socket.socket()
    sock.connect(("127.0.0.1", 9000))

    encryption_key = pickle.loads(sock.recv(1024))

    current_screen = 1

    while current_screen != 0:
        if current_screen == 1:
            current_screen = sign(sock, encryption_key)
        elif current_screen == 2:
            current_screen = choose_screen(sock)
        elif current_screen == 3:
            current_screen = view_cars(sock)
        elif current_screen == 4:
            current_screen = add_car(sock)
        elif current_screen == 5:
            current_screen = view_vids(sock)
        elif current_screen == 6:
            session(sock)
            graphics.restart()
            current_screen = 3
        print(current_screen)

    sock.send(b"EXIT")
    print("exited")
    sock.close()


if __name__ == '__main__':
    main()
