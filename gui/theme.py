import platform
from tkinter import ttk

class VSCodeTheme:
    # VS Code colors
    BACKGROUND = '#1e1e1e'
    SIDEBAR_BG = '#252526'
    EDITOR_BG = '#1e1e1e'
    FOREGROUND = '#d4d4d4'
    SELECTION_BG = '#264f78'
    ACTIVE_TAB_BG = '#1e1e1e'
    INACTIVE_TAB_BG = '#2d2d2d'
    ACCENT_BLUE = '#007acc'
    
    # Font settings
    if platform.system() == 'Darwin':  # macOS
        FONT_FAMILY = 'SF Mono'
        FONT_SIZE = 12
        PREVIEW_FONT_SIZE = 14  # Bigger for preview panel
    elif platform.system() == 'Windows':
        FONT_FAMILY = 'Consolas'
        FONT_SIZE = 11
        PREVIEW_FONT_SIZE = 13  # Bigger for preview panel
    else:  # Linux
        FONT_FAMILY = 'DejaVu Sans Mono'
        FONT_SIZE = 11
        PREVIEW_FONT_SIZE = 13  # Bigger for preview panel
    
    FALLBACK_FONTS = ['Consolas', 'Monaco', 'DejaVu Sans Mono', 'Courier New']
    
    # Preview panel specific settings
    PREVIEW_FONT_FAMILY = FONT_FAMILY
    CHAT_FONT_SIZE = FONT_SIZE + 1  # Slightly bigger for chat

def setup_styles():
    style = ttk.Style()
    
    # Configure common styles
    style.configure('Dark.TFrame', background=VSCodeTheme.BACKGROUND)
    style.configure('Dark.TLabel', background=VSCodeTheme.BACKGROUND, foreground=VSCodeTheme.FOREGROUND)
    style.configure('Accent.TButton', background=VSCodeTheme.ACCENT_BLUE)
    style.configure('Toolbutton', background=VSCodeTheme.SIDEBAR_BG)
    
    # Configure Notebook styles
    style.configure('TNotebook', background=VSCodeTheme.BACKGROUND)
    style.configure('TNotebook.Tab', background=VSCodeTheme.INACTIVE_TAB_BG, 
                   foreground=VSCodeTheme.FOREGROUND, padding=[10, 2])
    
    # Configure Treeview styles
    style.configure('Treeview', 
                   background=VSCodeTheme.EDITOR_BG,
                   foreground=VSCodeTheme.FOREGROUND,
                   fieldbackground=VSCodeTheme.EDITOR_BG)
