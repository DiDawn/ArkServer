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
    def get_servers() -> list[ArkServer]:
        servers = []
        with open('apps.txt', 'r') as f:
            for line in f.readlines():
                version, name, save_name, bat_name = line.strip("\n").split("|")
                server = ArkServer(version, name, save_name, bat_name)
                servers.append(server)
        return servers

    @staticmethod
    def add_server(server_version, server_name, save_name, bat_name) -> None:
        with open('apps.txt', 'a') as f:
            f.write(f"{server_version}|{server_name}|{save_name}|{bat_name}\n")
