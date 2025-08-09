import tkinter as tk
from pygments import lex
from pygments.lexers import get_lexer_for_filename
from pygments.styles import get_style_by_name

class SyntaxHighlighter:
    @staticmethod
    def apply_highlighting(text_widget, filename, content):
        try:
            lexer = get_lexer_for_filename(filename)
            style = get_style_by_name('monokai')
            
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', content)
            
            for token, value in lex(content, lexer):
                style_color = style.style_for_token(token)['color']
                if style_color:
                    tag_name = str(token)
                    text_widget.tag_configure(tag_name, foreground=f"#{style_color}")
                    
                    start = '1.0'
                    while True:
                        start = text_widget.search(value, start, tk.END)
                        if not start:
                            break
                        end = f"{start}+{len(value)}c"
                        text_widget.tag_add(tag_name, start, end)
                        start = end
                        
        except Exception as e:
            print(f"Error in syntax highlighting: {e}")
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', content)