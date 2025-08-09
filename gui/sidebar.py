import tkinter as tk
from tkinter import ttk
from pathlib import Path
from .theme import VSCodeTheme

class Sidebar:
    def __init__(self, parent, callbacks):
        self.frame = ttk.Frame(parent, style='Dark.TFrame')
        self.callbacks = callbacks
        self.opened_files = {}
        self.setup_sidebar()

    def setup_sidebar(self):
        # Activity bar (left side)
        self.activity_bar = ttk.Frame(self.frame, style='Dark.TFrame')
        self.activity_bar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create test buttons
        self.add_activity_button("Static Test", self.callbacks['static'])
        self.add_activity_button("Dynamic Test", self.callbacks['dynamic'])
        self.add_activity_button("White Box Test", self.callbacks['whitebox'])
        self.add_activity_button("Open Folder", self.callbacks['open_folder'])
        
        # Files sidebar
        self.files_sidebar = ttk.Frame(self.frame, style='Dark.TFrame')
        self.files_sidebar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Explorer header with buttons
        self.create_explorer_header()
        
        # File tree
        self.create_file_tree()

    def add_activity_button(self, text, command):
        btn = ttk.Button(
            self.activity_bar,
            text=text,
            command=command,
            style='Toolbutton'
        )
        btn.pack(pady=2, padx=2)
        
        # Create enhanced tooltip that shows selected files
        def get_tooltip_text():
            selected_items = self.get_selected_items()
            if selected_items:
                if len(selected_items) == 1:
                    return f"{text}\nSelected: {selected_items[0].name}"
                else:
                    file_names = [item.name for item in selected_items[:3]]
                    if len(selected_items) > 3:
                        file_names.append(f"... and {len(selected_items) - 3} more")
                    return f"{text}\nSelected: {', '.join(file_names)}"
            else:
                return f"{text}\nNo files selected"
        
        self.create_tooltip(btn, get_tooltip_text)

    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Handle both string and function text
            tooltip_text = text() if callable(text) else text
            
            label = ttk.Label(
                tooltip, 
                text=tooltip_text, 
                background=VSCodeTheme.SIDEBAR_BG, 
                foreground=VSCodeTheme.FOREGROUND
            )
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.after(2000, hide_tooltip)
            
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def create_explorer_header(self):
        header_frame = ttk.Frame(self.files_sidebar)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            header_frame, 
            text="EXPLORER", 
            style='Dark.TLabel'
        ).pack(side=tk.LEFT)
        
    def create_header_button(self, text, command):
        btn = ttk.Button(
            self.files_sidebar,
            text=text,
            command=command,
            style='Toolbutton',
            width=3
        )
        btn.pack(side=tk.RIGHT, padx=2)

    def create_file_tree(self):
        # Create tree frame with scrollbar
        tree_frame = ttk.Frame(self.files_sidebar)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create tree with columns for icons and names
        self.tree = ttk.Treeview(
            tree_frame, 
            show='tree', 
            selectmode='browse',
            style='Custom.Treeview'
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, 
            orient="vertical", 
            command=self.tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind events
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        self.tree.bind('<Return>', self.on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_change)

        # Configure style
        style = ttk.Style()
        style.configure(
            'Custom.Treeview',
            background=VSCodeTheme.EDITOR_BG,
            foreground=VSCodeTheme.FOREGROUND,
            fieldbackground=VSCodeTheme.EDITOR_BG
        )
        
        # Add selection status label
        self.selection_status = ttk.Label(
            self.files_sidebar,
            text="No files selected",
            style='Dark.TLabel',
            font=('Consolas', 9)
        )
        self.selection_status.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate_tree(self, directory):
        self.current_directory = directory
        self.clear_tree()
        self._populate_tree_recursive(directory, "")

    def _populate_tree_recursive(self, directory, parent):
        try:
            # Sort directories first, then files
            paths = sorted(
                directory.iterdir(),
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
            
            for path in paths:
                # Skip hidden files and __pycache__
                if path.name.startswith('.') or path.name == '__pycache__':
                    continue

                # Create unique ID for the item
                item_id = str(path)
                
                # Insert item into tree
                self.tree.insert(
                    parent, 
                    'end',
                    item_id,
                    text=path.name,
                    tags=('directory' if path.is_dir() else 'file',)
                )
                
                # Recursively populate subdirectories
                if path.is_dir():
                    self._populate_tree_recursive(path, item_id)
                    
        except PermissionError:
            pass  # Skip directories we can't access
        except Exception as e:
            print(f"Error populating tree: {e}")

    def on_double_click(self, event):
        item_id = self.tree.focus()
        if item_id:
            path = Path(item_id)
            if path.is_file():
                self.callbacks['open_file'](path)

    def refresh_tree(self):
        if hasattr(self, 'current_directory'):
            self.populate_tree(self.current_directory)

    def collapse_all(self):
        for item in self.tree.get_children():
            self.tree.item(item, open=False)

    def get_selected_items(self):
        """Return list of selected file paths"""
        return [Path(item) for item in self.tree.selection()]

    def on_selection_change(self, event):
        """Update selection status when files are selected"""
        selected_items = self.get_selected_items()
        if selected_items:
            if len(selected_items) == 1:
                self.selection_status.config(text=f"Selected: {selected_items[0].name}")
            else:
                self.selection_status.config(text(f"Selected: {len(selected_items)} files"))
        else:
            self.selection_status.config(text="No files selected")