import customtkinter
from PIL import Image
from tkinter import filedialog
import os
from ark_server_handler import ArkServerHandler
from passlib.hash import sha256_crypt
from data_extractor import DataExtractor
from resize_all_windows import resize

customtkinter.set_appearance_mode("dark")


class Button(customtkinter.CTkButton):
    def __init__(self, master, name, button_type=None, call_back=None, command_arg=None, **kwargs):
        """
        :type call_back: function
        """
        super().__init__(master, **kwargs)
        if command_arg is not None and call_back is not None:
            self.configure(command=lambda: call_back(command_arg))
        elif call_back is not None:
            self.configure(command=lambda: call_back())

        self.name = name
        self.button_type = button_type


class TkImage(customtkinter.CTkImage):
    def __init__(self, path, name, **kwargs):
        self.image = Image.open(os.path.join(path, name))
        self.name = name
        super().__init__(self.image, **kwargs)


class ParamsFrame(customtkinter.CTkFrame):
    def __init__(self, master, admin: bool, server_handler, refresh_main_frame, update_button_image,
                 delete_button_image, check_input_error, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.refresh_main_frame = refresh_main_frame
        self.update_button_image = update_button_image
        self.delete_button_image = delete_button_image
        self.check_input_error = check_input_error
        self.admin = admin
        self.server_handler = server_handler
        self.data_extractor = server_handler.data_extractor
        self.visible = False

        self.admin_frame, self.user_frame, self.path_entry, self.server_port_entry, self.target_ip_entry, self.target_port_entry = self.frame_constructor()

    def frame_constructor(self):
        # admin frame
        admin_entry_frame = customtkinter.CTkFrame(self, fg_color="transparent", bg_color="transparent")
        path_entry = customtkinter.CTkEntry(admin_entry_frame, width=200, placeholder_text="Path to ShooterGame.exe")
        if self.data_extractor.params.pathToShooterGame:
            path_entry.insert(0, self.data_extractor.params.pathToShooterGame)

        folder_button = customtkinter.CTkButton(admin_entry_frame, text="",
                                                command=lambda: self.select_folder(path_entry),
                                                width=20, fg_color="gray24", hover_color="gray12",
                                                image=TkImage(".\\images\\assets", "folder.png",
                                                              size=(15, 15)))

        server_port_entry = customtkinter.CTkEntry(admin_entry_frame, width=200, placeholder_text="Server port")
        if self.data_extractor.params.serverPort is not None:
            server_port_entry.insert(0, self.data_extractor.params.serverPort)
        # grid admin frame
        path_entry.grid(row=0, column=0, padx=(30, 0), pady=(15, 15), sticky="w")
        folder_button.grid(row=0, column=1)
        server_port_entry.grid(row=1, column=0, padx=30, pady=(0, 15))

        # user frame
        user_entry_frame = customtkinter.CTkFrame(self, fg_color="transparent", bg_color="transparent")
        target_ip_entry = customtkinter.CTkEntry(user_entry_frame, width=200, placeholder_text="Target ip")
        if self.data_extractor.params.targetIp is not None:
            target_ip_entry.insert(0, self.data_extractor.params.targetIp)
        target_port_entry = customtkinter.CTkEntry(user_entry_frame, width=200, placeholder_text="Target port")
        if self.data_extractor.params.targetPort is not None:
            target_port_entry.insert(0, self.data_extractor.params.targetPort)
        # grid user frame
        target_ip_entry.grid(row=0, column=0, padx=30, pady=(15, 15))
        target_port_entry.grid(row=1, column=0, padx=30, pady=(0, 15))

        # for admin and user
        modify_servers_button = customtkinter.CTkButton(self, text="Modify servers",
                                                        command=lambda: self.modify_servers(), width=200)
        save_changes_button = customtkinter.CTkButton(self, text="Save changes",
                                                      command=lambda: self.save_changes(), width=200)

        user_entry_frame.grid(row=1, column=0, padx=30, pady=15)
        modify_servers_button.grid(row=2, column=0, padx=30, pady=15)
        save_changes_button.grid(row=3, column=0, padx=30, pady=(0, 15))

        return admin_entry_frame, user_entry_frame, path_entry, server_port_entry, target_ip_entry, target_port_entry

    def select_folder(self, entry: customtkinter.CTkEntry):
        result = filedialog.askdirectory(title="select a folder")
        if result and result.endswith("ShooterGame"):
            result = result.replace("/", "\\")
            entry.insert(0, result)
            self.server_handler.update_shooter_game_path(result)

    def hide_show(self):
        if self.visible:
            self.grid_forget()
            self.visible = False
        else:
            if self.admin:
                self.admin_frame.grid(row=0, column=0, padx=30, pady=15)
                self.user_frame.grid_forget()
            self.grid(row=0, column=0)
            self.lift()
            self.visible = True

    def save_changes(self):
        if self.admin:
            self.data_extractor.update_param("serverPort", self.server_port_entry.get())
            self.server_handler.update_shooter_game_path(self.path_entry.get())
        else:
            self.data_extractor.update_param("targetIp", self.target_ip_entry.get())
            self.data_extractor.update_param("targetPort", self.target_port_entry.get())

    def modify_servers(self):
        modify_servers_frame = customtkinter.CTkFrame(self.master, fg_color="transparent", bg_color="transparent")

        servers_names = [server.name for server in self.server_handler.servers]
        choice = customtkinter.CTkOptionMenu(modify_servers_frame, values=servers_names)
        choice.grid(row=0, column=0, padx=30, pady=15)
        select_button = Button(modify_servers_frame, "select", call_back=self.select_server,
                               command_arg=(choice, modify_servers_frame), text="select")
        select_button.grid(row=1, column=0, padx=30, pady=15)

        self.hide_show()
        modify_servers_frame.grid(row=0, column=0)
        modify_servers_frame.lift()

    def select_server(self, args):
        server_name, frame = args
        server_name = server_name.get()
        server = self.server_handler.get_server(server_name)
        frame.grid_forget()

        modify_server_attributes_frame = customtkinter.CTkFrame(self.master, fg_color="transparent",
                                                                bg_color="transparent")

        top_frame = customtkinter.CTkFrame(modify_server_attributes_frame, fg_color="transparent",
                                           bg_color="transparent")
        add_server_label = customtkinter.CTkLabel(top_frame, text="Modify server attributes",
                                                  font=customtkinter.CTkFont(size=25, weight="bold"))
        close_button = customtkinter.CTkButton(top_frame, text="",
                                               command=lambda: modify_server_attributes_frame.grid_forget(),
                                               width=20, fg_color="gray24", hover_color="gray12",
                                               image=TkImage(".\\images\\assets", "close.png",
                                                             size=(15, 15)))
        add_server_label.grid(row=0, column=0, padx=45)
        close_button.grid(row=0, column=0, sticky="ne")

        server_name_input = customtkinter.CTkEntry(modify_server_attributes_frame, width=200,
                                                   placeholder_text="Server name")
        server_name_input.insert(0, server.name)

        dlcs = ["The Island", "The Center", "Scorched Earth", "Ragnarok", "Aberration", "Extinction", "Valguero",
                "Genesis: Part 1", "Crystal Isles", "Genesis: Part 2", "Lost Island", "Fjordur"]
        server_version = customtkinter.CTkOptionMenu(modify_server_attributes_frame, values=dlcs,
                                                     width=200,
                                                     fg_color="gray24", button_color="gray18",
                                                     button_hover_color="gray12")
        server_version.set(server.version)

        server_save_name_input = customtkinter.CTkEntry(modify_server_attributes_frame, width=200,
                                                        placeholder_text="Save folder name")
        server_save_name_input.insert(0, server.save_name)

        server_bat_name_input = customtkinter.CTkEntry(modify_server_attributes_frame, width=200,
                                                       placeholder_text="Bat name")
        server_bat_name_input.insert(0, server.bat_name)

        error_label = customtkinter.CTkLabel(modify_server_attributes_frame, text="", fg_color="transparent",
                                             text_color="red4", width=200)

        save_button = Button(modify_server_attributes_frame, "save", call_back=self.save_server,
                             command_arg=([server, server_name_input, server_version, server_save_name_input,
                                           server_bat_name_input, modify_server_attributes_frame, error_label]),
                             text="Save")

        delete_button = Button(modify_server_attributes_frame, "delete", call_back=self.delete_server,
                               command_arg=([server, modify_server_attributes_frame]),
                               text="Delete", fg_color="firebrick4", hover_color="firebrick3")

        top_frame.grid(row=0, column=0, padx=30, pady=15)
        server_name_input.grid(row=1, column=0, padx=30, pady=(15, 15))
        server_version.grid(row=2, column=0, padx=30, pady=(0, 15))
        server_save_name_input.grid(row=3, column=0, padx=30, pady=(0, 15))
        server_bat_name_input.grid(row=4, column=0, padx=30, pady=(0, 15))
        save_button.grid(row=5, column=0, padx=30, pady=(15, 15))
        delete_button.grid(row=6, column=0, padx=30, pady=(0, 15))
        error_label.grid(row=7, column=0, padx=30, pady=(0, 15))
        modify_server_attributes_frame.grid(row=0, column=0)
        modify_server_attributes_frame.lift()

    def save_server(self, args):
        server, server_name, server_version, save_name, bat_name, frame, error_label = args
        prompt_error = self.check_input_error(server_version.get(), server_name.get(), save_name.get(), bat_name.get())
        if prompt_error:
            error_label.configure(text=prompt_error)
        else:
            if server.version != server_version.get() or server.name != server_name.get():
                self.update_button_image(server.name, server_name.get(), server_version.get())

            self.server_handler.update_server(server.name, server_version.get(), server_name.get(),
                                              save_name.get(), bat_name.get())

            frame.grid_forget()
            self.refresh_main_frame()

    def delete_server(self, args):
        server, frame = args
        self.server_handler.delete_server(server.name)
        self.delete_button_image(server.name)
        frame.grid_forget()
        self.refresh_main_frame()


class ScrollableButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.button_list = []

    def add_item(self, button, index: tuple[int, int], padding=10):
        i, j = index

        button.grid(row=i, column=j, pady=padding, padx=padding, sticky="nsew")
        self.button_list.append(button)
        self.grid_columnconfigure(j, weight=1)
        self.grid_rowconfigure(i, weight=1)


class AddServerFrame(customtkinter.CTkFrame):
    def __init__(self, master, add_server_func, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
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
                                               image=TkImage(".\\images\\assets", "close.png",
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

        self.data_extractor = DataExtractor()
        self.server_handler = ArkServerHandler(self.data_extractor)

        self.title("Ark Server Manager")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)

        # load and create background image
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.bg_image = customtkinter.CTkImage(Image.open(".\\images\\assets\\wallpaper.png"),
                                               size=(self.width, self.height))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image)
        self.bg_image_label.grid(row=0, column=0)

        self.buttons_images = []
        self.buttons = []
        names = os.listdir("images\\thumbnails")
        for name in names:
            self.buttons_images.append(TkImage(".\\images\\thumbnails", name, size=(500, 280)))
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
        self.side_bar = None

        self.add_server_frame = AddServerFrame(self, self.add_server, fg_color="transparent",
                                               bg_color="transparent")

        self.params_frame = ParamsFrame(self, self.admin, self.server_handler, self.refresh_main_frame,
                                        self.update_button_image, self.delete_button_image,
                                        self.check_input_error, fg_color="transparent")

    def login_event(self):
        print("Login pressed - username:", self.username_entry.get(), "password:", self.password_entry.get())
        admin_username = '$5$jWN4MYtdJ.9xKhW/$uL33fRCPTvZVkYGAVa6a4ILt59WEs0c6qcbv/YajPJ.'
        admin_password = '$5$S0P8XKh9/NoX/hj.$eckpW4rPYDN1GJ27jiCvDUAB87z2LV64xaJU.31yyBC'
        username = sha256_crypt.verify(self.username_entry.get(), admin_username)
        password = sha256_crypt.verify(self.password_entry.get(), admin_password)
        self.admin = username and password
        self.admin = True

        print(f"{self.admin=}")

        if self.admin:
            self.buttons_images.append(TkImage(".\\images\\assets", "plus.png", size=(500, 280)))
            self.params_frame.admin = True

        self.login_frame.grid_forget()  # remove login frame

        self.main_frame, self.buttons = self.main_frame_constructor()
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=100)  # show main frame
        self.side_bar = self.side_bar_constructor()
        self.side_bar.grid(row=0, column=0, sticky="nse")

    def side_bar_constructor(self):
        side_bar = customtkinter.CTkFrame(self)

        image = TkImage(".\\images\\assets", "gear.png", size=(30, 30))
        gear_button = Button(side_bar, "gear", image=image, text="",
                             call_back=lambda: self.params_frame.hide_show(),
                             width=40, fg_color="transparent", bg_color="transparent", hover_color="gray12")

        image = TkImage(".\\images\\assets", "start.png", size=(30, 30))
        start_button = Button(side_bar, "start", image=image, text="",
                              call_back=lambda: self.start_all_servers(), width=40,
                              fg_color="transparent", bg_color="transparent", hover_color="gray12")

        image = TkImage(".\\images\\assets", "stop.png", size=(30, 30))
        stop_button = Button(side_bar, "stop", image=image, text="",
                             call_back=lambda: self.stop_all_servers(), width=40,
                             fg_color="transparent", bg_color="transparent", hover_color="gray12")

        gear_button.grid(row=0, column=0, padx=10, pady=10)
        start_button.grid(row=1, column=0, padx=10, pady=(0, 10))
        stop_button.grid(row=2, column=0, padx=10, pady=(0, 10))

        if self.admin:
            image = TkImage(".\\images\\assets", "grid.png", size=(30, 30))
            grid_button = Button(side_bar, "grid", image=image, text="",
                                 call_back=lambda: resize(self.server_handler.active_servers()), width=40,
                                 fg_color="transparent", bg_color="transparent", hover_color="gray12")

            image = TkImage(".\\images\\assets", "admin_panel.png", size=(30, 30))
            admin_panel_button = Button(side_bar, "admin_panel", image=image, text="",
                                        call_back=lambda: print("click!"), width=40,
                                        fg_color="transparent", bg_color="transparent", hover_color="gray12")

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
        main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        buttons_master = main_frame
        scrollable_frame = None
        if len(self.server_handler.servers) > 4 or (self.admin and len(self.server_handler.servers) > 3):
            scrollable_frame = ScrollableButtonFrame(main_frame)
            buttons_master = scrollable_frame

        buttons = []
        items = self.match_image_server()
        print(items)
        for server, image in items:
            button = Button(buttons_master, server.name, call_back=self.button_event, button_type="server",
                            command_arg=server.name, text="", image=image, bg_color="transparent",
                            hover_color="darkslategray")
            if server.is_online():
                button.configure(fg_color="green4")
            else:
                button.configure(fg_color="firebrick4")
            buttons.append(button)
        if self.admin:
            for image in self.buttons_images:
                if image.name.split(".")[0] == 'plus':
                    buttons.append(Button(buttons_master, "plus", call_back=self.plus_button_callback, text="",
                                          image=image))

        if len(buttons) > 4:
            main_frame.grid_columnconfigure(0, weight=1)
            main_frame.grid_rowconfigure(0, weight=1)

            for i, button in enumerate(buttons):
                scrollable_frame.add_item(button, (i // 2, i % 2))

            scrollable_frame.grid(row=0, column=0, sticky="nsew")

            return main_frame, scrollable_frame.button_list

        elif len(buttons) <= 4:
            for i in range(2):
                main_frame.grid_rowconfigure(i, weight=1)
                main_frame.grid_columnconfigure(i, weight=1)

            for i, button in enumerate(buttons):
                button.grid(row=i // 2, column=i % 2, pady=10, padx=10, sticky="nsew")

            return main_frame, buttons

    def refresh_main_frame(self):
        self.main_frame.grid_forget()
        self.main_frame, self.buttons = self.main_frame_constructor()
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=100)

    def update_button_image(self, old_name, new_name, version):
        new_image = TkImage(".\\images\\assets\\versions", self.image_version[version], size=(500, 280))
        image_ext = self.image_version[version].split(".")[-1]
        new_image.name = f"{new_name}.{image_ext}"
        new_image.image.save(f".\\images\\thumbnails\\{new_name}.{image_ext}")

        for i, image in enumerate(self.buttons_images):
            if image.name.split(".")[0] == old_name:
                os.remove(f".\\images\\thumbnails\\{image.name}")
                self.buttons_images[i] = new_image

    def delete_button_image(self, name):
        for i, image in enumerate(self.buttons_images):
            if image.name.split(".")[0] == name:
                os.remove(f".\\images\\thumbnails\\{image.name}")
                self.buttons_images.pop(i)

    def plus_button_callback(self):
        print("test")
        self.add_server_frame.grid(row=0, column=0)
        self.add_server_frame.lift()

    def start_all_servers(self):
        self.server_handler.start_all_servers()
        for button in self.buttons:
            if button.name != "plus":
                button.configure(fg_color="green4")

    def stop_all_servers(self):
        self.server_handler.stop_all_servers()
        for button in self.buttons:
            if button.name != "plus":
                button.configure(fg_color="firebrick4")

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
        prompt_error = self.check_input_error(version, name, save_name, bat_name)
        if prompt_error:
            self.add_server_frame.show_error_label(prompt_error)
        else:
            self.add_server_frame.hide_error_label()
            self.add_server_frame.grid_forget()

            tk_image = TkImage("images/assets/versions", self.image_version[version], size=(500, 280))
            image_ext = self.image_version[version].split(".")[-1]
            tk_image.image.save(f".\\images\\thumbnails\\{name}.{image_ext}")
            tk_image.name = f"{name}.{image_ext}"

            self.buttons_images.append(tk_image)
            self.server_handler.add_server(version, name, save_name, bat_name)

            self.refresh_main_frame()

    def check_input_error(self, version, name, save_name, bat_name):
        error, saves_files, bat_files = [], [], []
        saves_files_path = self.data_extractor.params.pathToShooterGame + "\\Saved"
        bat_files_path = self.data_extractor.params.pathToShooterGame + "\\Binaries\\Win64"
        try:
            saves_files = os.listdir(saves_files_path)
        except FileNotFoundError:
            error.append(f"Invalid path for saves files: {saves_files_path}")
        try:
            bat_files = os.listdir(bat_files_path)
        except FileNotFoundError:
            error.append(f"Invalid path for bat files: {bat_files_path}")

        if name and save_name in saves_files and bat_name in bat_files and self.data_extractor.params.pathToShooterGame:
            return False
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
                prompt_error += element + "\n"

            if self.data_extractor.params.pathToShooterGame is None:
                prompt_error = "No path to ShooterGame.exe"

            return prompt_error

    def select_image(self, name):
        if name:
            result = filedialog.askopenfilename(initialdir=self.get_download_path(), title="select an images",
                                                filetypes=[("Image file", "*.jpg"), ("Image file", "*.png")])
            image_ext = result.split("/")[-1].split(".")[-1]
            if result:
                image = Image.open(result)
                image.save(f".\\images\\thumbnails\\{name}.{image_ext}")

    def match_image_server(self) -> list:
        match_list = []
        for server in self.server_handler.servers:
            for image in self.buttons_images:
                if server.name == image.name.split(".")[0]:
                    match_list.append((server, image))
        print(match_list)
        return match_list

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
