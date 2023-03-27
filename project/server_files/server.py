import random
import threading
import socket
from car_client_classes import *
import time
import hashlib
import rsa
import pickle
import secrets


DB = CarClientORM()
lock = threading.Lock()

session_dict = {}

publickey, privatekey = rsa.newkeys(1024)

cars_dict = {}
clients_dict = {}

taken_port_list = []


def accept_car(sock):
    ID = sock.recv(1024).decode()
    accepted = False
    lock.acquire()

    if ID in DB.get_IDs():
        DB.change_state(ID, "online")
        accepted = True

    lock.release()
    return accepted, ID


def handle_car(sock):
    global session_dict

    accepted, id = accept_car(sock)
    if not accepted:
        sock.send(b"not accepted")
        return
    sock.send(b"accepted")

    lock.acquire()
    session_dict[id] = False
    lock.release()

    while True:  # waiting for client to connect
        if session_dict[id]:
            car_session(sock, id)
            session_dict[id] = False


def sign(sock):
    done = False
    username = ""
    while not done:

        data = sock.recv(1024)
        if data == b"EXIT":
            return False, username

        data = rsa.decrypt(data, privatekey).decode().split("~")
        action = data[0]

        lock.acquire()
        if action == "SNUP":
            username = data[1]
            password = data[2]

            if username in DB.get_usernames():
                sock.send(b"NGOD~username taken")
            else:
                salt = secrets.token_hex(8)
                hashed_password = hashlib.sha256((password+salt).encode()).hexdigest()
                new_client = Client(username, salt, hashed_password)
                DB.insert_user(new_client)
                sock.send(b"GOOD")
                done = True

        elif action == "SNIN":
            username = data[1]
            password = data[2]

            try:
                data = DB.get_user_by_username(username)
                if data[2] == hashlib.sha256((password + data[1]).encode()).hexdigest():
                    sock.send(b"GOOD")
                    done = True
                else:
                    sock.send(b"NGOD~wrong password")
            except:
                sock.send(b"NGOD~username does not exit")

        lock.release()

    return True, username


def open_udp_sock():
    global taken_port_list

    udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    random_port = random.randint(1000, 6000)
    while random_port in taken_port_list:
        random_port = random.randint(1000, 6000)

    udp_socket.bind(("0.0.0.0", random_port))

    lock.acquire()
    taken_port_list.append(random_port)
    lock.release()

    return udp_socket, random_port


def send_data_car(id, tcp_sock, udp_sock, addr):
    while session_dict[id]:
        if cars_dict[id]:
            data_lst = cars_dict[id]
            lock.acquire()
            cars_dict[id] = []
            lock.release()

            for message in data_lst:
                print(message[0])   # if A in data then stream, else: tcp socket.
                if message[0].decode() == "A":
                    udp_sock.sendto(message[1:], addr)
                else:
                    tcp_sock.send(message)


def send_data_client(id, tcp_sock, udp_sock, addr):
    while session_dict[id]:
        if clients_dict[id]:
            data_lst = clients_dict[id]
            lock.acquire()
            clients_dict[id] = []
            lock.release()

            for message in data_lst:
                print(message[0])   # if A in data then stream, else: tcp socket.
                if message[0].decode() == "A":
                    udp_sock.sendto(message[1:], addr)
                else:
                    tcp_sock.send(message)


def recv_stream_car(id, udp_socket, addr):
    global clients_dict
    BUFF_SIZE = 65536

    while session_dict[id]:
        data = udp_socket.recvfrom(BUFF_SIZE)
        lock.acquire()
        clients_dict[id].append(b"A" + data)
        lock.release()


def recv_data_car(id, tcp_sock):
    global clients_dict
    while session_dict[id]:
        data = tcp_sock.recv(1024)
        lock.acquire()
        clients_dict[id].append(data)
        lock.release()


def car_session(car_sock, id):
    global clients_dict

    udp_socket, port = open_udp_sock()
    car_sock.send(str(port).encode())

    data, addr = udp_socket.recvfrom(1024)

    clients_dict[id] = []

    send_thread = threading.Thread(target=send_data_car, args=(id, car_sock, udp_socket, addr))
    recv_stream_thread = threading.Thread(target=recv_stream_car, args=(id, udp_socket, addr))
    recv_data_thread = threading.Thread(target=recv_data_car, args=(id, car_sock))

    send_thread.start()
    recv_stream_thread.start()
    recv_data_thread.start()


def client_session(client_sock, car_id):
    global cars_dict

    udp_socket, port = open_udp_sock()
    client_sock.send(str(port).encode())

    data, addr = udp_socket.recvfrom(1024)

    cars_dict[car_id] = []

    send_thread = threading.Thread(target=send_data_client, args=(car_id, client_sock, udp_socket, addr))
    send_thread.start()


def cars(sock, username):
    global session_dict
    cars_to_send = DB.get_cars_by_owner(username)
    print(cars_to_send)
    sock.send(pickle.dumps(cars_to_send))
    car_to_connect = sock.recv(1024).decode()
    print(car_to_connect)

    if car_to_connect == "BACK":
        return True
    else:
        session_dict[car_to_connect] = True
        return client_session(sock, car_to_connect) # returns if to continue or not at end


def add_car(sock, username):
    with open("cars_id.txt", "r") as f:
        id_lst = f.readlines()

    while True:
        data = sock.recv(1024).decode()

        if data == "EXIT":
            return False

        elif data == "BACK":
            return True

        data = data.split("~")

        if data[0] in id_lst and data[0] not in DB.get_cars_id_by_owner(username) and data[1] not in DB.get_cars_name_by_owner(username):
            new_car = Car(username, data[0], data[1], "offline")
            DB.insert_car(new_car)

            sock.send(b"GOOD")
            return True
        else:
            sock.send(b"NGOD")


def send_videos(sock, username):
    pass


def recv_choice(sock, username):
    running = True
    while running:
        choice = sock.recv(1024).decode()
        print(choice)

        if choice == "EXIT":
            running = False

        elif choice == "VCAR":
            running = cars(sock, username)

        elif choice == "NCAR":
            running = add_car(sock, username)

        elif choice == "VDEO":
            running = send_videos(sock, username)

    return


def handle_client(sock):
    sock.send(pickle.dumps(publickey))
    accepted, username = sign(sock)
    if accepted:
        recv_choice(sock, username)

    sock.close()
    print("thread closed")


def car_main_thread():
    car_main_socket = socket.socket()
    car_main_socket.bind(("0.0.0.0", 8000))
    car_main_socket.listen(20)
    while True:
        car_sock, addr = car_main_socket.accept()
        print(f"connected: {addr}")
        car_thread = threading.Thread(target=handle_car, args=(car_sock,))
        car_thread.start()


def client_main_thread():
    client_main_socket = socket.socket()
    client_main_socket.bind(("0.0.0.0", 9000))
    client_main_socket.listen(20)
    while True:
        cli_sock, addr = client_main_socket.accept()
        print("got client")
        client_thread = threading.Thread(target=handle_client, args=(cli_sock,))
        client_thread.start()


def main():
    car_accpet_thread = threading.Thread(target=car_main_thread, args=())
    client_accpet_thread = threading.Thread(target=client_main_thread, args=())

    car_accpet_thread.start()
    client_accpet_thread.start()


if __name__ == '__main__':
    main()
