import cv2
import socket
import pickle

sock = socket.socket()
sock.connect(("10.100.102.8", 4004))

vid = cv2.VideoCapture(0)

while True:
    try:
        ret, frame = vid.read()
        data = pickle.dumps(frame)

        chunk_size = 4096
        chunck_lst = []
        for i in range(0, len(data), chunk_size):
            chunck_lst.append(data[i:i + chunk_size])

        sock.send(len(data).to_bytes(3, 'big'))
        print(f"sent: {len(data)}")

        for i in chunck_lst:
            sock.send(i)
        print("sent")
    except:
        break

vid.release()

