import json
from test_client import Client
from ark_server import ArkServer


class CustomArkServer(ArkServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_online = False


class CustomClient(Client):
    def __init__(self, port, ip):
        super().__init__(port, ip)

        self.servers = []
        self.get_servers()

    def get_servers(self):
        self.send_txt('get_servers')

    def resize_servers_window(self):
        self.send_txt('resize_servers_window')

    def start_all_servers(self):
        self.send_txt('start_all')

    def close_server(self, server_name):
        self.send_txt('stop_server')
        self.send_txt(server_name)

    def start_server(self, server_name):
        self.send_txt('start_server')
        self.send_txt(server_name)

    def stop_all_servers(self):
        self.send_txt('stop_all')

    def update_server_state(self, server_name):
        self.send_txt('is_server_online:')
        self.send_txt(server_name)

    def add_server(self, server_dict):
        self.send_txt('add_server')
        self.send_json(server_dict)
        self.servers.append(CustomArkServer.from_dict(server_dict))

    def update_shooter_game_path(self, path):
        self.send_txt('update_shooter_game_path')
        self.send_txt(path)

    def save_new_server_params(self, old_name, server_dict):
        self.send_txt('save_new_server_params')
        self.send_txt(old_name)
        self.send_json(server_dict)

    def delete_server(self, server_name):
        self.send_txt('delete_server')
        self.send_txt(server_name)

    def handle_msg(self, msg_type, msg) -> bool:
        if msg_type == 'txt':
            if msg == 'close':
                return False

            elif msg == 'servers:':
                _, msg = self.receive_msg()
                servers = json.loads(msg)

                for element in servers.values():
                    self.servers.append(CustomArkServer.from_dict(element))

            elif msg == 'server_name_state:':
                _, msg = self.receive_msg()
                server_name = msg.decode('utf-8')
                _, msg = self.receive_msg()
                state = msg.decode('utf-8')
                if state == 'True':
                    state = True
                else:
                    state = False

                for server in self.servers:
                    if server.name == server_name:
                        server.is_online = state

        return True


if __name__ == '__main__':
    client = CustomClient(5050, '192.168.230.225')
    client.send_txt('close')
