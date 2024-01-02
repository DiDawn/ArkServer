from test_server import Server
import json
from ark_server_handler import ArkServerHandler
from data_extractor import DataExtractor


class ServerDataExchange(Server):
    def __init__(self, port, ark_server_handler):
        super().__init__(port)

        self.ark_server_handler = ark_server_handler

        self.map = {
            'get_servers': self.send_servers,
            'start_all': self.start_all_servers,
            'stop_all': self.stop_all_servers,
            'resize_servers_window': self.resize_servers_window,
        }

        self.listen()

    def handle_msg(self, conn, addr, msg_type, msg):
        print(msg, type(msg))
        if msg_type == 'txt':
            msg = msg.decode('utf-8')

            if msg == 'close':
                self.log.append(f'[DISCONNECTED] {addr} disconnected.')
                return False

            elif msg == 'is_server_online':
                _, msg = self.receive_msg(conn)
                server_name = msg.decode('utf-8')
                is_online = self.ark_server_handler.is_server_online(server_name)
                self.send_txt(conn, f'server_name_state:')
                self.send_txt(conn, server_name)
                if is_online:
                    self.send_txt(conn, f'True')
                else:
                    self.send_txt(conn, 'False')

            elif msg == 'stop_server':
                _, server_name = self.receive_msg(conn)
                server_name = server_name.decode('utf-8')
                self.ark_server_handler.closer_server(server_name)

            elif msg == 'start_server':
                _, server_name = self.receive_msg(conn)
                server_name = server_name.decode('utf-8')
                self.ark_server_handler.start_server(server_name)

            elif msg == 'add_server':
                _, msg = self.receive_msg(conn)
                serv_dict = json.loads(msg)
                name, version = serv_dict['name'], serv_dict['version']
                save_name, bat_name = serv_dict['save_name'], serv_dict['bat_name']
                self.ark_server_handler.add_server(version, name, save_name, bat_name)

            elif msg == 'update_shooter_game_path':
                _, msg = self.receive_msg(conn)
                path = msg.decode('utf-8')
                self.ark_server_handler.update_shooter_game_path(path)

            elif msg == 'save_new_server_params':
                _, old_name = self.receive_msg(conn)
                old_name = old_name.decode('utf-8')
                _, msg = self.receive_msg(conn)
                serv_dict = json.loads(msg)
                name, version = serv_dict['name'], serv_dict['version']
                save_name, bat_name = serv_dict['save_name'], serv_dict['bat_name']
                self.ark_server_handler.update_server(old_name, version, name, save_name, bat_name)

            elif msg == 'delete_server':
                _, server_name = self.receive_msg(conn)
                server_name = server_name.decode('utf-8')
                self.ark_server_handler.delete_server(server_name)

            else:
                self.log.append(f'[MESSAGE] {addr} sent: {msg}')
                self.map[msg](conn)

        elif msg_type == 'json':
            msg = json.loads(msg.decode('utf-8'))
            self.log.append(f'[MESSAGE] {addr} sent: {msg}')

        return True

    def send_servers(self, conn):
        self.send_txt(conn, 'servers:')
        self.send_json(conn, self.ark_server_handler.dict())

    def start_all_servers(self, _):
        self.ark_server_handler.start_all_servers()

    def stop_all_servers(self, _):
        self.ark_server_handler.stop_all_servers()

    def resize_servers_window(self, _):
        self.ark_server_handler.resize_servers_window()


if __name__ == '__main__':
    data_extractor = DataExtractor()
    ark_servers_handler = ArkServerHandler(data_extractor)
    server_data_exchange = ServerDataExchange(5050, ark_servers_handler)
    server_data_exchange.listen()
