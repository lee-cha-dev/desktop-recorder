from tkinter import ttk, messagebox
from tkinter import font as tkFont


class CustomComboBox(ttk.Combobox):
    def __init__(self, master=None, values=None, **kw):
        super().__init__(master, values=values, **kw)

        # Use a modern font and larger size for the button text
        self.custom_font = tkFont.Font(family="Helvetica", size=10, weight="bold")

        # Apply the font
        self.option_add('TCombobox*Listbox*Font', self.custom_font)
        self.configure(font=self.custom_font)

        self.values = values

        # Bind for on hover
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        # self.config(foreground=self.hover_foreground, background=self.hover_background)
        pass

    def on_leave(self, e):
        # self.config(foreground=self.default_foreground, background=self.default_background)
        pass

