import subprocess
import sys
from pid_modules import get_processes


class Server:
    def __init__(self, server_version, server_name, save_name, bat_name):
        self.name = server_name
        self.version = server_version
        self.save_name = save_name
        self.bat_name = bat_name

    def start(self, path):
        if not self.is_online():
            go2 = path+"\\Binaries\\Win64"
            command = f'{path[:2]} && cd "{go2}" && start {self.bat_name}'
            subprocess.run(command, shell=True)

    def close(self):
        online, pid = self.is_online(return_pid=True)
        if online:
            subprocess.run(f"taskkill /T /PID {pid}")

    def is_online(self, return_pid=False):
        processes = get_processes(*sys.argv[1:])
        for process in processes:
            if self.save_name in process:
                if return_pid:
                    return True, process.pid
                return True
        if return_pid:
            return False, 0
        return False


class ServerHandler:
    def __init__(self):
        self.servers = self.get_servers()
        with open('params.txt', 'r') as f:
            self.global_path = f.readlines()[0]
            self.global_path = self.global_path.split("=")[1][1:].strip("\n")

    @staticmethod
    def get_servers() -> list[Server]:
        servers = []
        with open('apps.txt', 'r') as f:
            for line in f.readlines():
                version, name, save_name, bat_name = line.strip("\n").split("|")
                server = Server(version, name, save_name, bat_name)
                servers.append(server)
        return servers

    def add_server(self, server_version, server_name, save_name, bat_name) -> None:
        server = Server(server_version, server_name, save_name, bat_name)
        self.servers.append(server)
        with open("apps.txt", "a") as f:
            f.write(f"{server_version}|{server_name}|{save_name}|{bat_name}\n")

    def __str__(self):
        final_str = ""
        for server in self.servers:
            final_str += f"{server.version}|{server.name}|{server.save_name}|{server.bat_name}\n"
        return final_str

    def start_server(self, name):
        for server in self.servers:
            if name.lower() in server.name.lower():
                server.start(self.global_path)

    def close_server(self, name):
        for server in self.servers:
            if server.name == name:
                server.close()

    def is_server_online(self, name):
        for server in self.servers:
            if server.name == name:
                return server.is_online()


if __name__ == "__main__":
    s = ServerHandler()
