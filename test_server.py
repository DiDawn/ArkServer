import socket
from threading import Thread
from time import localtime


class Log:
    def __init__(self):

        with open('log.txt', 'r') as f:
            self.log = f.readlines()

    def __str__(self):
        return '\n'.join(self.log)

    def append(self, msg):
        date = localtime()
        year, month = date.tm_year, date.tm_mon
        if month < 10:
            month = f'0{month}'
        day, hour, minute, second = date.tm_mday, date.tm_hour, date.tm_min, date.tm_sec
        if day < 10:
            day = f'0{day}'
        if hour < 10:
            hour = f'0{hour}'
        if minute < 10:
            minute = f'0{minute}'
        if second < 10:
            second = f'0{second}'
        msg = f'[{year}/{month} {hour}:{minute}:{second}]~{msg}'
        self.log.append(msg)
        print(msg)
        with open('log.txt', 'a') as f:
            f.write(msg+'\n')


class Server:
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostbyname(socket.gethostname()), port))
        self.log = Log()

    def handle_client(self, conn, addr):
        self.log.append(f'[NEW CONNECTION] {addr} connected.')
        connected = True
        while connected:
            msg_length = conn.recv(64).decode('utf-8')
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode('utf-8')
                if msg == 'close':
                    connected = False
                    conn.send('Connection closed.'.encode('utf-8'))
                    self.log.append(f'[CONNECTION CLOSED] {addr} disconnected.')
                else:
                    conn.send('Message received.'.encode('utf-8'))
                    self.log.append(f'[Message] {addr}: {msg}')
        conn.close()
        print(self.log)

    def listen(self):
        self.socket.listen(2)
        while True:
            conn, addr = self.socket.accept()
            Thread(target=self.handle_client, args=(conn, addr)).start()


server = Server(5050)
server.listen()
