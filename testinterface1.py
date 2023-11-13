import customtkinter
from PIL import Image
from tkinter import filedialog
import os
from server_modules import ServerHandler
from passlib.hash import sha256_crypt

customtkinter.set_appearance_mode("dark")


class Button(customtkinter.CTkButton):
    def __init__(self, master, name, command, command_args=None, **kwargs):
        super().__init__(master, **kwargs)
        if command_args is not None:
            self.configure(command=lambda: command(*command_args))
        else:
            self.configure(command=lambda: command())

        self.name = name


class TkImage(customtkinter.CTkImage):
    def __init__(self, path, name, **kwargs):
        self.image = Image.open(os.path.join(path, name))
        self.name = name
        super().__init__(self.image, **kwargs)


class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.button_list = []

    def add_item(self, image, command, index: tuple[int, int], padding=10, server=None, name="", **kwargs):
        i, j = index
        if server is not None:
            button = Button(self, server.name, command, command_args=server.name, text="", image=image, **kwargs)
        else:
            button = Button(self, name, command, text="", image=image, **kwargs)

        if server is not None:
            if server.is_online():
                button.configure(fg_color="green4")
            else:
                button.configure(fg_color="firebrick4")

        if self.command is not None:
            if server is not None:
                button.configure(command=lambda: self.command(server.name))
            else:
                button.configure(command=lambda: self.command(name))
        button.grid(row=i, column=j, pady=padding, padx=padding, sticky="nsew")
        self.button_list.append(button)
        self.grid_columnconfigure(j, weight=1)
        self.grid_rowconfigure(i, weight=1)


