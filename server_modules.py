import subprocess
from pid_modules import *


class Server:
    def __init__(self, app_name, bat_name):
        self.name, self.bat_name = app_name, bat_name

    def start(self, path):
        if not self.is_online():
            go2 = path+"\\Binaries\\Win64"
            command = f'{path[:2]} && cd "{go2}" && start {self.bat_name}'
            subprocess.run(command, shell=True)

    def close(self):
        if self.is_online():
            subprocess.run(f"taskkill /T /PID {process.pid}")

    def is_online(self):
        processes = get_processes(*sys.argv[1:])
        for process in processes:
            if self.name in process:
                return True
        return False


class ServerHandler:
    def __init__(self):
        self.servers = self.get_servers()
        with open('params.txt', 'r') as f:
            self.global_path, self.server_version = f.readlines()[:2]

    @staticmethod
    def get_servers() -> list[Server]:
        servers = []
        with open('apps.txt', 'r') as f:
            for line in f.readlines():
                server_name, bat_name = line.split("|")
                server = Server(server_name, bat_name)
                servers.append(server)
        return servers

    def add_server(self, server_name, bat_name) -> None:
        server = Server(server_name, bat_name)
        self.servers.append(server)
        with open("apps.txt", "a") as f:
            f.write(f"{server_name}|{bat_name}\n")

    def __str__(self):
        final_str = ""
        for server in self.servers:
            final_str += f"{server.name}|{server.bat_name}\n"
        return final_str

    def start_server(self, name):
        for server in self.servers:
            if name.lower() in server.name.lower():
                server.start(self.global_path)

    def close_server(self, name):
        for server in self.servers:
            if server.name == name:
                server.close()


if __name__ == "__main__":
    s = ServerHandler()
    s.add_server("extinction_test", "bat_test.bat")
