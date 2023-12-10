import socket


class Client:
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((socket.gethostbyname(socket.gethostname()), port))

    def send(self, msg):
        message = msg.encode('utf-8')
        msg_length = len(message)
        send_length = str(msg_length).encode('utf-8')
        send_length += b' ' * (64 - len(send_length))
        self.socket.send(send_length)
        self.socket.send(message)
        print(self.socket.recv(64).decode('utf-8'))

    def close(self):
        self.send('close')
        self.socket.close()


client = Client(5050)
