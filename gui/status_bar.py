import tkinter as tk
from tkinter import ttk
from .theme import VSCodeTheme

class StatusBar:
    def __init__(self, parent, font):
        self.parent = parent
        self.status_label = ttk.Label(
            parent,
            text="",
            font=font,
            background=VSCodeTheme.BACKGROUND,
            foreground=VSCodeTheme.FOREGROUND
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def show_message(self, message, duration=3000):
        self.status_label.config(text=message)
        self.parent.after(duration, lambda: self.status_label.config(text=""))