class AddServerFrame(customtkinter.CTkFrame):
    def __init__(self, master, current_path, add_server_func, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.current_path = current_path
        self.add_server_func = add_server_func

        self.error_label = customtkinter.CTkLabel(self, text="", fg_color="transparent", text_color="red4", width=200)

        self.frame_constructor()

    def frame_constructor(self):
        top_frame = customtkinter.CTkFrame(self, fg_color="transparent", bg_color="transparent")
        add_server_label = customtkinter.CTkLabel(top_frame, text="Add a server",
                                                  font=customtkinter.CTkFont(size=25, weight="bold"))
        close_button = customtkinter.CTkButton(top_frame, text="",
                                               command=lambda: self.close_self(),
                                               width=20, fg_color="gray24", hover_color="gray12",
                                               image=TkImage(self.current_path + "\\images", "close.png",
                                                             size=(15, 15)))
        add_server_label.grid(row=0, column=0, padx=45)
        close_button.grid(row=0, column=0, sticky="ne")

        dlcs = ["The Island", "The Center", "Scorched Earth", "Ragnarok", "Aberration", "Extinction", "Valguero",
                "Genesis: Part 1", "Crystal Isles", "Genesis: Part 2", "Lost Island", "Fjordur"]
        server_version = customtkinter.CTkOptionMenu(self, values=dlcs,
                                                     width=200,
                                                     fg_color="gray24", button_color="gray18",
                                                     button_hover_color="gray12")
        server_name = customtkinter.CTkEntry(self, width=200, placeholder_text="Server name")
        save_name = customtkinter.CTkEntry(self, width=200, placeholder_text="Save folder name")
        bat_name = customtkinter.CTkEntry(self, width=200, placeholder_text="Bat name")

        add_server_button = customtkinter.CTkButton(self, text="Add a server",
                                                    command=lambda: self.add_server_func(server_version.get(),
                                                                                         server_name.get(),
                                                                                         save_name.get(),
                                                                                         bat_name.get()),
                                                    width=200, fg_color="gray24", hover_color="gray12")

        top_frame.grid(row=0, column=0, padx=30, pady=15)
        server_version.grid(row=1, column=0, padx=30, pady=(15, 15))
        server_name.grid(row=2, column=0, padx=30, pady=(0, 15))
        save_name.grid(row=3, column=0, padx=30, pady=(0, 15))
        bat_name.grid(row=4, column=0, padx=30, pady=(0, 15))
        add_server_button.grid(row=6, column=0, padx=30, pady=(15, 15))

    def show_error_label(self, error):
        self.error_label.configure(text=error)
        self.error_label.grid(row=5, column=0, padx=30)

    def hide_error_label(self):
        self.error_label.configure(text="")
        self.error_label.grid_forget()

    def close_self(self):
        self.hide_error_label()
        self.grid_forget()



class App(customtkinter.CTk):
    width = 1280
    height = 720

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.server_handler = ServerHandler()

        self.title("Ark Server Manager")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)

        # load and create background image
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.bg_image = customtkinter.CTkImage(Image.open(self.current_path + "\\images\\wallpaper.png"),
                                               size=(self.width, self.height))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image)
        self.bg_image_label.grid(row=0, column=0)

        self.buttons_images = []
        self.buttons = []
        names = os.listdir("images\\thumbnails")
        for name in names:
            self.buttons_images.append(TkImage(self.current_path + "\\images\\thumbnails", name, size=(500, 280)))
        self.image_version = {"The Island": "the island.jpg", "The Center": "the center.jpg",
                              "Scorched Earth": "scorched earth.jpg", "Ragnarok": "ragnarok.jpg",
                              "Aberration": "aberration.jpg", "Extinction": "extinction.jpg",
                              "Valguero": "valguero.jpg", "Genesis: Part 1": "genesis part1.jpg",
                              "Crystal Isles": "crystal isles.jpg", "Genesis: Part 2": "genesis part2.png",
                              "Lost Island": "lost island.jpg", "Fjordur": "fjordur.jpg"}

        # create login frame
        self.login_frame, self.username_entry, self.password_entry = self.login_frame_constructor()
        self.admin = False

        self.main_frame = None
        self.add_server_frame = AddServerFrame(self, self.current_path, self.add_server, fg_color="transparent",
                                               bg_color="transparent")

        self.side_bar = self.side_bar_constructor()

    def login_event(self):
        print("Login pressed - username:", self.username_entry.get(), "password:", self.password_entry.get())
        admin_username = '$5$jWN4MYtdJ.9xKhW/$uL33fRCPTvZVkYGAVa6a4ILt59WEs0c6qcbv/YajPJ.'
        admin_password = '$5$S0P8XKh9/NoX/hj.$eckpW4rPYDN1GJ27jiCvDUAB87z2LV64xaJU.31yyBC'
        username = sha256_crypt.verify(self.username_entry.get(), admin_username)
        password = sha256_crypt.verify(self.password_entry.get(), admin_password)
        self.admin = username and password
        print(f"{self.admin:}")
        self.admin = True
        if self.admin:
            self.buttons_images.append(TkImage(self.current_path + "\\images", "plus.png", size=(500, 280)))

        # create main frame
        self.main_frame, self.buttons = self.main_frame_constructor()

        self.login_frame.grid_forget()  # remove login frame
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=100)  # show main frame
        if self.admin:
            self.side_bar.grid(row=0, column=0, sticky="nse")

    def side_bar_constructor(self):
        side_bar = customtkinter.CTkFrame(self)

        image = TkImage(self.current_path + "\\images", "gear.png", size=(30, 30))
        gear_button = Button(side_bar, "gear", image=image, text="", command=lambda: print("click!"), width=40,
                             fg_color="transparent", bg_color="transparent", hover_color="gray12")

        image = TkImage(self.current_path + "\\images", "start.png", size=(30, 30))
        start_button = Button(side_bar, "start", image=image, text="",
                              command=lambda: self.server_handler.start_all_servers(), width=40,
                              fg_color="transparent", bg_color="transparent", hover_color="gray12")

        image = TkImage(self.current_path + "\\images", "stop.png", size=(30, 30))
        stop_button = Button(side_bar, "stop", image=image, text="",
                             command=lambda: self.server_handler.stop_all_servers(), width=40,
                             fg_color="transparent", bg_color="transparent", hover_color="gray12")

        image = TkImage(self.current_path + "\\images", "grid.png", size=(30, 30))
        grid_button = Button(side_bar, "grid", image=image, text="", command=lambda: print("click!"), width=40,
                             fg_color="transparent", bg_color="transparent", hover_color="gray12")

        image = TkImage(self.current_path + "\\images", "admin_panel.png", size=(30, 30))
        admin_panel_button = Button(side_bar, "admin_panel", image=image, text="",
                                    command=lambda: print("click!"), width=40,
                                    fg_color="transparent", bg_color="transparent", hover_color="gray12")

        gear_button.grid(row=0, column=0, padx=10, pady=10)
        start_button.grid(row=1, column=0, padx=10, pady=(0, 10))
        stop_button.grid(row=2, column=0, padx=10, pady=(0, 10))
        grid_button.grid(row=3, column=0, padx=10, pady=(0, 10))
        admin_panel_button.grid(row=4, column=0, padx=10, pady=(0, 10))

        return side_bar

    def login_frame_constructor(self):
        login_frame = customtkinter.CTkFrame(self, fg_color="transparent", bg_color="transparent")
        login_frame.grid(row=0, column=0)
        login_label = customtkinter.CTkLabel(login_frame, text="Login Page",
                                             font=customtkinter.CTkFont(size=25, weight="bold"))
        login_label.grid(row=0, column=0, padx=30, pady=15)
        username_entry = customtkinter.CTkEntry(login_frame, width=200, placeholder_text="Username")
        username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
        password_entry = customtkinter.CTkEntry(login_frame, width=200, show="*", placeholder_text="Password")
        password_entry.grid(row=2, column=0, padx=30, pady=(0, 15))
        login_button = customtkinter.CTkButton(login_frame, text="Login", command=self.login_event, width=200)
        login_button.grid(row=3, column=0, padx=30, pady=(15, 15))

        return login_frame, username_entry, password_entry

    def main_frame_constructor(self):
        if len(self.buttons_images) > 4:
            main_frame = customtkinter.CTkFrame(self, corner_radius=0)

            main_frame.grid_columnconfigure(0, weight=1)
            main_frame.grid_rowconfigure(0, weight=1)

            scrollable_frame = ScrollableLabelButtonFrame(main_frame)
            for i, element in enumerate(zip(self.server_handler.servers, self.buttons_images)):
                server, image = element[0], element[1]
                scrollable_frame.add_item(image, self.button_event, (i // 2, i % 2), server=server)

            if self.admin:
                i = len(self.buttons_images) - 1
                scrollable_frame.add_item(self.buttons_images[-1], self.plus_button_callback,
                                          (i // 2, i % 2), name="plus", fg_color="gray30", hover_color="gray12")

            scrollable_frame.grid(row=0, column=0, sticky="nsew")

            return main_frame, scrollable_frame.button_list
        else:
            main_frame = customtkinter.CTkFrame(self, corner_radius=0)
            for i in range(2):
                main_frame.grid_rowconfigure(i, weight=1)
                main_frame.grid_columnconfigure(i, weight=1)

            buttons = []
            for server, image in zip(self.server_handler.servers, self.buttons_images):
                button = (Button(main_frame, image.name, self.button_event, command_args=image.name, text="",
                                 image=image, bg_color="transparent", hover_color="darkslategray"))
                if server.is_online():
                    button.configure(fg_color="green4")
                else:
                    button.configure(fg_color="firebrick4")
                buttons.append(button)

            if self.admin:
                button = (Button(main_frame, "plus", self.plus_button_callback, text="", image=self.buttons_images[-1]))
                buttons.append(button)

            for i, button in enumerate(buttons):
                button.grid(row=i // 2, column=i % 2, pady=10, padx=10, sticky="nsew")

            return main_frame, buttons

    def plus_button_callback(self):
        self.add_server_frame.grid(row=0, column=0)
        self.add_server_frame.lift()

    def button_event(self, item):
        print(item)
        item = item.split('.')[0]
        for button in self.buttons:
            if button.name.split(".")[0] == item:
                if self.server_handler.is_server_online(item):
                    button.configure(fg_color="firebrick4")
                    self.server_handler.close_server(item)
                else:
                    button.configure(fg_color="green4")
                    self.server_handler.start_server(item)

    def add_server(self, version, name, save_name, bat_name):
        print(version, name, save_name, bat_name)

        if not bat_name.endswith(".bat") and bat_name:
            bat_name += ".bat"

        error, saves_files, bat_files = [], [], []
        saves_files_path = self.server_handler.global_path + "\\Saved"
        bat_files_path = self.server_handler.global_path+"\\Binaries\\Win64"
        try:
            saves_files = os.listdir(saves_files_path)
        except FileNotFoundError:
            error.append(f"Invalid path for saves files: {saves_files_path}")
        try:
            bat_files = os.listdir(bat_files_path)
        except FileNotFoundError:
            error.append(f"Invalid path for bat files: {bat_files_path}")

        if name and save_name in saves_files and bat_name in bat_files:

            self.add_server_frame.hide_error_label()
            self.add_server_frame.grid_forget()

            tk_image = TkImage(self.current_path + "\\images\\versions", self.image_version[version], size=(500, 280))
            self.buttons_images.append(tk_image)
            image_ext = self.image_version[version].split(".")[-1]
            tk_image.image.save(f".\\images\\thumbnails\\{name}.{image_ext}")

            self.server_handler.add_server(version, name, save_name, bat_name)

            self.buttons_images[-1], self.buttons_images[-2] = self.buttons_images[-2], self.buttons_images[-1]

            self.main_frame.grid_forget()

            self.main_frame, self.buttons = self.main_frame_constructor()
            self.main_frame.grid(row=0, column=0, sticky="nsew", padx=100)  # show main frame
        else:
            if not save_name:
                error.append("No save name")
            if save_name and not (save_name in saves_files):
                error.append(f"Invalid save name: {save_name}")
            if not bat_name:
                error.append("No bat name")
            if bat_name and not (bat_name in bat_files):
                error.append(f"Invalid bat name: {bat_name}")

            if not version:
                error.append("No version selected")
            if not name:
                error.append("Need a name to create a server")

            prompt_error = ""
            for element in error:
                prompt_error += element+"\n"

            self.add_server_frame.show_error_label(prompt_error)

    def select_image(self, name):
        if name:
            result = filedialog.askopenfilename(initialdir=self.get_download_path(), title="select an images",
                                                filetypes=[("Image file", "*.jpg"), ("Image file", "*.png")])
            image_ext = result.split("/")[-1].split(".")[-1]
            if result:
                image = Image.open(result)
                image.save(f".\\images\\thumbnails\\{name}.{image_ext}")

    @staticmethod
    def get_download_path():
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        else:
            return os.path.join(os.path.expanduser('~'), 'downloads')


if __name__ == "__main__":
    app = App()
    app.mainloop()
