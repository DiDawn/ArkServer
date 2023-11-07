import customtkinter
from PIL import Image
from tkinter import filedialog
import os
from server_modules import ServerHandler

customtkinter.set_appearance_mode("dark")


class Button(customtkinter.CTkButton):
    def __init__(self, master, name, command, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(command=lambda: command(name))

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

    def add_item(self, image, command, index: tuple[int, int], padding=10, server=None, name=""):
        i, j = index
        button = Button(self, server.name, command, text="", image=image)

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


class App(customtkinter.CTk):
    width = 1280
    height = 720

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.server_handler = ServerHandler()

        self.title("CustomTkinter example_background_image.py")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(True, True)

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
            self.buttons_images.append(TkImage(self.current_path+"\\images\\thumbnails", name, size=(500, 280)))
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
        self.add_server_frame = None

    def login_event(self):
        print("Login pressed - username:", self.username_entry.get(), "password:", self.password_entry.get())
        self.admin = ("louis", "itsnoturs") == (self.username_entry.get(), self.password_entry.get())
        print(f"{self.admin:}")

        if self.admin:
            self.buttons_images.append(TkImage(self.current_path+"\\images", "plus.png", size=(500, 280)))

        # create main frame
        self.main_frame, self.buttons = self.main_frame_constructor()

        self.login_frame.grid_forget()  # remove login frame
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=100)  # show main frame

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

            scrollable_frame = ScrollableLabelButtonFrame(main_frame, command=self.button_event)
            for i, element in enumerate(zip(self.server_handler.servers, self.buttons_images)):
                server, image = element[0], element[1]
                scrollable_frame.add_item(image, self.button_event, (i // 2, i % 2), server=server)

            if self.admin:
                i = len(self.buttons_images)
                scrollable_frame.add_item(self.buttons_images[-1], self.button_event,
                                          (i // 2, i % 2), name="plus")

            scrollable_frame.grid(row=0, column=0, sticky="nsew")

            return main_frame, scrollable_frame.button_list
        else:
            main_frame = customtkinter.CTkFrame(self, corner_radius=0)
            for i in range(2):
                main_frame.grid_rowconfigure(i, weight=1)
                main_frame.grid_columnconfigure(i, weight=1)

            buttons = []
            for server, image in zip(self.server_handler.servers, self.buttons_images):
                button = (Button(main_frame, image.name, self.button_event, text="", image=image,
                                 bg_color="transparent", hover_color="darkslategray"))
                if server.is_online():
                    button.configure(fg_color="green4")
                else:
                    button.configure(fg_color="firebrick4")
                buttons.append(button)

            if self.admin:
                button = (Button(main_frame, "plus", self.button_event, text="", image=self.buttons_images[-1]))
                buttons.append(button)

            for i, button in enumerate(buttons):
                button.grid(row=i//2, column=i % 2, pady=10, padx=10, sticky="nsew")

            return main_frame, buttons

    def button_event(self, item):
        item = item.split('.')[0]
        print(item)
        if item == 'plus':
            self.add_server_frame = customtkinter.CTkFrame(self, fg_color="transparent", bg_color="transparent")
            self.add_server_frame.grid(row=0, column=0)
            add_server_label = customtkinter.CTkLabel(self.add_server_frame, text="Add a server",
                                                      font=customtkinter.CTkFont(size=25, weight="bold"))
            dlcs = ["The Island", "The Center", "Scorched Earth", "Ragnarok", "Aberration", "Extinction", "Valguero",
                    "Genesis: Part 1", "Crystal Isles", "Genesis: Part 2", "Lost Island", "Fjordur"]
            server_version = customtkinter.CTkOptionMenu(self.add_server_frame, values=dlcs,
                                                         width=200,
                                                         fg_color="gray24", button_color="gray18",
                                                         button_hover_color="gray12")
            server_name = customtkinter.CTkEntry(self.add_server_frame, width=200, placeholder_text="Server name")
            save_name = customtkinter.CTkEntry(self.add_server_frame, width=200, placeholder_text="Save folder name")
            bat_name = customtkinter.CTkEntry(self.add_server_frame, width=200, placeholder_text="Bat name")

            add_server_button = customtkinter.CTkButton(self.add_server_frame, text="Add a server",
                                                        command=lambda: self.add_server(server_version.get(),
                                                                                        server_name.get(),
                                                                                        save_name.get(),
                                                                                        bat_name.get()),
                                                        width=200, fg_color="gray24", hover_color="gray12")
            add_server_label.grid(row=0, column=0, padx=30, pady=15)
            server_version.grid(row=1, column=0, padx=30, pady=(15, 15))
            server_name.grid(row=2, column=0, padx=30, pady=(0, 15))
            save_name.grid(row=3, column=0, padx=30, pady=(0, 15))
            bat_name.grid(row=4, column=0, padx=30, pady=(0, 15))
            add_server_button.grid(row=5, column=0, padx=30, pady=(15, 15))
            self.add_server_frame.lift()

        else:
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
        if version and name and save_name and bat_name:
            if not bat_name.endswith(".bat"):
                bat_name += ".bat"

            self.add_server_frame.grid_forget()

            tk_image = TkImage(self.current_path+"\\images\\versions", self.image_version[version], size=(500, 280))
            self.buttons_images.append(tk_image)
            image_ext = self.image_version[version].split(".")[-1]
            tk_image.image.save(f".\\images\\thumbnails\\{name}.{image_ext}")

            self.server_handler.add_server(version, name, save_name, bat_name)

            self.buttons_images[-1], self.buttons_images[-2] = self.buttons_images[-2], self.buttons_images[-1]

            self.main_frame.grid_forget()

            self.main_frame, self.buttons = self.main_frame_constructor()
            self.main_frame.grid(row=0, column=0, sticky="nsew", padx=100)  # show main frame
        else:
            print("missing an argument")

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
