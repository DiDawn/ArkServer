from data_extractor import DataExtractor
from ark_server import ArkServer


class ArkServerHandler:
    def __init__(self, data_extractor: DataExtractor):
        self.data_extractor = data_extractor
        self.servers = self.data_extractor.extract_servers()
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
        self.get_server(name).close()

    def is_server_online(self, name):
        return self.get_server(name).is_online()

    def get_server(self, name):
        for server in self.servers:
            if server.name == name:
                return server

    def active_servers(self):
        return [server for server in self.servers if server.is_online()]

    def update_server(self, name, server_version, server_name, save_name, bat_name):
        server = self.get_server(name)
        server.update(server_version, server_name, save_name, bat_name)
        self.data_extractor.update_server(self.servers)

    def delete_server(self, name):
        server = self.get_server(name)
        self.servers.remove(server)
        self.data_extractor.delete_server(self.servers, name)

    def __str__(self):
        final_str = ""
        for server in self.servers:
            final_str += f"{server.version}|{server.name}|{server.save_name}|{server.bat_name}\n"
        return final_str

    def dict(self):
        final_dict = {}
        for server in self.servers:
            final_dict[server.name] = server.dict()
        return final_dict
