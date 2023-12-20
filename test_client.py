import socket
import json


class Client:
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((socket.gethostbyname(socket.gethostname()), port))

    def send(self, message: bytes):
        msg_length = len(message)
        send_length = str(msg_length).encode('utf-8')
        send_length += b' ' * (64 - len(send_length))
        self.socket.send(send_length)
        self.socket.send(message)

    def send_txt(self, msg: str):
        self.send_type('txt')
        message = msg.encode('utf-8')
        self.send(message)

    def send_json(self, msg: dict):
        self.send_type('json')
        message = json.dumps(msg).encode('utf-8')
        self.send(message)

    def send_type(self, msg_type):
        self.send(msg_type.encode('utf-8'))

    def receive(self):
        msg_length = self.socket.recv(64).decode('utf-8')
        if msg_length:
            msg_length = int(msg_length)
            msg = self.socket.recv(msg_length).decode('utf-8')
            return msg

    def get_msg(self):
        msg_type = self.receive()
        msg = self.receive()
        return msg_type, msg

    def close(self):
        self.send_txt('close')
        print(self.get_msg())
        self.socket.close()


client = Client(5050)
client.send_json({'name': 'John', 'age': 30})
client.close()
