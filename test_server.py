import socket
from threading import Thread
from logger import Log
import json


class Server:
    def __init__(self, port, save_log=True):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostbyname(socket.gethostname()), port))
        self.save_log = save_log
        self.log = Log(self.save_log)

    def handle_client(self, conn, addr):
        self.log.append(f'[NEW CONNECTION] {addr} connected.')
        connected = True
        while connected:
            msg_type, msg = self.get_msg(conn)

            if msg_type == 'txt':
                if msg == 'close':
                    connected = False
                    self.log.append(f'[DISCONNECTED] {addr} disconnected.')
                else:
                    self.log.append(f'[MESSAGE] {addr} sent: {msg}')

            elif msg_type == 'json':
                self.log.append(f'[MESSAGE] {addr} sent: {msg}')

        self.send_txt(conn, 'Closing connection.')
        conn.close()

    @staticmethod
    def receive(conn):
        msg_length = conn.recv(64).decode('utf-8')
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode('utf-8')
            return msg

    @staticmethod
    def send(conn, message: bytes):
        msg_length = len(message)
        send_length = str(msg_length).encode('utf-8')
        send_length += b' ' * (64 - len(send_length))
        conn.send(send_length)
        conn.send(message)

    @staticmethod
    def send_type(conn, msg_type):
        Server.send(conn, msg_type.encode('utf-8'))

    @staticmethod
    def send_txt(conn, msg: str):
        Server.send_type(conn, 'txt')
        message = msg.encode('utf-8')
        Server.send(conn, message)

    @staticmethod
    def send_json(conn, msg: dict):
        Server.send_type(conn, 'json')
        message = json.dumps(msg).encode('utf-8')
        Server.send(conn, message)

    def get_msg(self, conn):
        msg_type = self.receive(conn)
        msg = self.receive(conn)

        if msg_type == 'txt':
            return msg_type, msg

        elif msg_type == 'json':
            msg = json.loads(msg)
            return msg_type, msg

    def listen(self):
        self.socket.listen()
        while True:
            conn, addr = self.socket.accept()
            Thread(target=self.handle_client, args=(conn, addr)).start()


server = Server(5050)
server.listen()
