import pygetwindow


class Window:
    def __init__(self, ark_map, game_version):
        self.win = pygetwindow.getWindowsWithTitle(f'G:/SteamCMD/steamapps/common/ARK Survival Evolved Dedicated Server/ShooterGame/Binaries/Win64/ShooterGameServer.exe v{game_version} [AltSaveDir={ark_map}]')[0]

    def resize(self):
        self.win.size = (900, 200)

    def place(self, n_left, n_top):
        self.win.moveTo(n_left, n_top)


def resize(active_server_list):
    for i, server in enumerate(active_server_list):
        window = Window(server.save_name, server.game_version)
        window.resize()
        window.place((i % 2) * 900, 100 + (i//2) * 200)
