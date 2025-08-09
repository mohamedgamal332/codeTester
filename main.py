from gui.editor import VSCodeLikeGUI
from gui.theme import setup_styles

if __name__ == "__main__":
    try:
        app = VSCodeLikeGUI()
        setup_styles()
        app.root.mainloop()
    except Exception as e:
        print(f"Error in main: {str(e)}")