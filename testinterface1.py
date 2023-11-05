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

    def add_item(self, server, image, command, index: tuple[int, int], padding=10):
        i, j = index
        button = Button(self, server.name, command, text="", image=image)

        if server.is_online():
            button.configure(fg_color="green4")
        else:
            button.configure(fg_color="firebrick4")

        if self.command is not None:
            button.configure(command=lambda: self.command(server.name))
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
        names = os.listdir(".\\images\\versions")
        for name in names:
            self.buttons_images.append(TkImage(self.current_path+"\\images\\versions", name, size=(500, 280)))

        # create login frame
        self.login_frame, self.username_entry, self.password_entry = self.login_frame_constructor()
        self.admin = False
        self.server_image = False

        self.main_frame = None
        self.add_server_frame = None

    def login_event(self):
        print("Login pressed - username:", self.username_entry.get(), "password:", self.password_entry.get())
        self.admin = ("louis", "itsnoturs") == (self.username_entry.get(), self.password_entry.get())

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
                scrollable_frame.add_item(server, image, self.button_event, (i // 2, i % 2))

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

            for i, button in enumerate(buttons):
                button.grid(row=i//2, column=i % 2, pady=10, padx=10, sticky="nsew")

            return main_frame, buttons

    def button_event(self, item):
        item = item.split('.')[0]
        if item == 'plus':
            self.add_server_frame = customtkinter.CTkFrame(self, fg_color="transparent", bg_color="transparent")
            self.add_server_frame.grid(row=0, column=0)
            add_server_label = customtkinter.CTkLabel(self.add_server_frame, text="Add server",
                                                      font=customtkinter.CTkFont(size=25, weight="bold"))
            server_name = customtkinter.CTkEntry(self.add_server_frame, width=200, placeholder_text="Version name")
            bat_name = customtkinter.CTkEntry(self.add_server_frame, width=200, placeholder_text="Bat name")
            add_image_button = customtkinter.CTkButton(self.add_server_frame, text="Add an image",
                                                       command=lambda: self.select_image(server_name.get()),
                                                       width=200)
            add_server_button = customtkinter.CTkButton(self.add_server_frame, text="Add a server",
                                                        command=lambda: self.add_server(server_name.get(),
                                                                                        bat_name.get()), width=200)
            add_server_label.grid(row=0, column=0, padx=30, pady=15)
            server_name.grid(row=1, column=0, padx=30, pady=(15, 15))
            bat_name.grid(row=2, column=0, padx=30, pady=(0, 15))
            add_image_button.grid(row=3, column=0, padx=30, pady=(15, 15))
            add_server_button.grid(row=4, column=0, padx=30, pady=(0, 15))
            self.add_server_frame.lift()

        else:
            for button in self.buttons:
                if button.name == item:
                    if self.server_handler.is_server_online(item):
                        button.configure(fg_color="firebrick4")
                        self.server_handler.close_server(item)
                    else:
                        button.configure(fg_color="green4")
                        self.server_handler.start_server(item)

    def add_server(self, name, bat_name):
        print(name, bat_name, self.server_image)
        if name and bat_name and self.server_image:

            self.add_server_frame.grid_forget()

            self.server_handler.add_server(name, bat_name)

            self.buttons_images.append(TkImage(self.current_path+"\\images\\versions",
                                               self.server_image, size=(500, 280)))
            self.buttons_images[-1], self.buttons_images[-2] = self.buttons_images[-2], self.buttons_images[-1]
            self.server_image = False

            self.main_frame.grid_forget()

            self.main_frame = self.main_frame_constructor()
            self.main_frame.grid(row=0, column=0, sticky="nsew", padx=100)  # show main frame
        else:
            print("missing an argument")

    def select_image(self, name):
        if name:
            result = filedialog.askopenfilename(initialdir=self.get_download_path(), title="select an images",
                                                filetypes=[("Image file", "*.jpg"), ("Image file", "*.png")])
            image_ext = result.split("/")[-1].split(".")[-1]
            image = Image.open(result)
            image.save(f".\\images\\versions\\{name}.{image_ext}")

            self.server_image = f"{name}.{image_ext}"

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
