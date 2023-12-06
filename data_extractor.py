import os
import csv
from dataclasses import dataclass
from ark_server import ArkServer


@dataclass
class Params:
    pathToShooterGame: str = None
    serverPort: int = None
    targetPort: int = None
    targetIp: str = None


class DataExtractor:
    def __init__(self):
        self.params = self.extract_params()
        self.extract_servers()

    @staticmethod
    def extract_params() -> Params:
        params = Params()
        if os.path.exists("params.csv"):
            with open("params.csv", encoding="utf8", newline="") as f:
                data = csv.reader(f)
                for line in data:
                    if line[1] != "None":
                        setattr(params, line[0], line[1].strip())
        else:
            with open("params.csv", encoding="utf8", newline="") as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerows([["pathToShooterGame", "None"], ["serverPort", "None"], ["targetPort", "None"],
                                  ["targetIp", "None"]])

        return params

    def update_param(self, param, value) -> None:
        print(param, value)
        if not self.params.__dict__[param] == value:
            print(value)
            setattr(self.params, param, value)
            with open("params.csv", "w", encoding="utf8", newline="") as f:
                writer = csv.writer(f, delimiter=',')
                for key, value in self.params.__dict__.items():
                    if value is None:
                        value = "None"
                    writer.writerow([key, value])

    @staticmethod
    def extract_servers():
        servers = []
        if os.path.exists("servers.csv"):
            with open("servers.csv", encoding="utf-8", newline="") as f:
                data = csv.reader(f)
                for line in data:
                    version, name, save_name, bat_name = line
                    server = ArkServer(version, name, save_name, bat_name)
                    servers.append(server)
        else:
            with open("servers.csv", encoding="utf-8", newline=""):
                pass

        return servers

    @staticmethod
    def add_server(server_version, server_name, save_name, bat_name) -> None:
        with open("servers.csv", "a", encoding="utf-8", newline="")as f:
            writer = csv.writer(f)
            writer.writerow([server_version, server_name, save_name, bat_name])

    @staticmethod
    def update_server(servers) -> None:
        with open("servers.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for server in servers:
                writer.writerow([server.version, server.name, server.save_name, server.bat_name])

    @staticmethod
    def delete_server(server_name):
        with open("servers.csv", encoding="utf-8", newline="") as f:
            data = csv.reader(f)
        with open("servers.csv", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for i, line in data:
                if line[1] != server_name:
                    writer.writerow(line)
