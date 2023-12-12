import tkinter as tk
from Module import ColorMixerApp, Layer, Suggestion

class Main:
    def __init__(self, root):
        self.root = root
        root.title("Color Calculator")
        root.geometry('608x365+400+100')
        root.configure(bg="#293C4A", bd=10)
        root.resizable(False, False)

        button_params = {'bd': 5, 'fg': '#BBB', 'bg': '#3C3636', 'font': ('sans-serif', 20, 'bold')}

        self.ColorMixerApp_button = tk.Button(root, button_params, text="ColorMixerApp", command=self.open_ColorMixerApp, width=11, height=2)
        self.Layer_button = tk.Button(root, button_params, text="Layer", command=self.open_Layer, width=11, height=2)
        self.Suggestion_button = tk.Button(root, button_params, text="Suggestion", command=self.open_Suggestion, width=11, height=2)

        self.ColorMixerApp_button.place(anchor="s", relx=0.5, rely=0.3, x=0, y=0)
        self.Layer_button.place(anchor="s", relx=0.5, rely=0.5, x=0, y=0)
        self.Suggestion_button.place(anchor="s", relx=0.5, rely=0.7, x=0, y=0)

    def open_ColorMixerApp(self):
        try:
            new_window = tk.Toplevel(self.root)
            app = ColorMixerApp(new_window)
        except Exception as e:
            print(f"Failed to open ColorMixerApp: {e}")

    def open_Layer(self):
        new_window = tk.Toplevel(self.root)
        app = Layer(new_window)

    def open_Suggestion(self):
        new_window = tk.Toplevel(self.root)
        app = Suggestion(new_window)

if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()
