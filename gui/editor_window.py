import tkinter as tk
from tkinter import ttk
from .theme import VSCodeTheme

class EditorWindow:
    def __init__(self, parent, content="", file_path=None, font=None):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.create_editor(content, font)
        
    def create_editor(self, content, font):
        # Create line numbers
        self.line_numbers = tk.Text(
            self.frame,
            width=4,
            padx=3,
            pady=5,
            bg=VSCodeTheme.SIDEBAR_BG,
            fg='#6e7681',
            relief='flat',
            font=font,
            state='disabled'
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Create main editor
        self.editor = tk.Text(
            self.frame,
            bg=VSCodeTheme.EDITOR_BG,
            fg=VSCodeTheme.FOREGROUND,
            insertbackground=VSCodeTheme.FOREGROUND,
            relief='flat',
            font=font,
            pady=5,
            padx=5,
            wrap='none'
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.configure(yscrollcommand=scrollbar.set)

        # Insert content
        if content:
            self.editor.insert('1.0', content)
            self.update_line_numbers()

        # Bind events
        self.editor.bind('<Key>', lambda e: self.update_line_numbers())
        self.editor.bind('<MouseWheel>', lambda e: self.update_line_numbers())

    def update_line_numbers(self):
        self.line_numbers.configure(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        
        count = self.editor.get('1.0', tk.END).count('\n')
        numbers = '\n'.join(str(i) for i in range(1, count + 1))
        
        self.line_numbers.insert('1.0', numbers)
        self.line_numbers.configure(state='disabled')

    def get_content(self):
        return self.editor.get('1.0', tk.END)

    def set_content(self, content):
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', content)
        self.update_line_numbers()
