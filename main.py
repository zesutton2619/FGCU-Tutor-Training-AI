import gui
from tkinter import messagebox


if __name__ == "__main__":
    try:
        gui.start_gui()
    except Exception as e:
        messagebox.showerror("Error", str(e))
