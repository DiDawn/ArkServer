from data_extractor import DataExtractor
from ark_server import ArkServer


class ArkServerHandler:
    def __init__(self):
        self.data_extractor = DataExtractor()
        self.servers = self.data_extractor.get_servers()
        self.shooter_game_path = self.data_extractor.params.pathToShooterGame

    def update_shooter_game_path(self, path):
        self.shooter_game_path = path
        self.data_extractor.update_param("pathToShooterGame", path)

    def add_server(self, server_version, server_name, save_name, bat_name) -> None:
        server = ArkServer(server_version, server_name, save_name, bat_name)
        self.servers.append(server)
        self.data_extractor.add_server(server_version, server_name, save_name, bat_name)

    def start_server(self, name):
        for server in self.servers:
            if name.lower() in server.name.lower():
                server.start(self.shooter_game_path)

    def start_all_servers(self):
        for server in self.servers:
            if not server.is_online():
                server.start(self.shooter_game_path)

    def stop_all_servers(self):
        for server in self.servers:
            if server.is_online():
                server.close()

    def close_server(self, name):
        for server in self.servers:
            if server.name == name:
                server.close()

    def is_server_online(self, name):
        for server in self.servers:
            if server.name == name:
                return server.is_online()

    def __str__(self):
        final_str = ""
        for server in self.servers:
            final_str += f"{server.version}|{server.name}|{server.save_name}|{server.bat_name}\n"
        return final_str
