import subprocess
import sys
from pid_modules import get_processes


class ArkServer:
    def __init__(self, server_version, server_name, save_name, bat_name):
        self.name = server_name
        self.game_version = '358.17'
        self.version = server_version
        self.save_name = save_name
        self.bat_name = bat_name

    def start(self, path):
        if not self.is_online():
            go2 = path+"\\Binaries\\Win64"
            command = f'{path[:2]} && cd "{go2}" && call {self.bat_name}'
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

    def update(self, server_version, server_name, save_name, bat_name):
        self.version = server_version
        self.name = server_name
        self.save_name = save_name
        self.bat_name = bat_name

    def dict(self):
        return {
            "version": self.version,
            "name": self.name,
            "save_name": self.save_name,
            "bat_name": self.bat_name
        }
