import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog, messagebox, StringVar
from PIL import Image
import cv2
import numpy as np
from sklearn.cluster import KMeans
import colorsys
import re
import imghdr
from abc import ABC, abstractmethod



class GUIComponent(ABC):
    def __init__(self, master, **kwargs):
        self.master = master
        self.create_widget(**kwargs)

    @abstractmethod
    def create_widget(self, **kwargs):
        pass

class CustomButton(GUIComponent, tk.Button):
    def create_widget(self, **kwargs):
        tk.Button.__init__(self, self.master, **kwargs)


class CustomLabel(GUIComponent, tk.Label):
    def create_widget(self, **kwargs):
        tk.Label.__init__(self, self.master, **kwargs, fg='black') 

class Hex(ABC):

    @abstractmethod
    def import_colors(self):
        pass
    
    @abstractmethod
    def hex_to_rgb(self, hex_color):
        pass

    @abstractmethod
    def rgb_to_hex(self, rgb_color):
        pass

class UI(object):
    def __init__(self, root, color1, color2, camera, color1_label, color2_label, color3_label, color_button, random_color_button, upload_button, camera_button, reset_button, add_button, subtract_button, manual_input_button, color_option, color1_radio, result_label):
        self.root = root
        self.color1 = color1
        self.color2 = color2
        self.camera = camera
        self.color1_label = color1_label
        self.color2_label = color2_label
        self.color3_label = color3_label
        self.color_button = color_button
        self.random_color_button = random_color_button
        self.upload_button = upload_button
        self.camera_button = camera_button
        self.reset_button = reset_button
        self.add_button = add_button
        self.subtract_button = subtract_button
        self.manual_input_button = manual_input_button
        self.color_option = color_option
        self.color1_radio = color1_radio
        self.result_label = result_label

        # ui
        root.title("Color Calculator")
        root.geometry('608x365+400+100')
        root.configure(bg="#293C4A", bd=10)
        root.resizable(False, False)

        button_params = {'bd': 5, 'fg': '#BBB', 'bg': '#3C3636', 'font': ('sans-serif', 20, 'bold')}

        self.color1_label = CustomLabel(root, text="Color 1", bg="white", width=8, height=5)
        self.color2_label = CustomLabel(root, text="Color 2", bg="white", width=8, height=5)
        self.result_label = CustomLabel(root, text="", bg="white", width=8, height=5)

        self.color_button = CustomButton(root, text="Choose Color", command=self.import_colors, width=11, height=2, bd=5, fg='#BBB', bg='#3C3636', font=('sans-serif', 20, 'bold'))
        self.random_color_button = tk.Button(root, button_params, text="Random Color", command=self.random_color, width=11,height=2)
        self.upload_button = tk.Button(root, button_params, text="Upload Image", command=self.upload_image, width=11,height=2)
        self.camera_button = tk.Button(root, button_params, text="Open Camera", command=self.open_camera, width=11,height=2)
        self.reset_button = tk.Button(root, button_params, text="Delete", command=self.reset, width=11,height=2)
        self.add_button = tk.Button(root, button_params, text="Add Colors", command=self.add_colors, width=11,height=2)
        self.subtract_button = tk.Button(root, button_params, text="Subtract Colors", command=self.subtract_colors, width=11,height=2)
        self.manual_input_button = tk.Button(root, button_params, text="Manual Input Color", command=self.manual_input_color, width=11,height=2)

        self.color_option = StringVar()
        self.color_option.set("color1")
        self.color1_radio = tk.Radiobutton(root, text="Color 1", variable=self.color_option, value="color1")
        self.color2_radio = tk.Radiobutton(root, text="Color 2", variable=self.color_option, value="color2")

        self.color1_label.grid(row=1, column=0, sticky="nsew")
        self.color2_label.grid(row=1, column=1, sticky="nsew")
        self.result_label.grid(row=1, column=2, sticky="nsew")

        self.color1_radio.grid(row=2, column=0, sticky="nsew")
        self.color2_radio.grid(row=2, column=1, sticky="nsew")
        self.add_button.grid(row=2, column=2, sticky="nsew")
        self.color_button.grid(row=3, column=0, sticky="nsew")
        self.random_color_button.grid(row=3, column=1, sticky="nsew")
        self.subtract_button.grid(row=3, column=2, sticky="nsew")
        self.upload_button.grid(row=4, column=0, sticky="nsew")
        self.camera_button.grid(row=4, column=1, sticky="nsew")
        self.reset_button.grid(row=4, column=2, sticky="nsew")
        self.manual_input_button.grid(row=5, column=1, sticky="nsew")

        self.color1 = (255, 255, 255)
        self.color2 = (255, 255, 255)

        self.camera = None


class ColorMixerApp(UI,Hex):
    def __init__(self, root,add_used = False,subtract_used = False):
        super().__init__(
            root=root,
            color1=(255, 255, 255), 
            color2=(255, 255, 255), 
            camera=None,
            color1_label=None,
            color2_label=None,
            color3_label=None,
            color_button=None,
            random_color_button=None,
            upload_button=None,
            camera_button=None,
            reset_button=None,
            add_button=None,
            subtract_button=None,
            manual_input_button=None,
            color_option=StringVar(),
            color1_radio=None,
            result_label=None
        )
        self.add_used =add_used
        self.subtract_used =subtract_used

    def import_colors(self):
        try:
            selected_color = self.color_option.get()
            color = colorchooser.askcolor()
            if color:  
                hex_color = color[1]  
                if selected_color == "color1":
                    self.color1 = color[0]  
                    self.color1_label.config(bg=hex_color, text=hex_color)  
                elif selected_color == "color2":
                    self.color2 = color[0]
                    self.color2_label.config(bg=hex_color, text=hex_color)
            self.reset_add_subtract_flags()
        except Exception as e:
            print(f"Error occurred: {e}")

    def manual_input_color(self):
        try:
            selected_color = self.color_option.get()
            color_input = simpledialog.askstring("Input Color", "Enter color in #RRGGBB format:")
            if color_input:
                if self.is_valid_hex_color(color_input):
                    rgb_color = self.hex_to_rgb(color_input)
                    if selected_color == "color1":
                        self.color1 = rgb_color
                        self.color1_label.config(bg=color_input, text=color_input)
                    elif selected_color == "color2":
                        self.color2 = rgb_color
                        self.color2_label.config(bg=color_input, text=color_input)
                else:
                    raise ValueError("Invalid color format. Please use the #RRGGBB format.")
                self.reset_add_subtract_flags()
        except ValueError as ve:
            messagebox.showerror("Invalid Color Format", str(ve))
        except Exception as e:
            messagebox.showerror("Error", "An unexpected error occurred: " + str(e))


    def random_color(self):
        random_color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
        hex_color = "#{:02X}{:02X}{:02X}".format(*random_color)
        selected_color = self.color_option.get()
        if selected_color == "color1":
            self.color1 = random_color
            self.color1_label.config(bg=hex_color, text=hex_color)
        elif selected_color == "color2":
            self.color2 = random_color
            self.color2_label.config(bg=hex_color, text=hex_color)
        self.reset_add_subtract_flags()

    def get_most_common_color(self, image_path):
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        small_image = cv2.resize(image_rgb, (50, 50))
        pixels = small_image.reshape(-1, 3)
        colors, counts = np.unique(pixels, axis=0, return_counts=True)
        most_common_color = colors[counts.argmax()]
        most_common_color = tuple(map(int, most_common_color))
        return most_common_color

    def upload_image(self):
        try:
            selected_color = self.color_option.get()
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.bmp")])
            if file_path:
                if imghdr.what(file_path) is not None:
                    color = self.get_most_common_color(file_path)
                    hex_color = "#{:02X}{:02X}{:02X}".format(*color)
                    if selected_color == "color1":
                        self.color1 = color
                        self.color1_label.config(bg=hex_color, text=hex_color)
                    elif selected_color == "color2":
                        self.color2 = color
                        self.color2_label.config(bg=hex_color, text=hex_color)
                else:
                    # when the upload not image
                    raise ValueError("The selected file is not a supported image format.")
                self.reset_add_subtract_flags()
        except ValueError as ve:
            messagebox.showerror("Invalid File", str(ve))
        except Exception as e:
            messagebox.showerror("Error", "An unexpected error occurred while uploading the image: " + str(e))


    def open_camera(self):
        try:
            selected_color = self.color_option.get()
            if not self.camera:
                self.camera = cv2.VideoCapture(0)

            ret, frame = self.camera.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_pil = Image.fromarray(image)
                color = self.get_dominant_color(image_pil)
                hex_color = "#{:02X}{:02X}{:02X}".format(*color)
                if selected_color == "color1":
                    self.color1 = color
                    self.color1_label.config(bg=hex_color, text=hex_color)
                elif selected_color == "color2":
                    self.color2 = color
                    self.color2_label.config(bg=hex_color, text=hex_color)
            self.reset_add_subtract_flags()
            self.camera = None
        except Exception as e:
            messagebox.showerror("Error", "An unexpected error occurred while accessing the camera: " + str(e))


    def process_and_display_image(self, image, selected_color):
        try:
            resized_image = image.resize((100, 100))
            color = self.get_dominant_color_upload(resized_image)
            if selected_color == "color1":
                self.color1 = color
                self.color1_label.config(bg=self.rgb_to_hex(color))
            elif selected_color == "color2":
                self.color2 = color
                self.color2_label.config(bg=self.rgb_to_hex(color))
        except Exception as e:
            print(f"Error in process_and_display_image: {e}")

    def get_dominant_color(self, image):
        try:
            pixels = np.array(image)
            pixels = pixels.reshape(-1, 3)
            dominant_color = pixels.mean(axis=0)
            return tuple(map(int, dominant_color))
        except Exception as e:
            print(f"Error in get_dominant_color: {e}")

    def get_dominant_color_upload(self, image, num_colors=1):
        try:
            pixels = np.array(image)
            if pixels.shape[2] != 3:
                image = image.convert("RGB")
                pixels = np.array(image)
            pixels = pixels.reshape(-1, 3)
            kmeans = KMeans(n_clusters=num_colors)
            kmeans.fit(pixels)
            dominant_color = kmeans.cluster_centers_[0]
            return tuple(map(int, dominant_color))
        except Exception as e:
            print(f"Error in get_dominant_color_upload: {e}")

    def display_result(self, text, color, selected_color):
        try:
            result_label_text = self.rgb_to_hex(color)
            self.result_label.config(text=result_label_text, bg=result_label_text)
        except Exception as e:
            print(f"Error in display_result: {e}")

    def reset(self):
        try:
            selected_color = self.color_option.get()
            if self.color1 == (255, 255, 255) and self.color2 == (255, 255, 255):
                result_label_text = "#FFFFFF"
                self.result_label.config(text=result_label_text, bg=result_label_text)
            else:
                if selected_color == "color1":
                    self.color1 = (255, 255, 255)
                    self.color1_label.config(bg=self.rgb_to_hex(self.color1))
                elif selected_color == "color2":
                    self.color2 = (255, 255, 255)
                    self.color2_label.config(bg=self.rgb_to_hex(self.color2))
        except Exception as e:
            print(f"Error in reset: {e}")

    def add_colors(self):
        try:
            if self.add_used:
                messagebox.showwarning("Warning", "Add operation already used. Please change Color 1 or Color 2.")
                return
            selected_color = self.color_option.get()
            if selected_color == "color1":
                r1, g1, b1 = self.color1
                r2, g2, b2 = self.color2
            else:
                r1, g1, b1 = self.color2
                r2, g2, b2 = self.color1

            added_color = ((r1 + r2) // 2, (g1 + g2) // 2, (b1 + b2) // 2)
            self.display_result("Add Color: " + self.rgb_to_hex(added_color), added_color, selected_color)

            if selected_color == "color1":
                self.color1 = added_color
            elif selected_color == "color2":
                self.color2 = added_color
            self.add_used = True
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred while adding colors: {e}")

    def subtract_colors(self):
        try:
            if self.subtract_used:
                messagebox.showwarning("Warning", "Subtract operation already used. Please change Color 1 or Color 2.")
                return

            selected_color = self.color_option.get()
            if selected_color == "color1":
                r1, g1, b1 = self.color1
                r2, g2, b2 = self.color2
            else:
                r1, g1, b1 = self.color2
                r2, g2, b2 = self.color1

            subtracted_color = (max(0, r1 - r2), max(0, g1 - g2), max(0, b1 - b2))
            self.display_result("Subtract Color: " + self.rgb_to_hex(subtracted_color), subtracted_color, selected_color)

            if selected_color == "color1":
                self.color1 = subtracted_color
            elif selected_color == "color2":
                self.color2 = subtracted_color

            self.subtract_used = True
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred while subtracting colors: {e}")

    def reset_add_subtract_flags(self):
        self.add_used = False
        self.subtract_used = False

    def is_valid_hex_color(self, hex_color):
        try:    
            hex_color = hex_color.lstrip('#')
            return len(hex_color) == 6 and all(c in '0123456789ABCDEFabcdef' for c in hex_color)
        except TypeError:
            return False

    def hex_to_rgb(self, hex_color):
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            messagebox.showerror("Error", "Invalid hexadecimal color format")

    @staticmethod
    def rgb_to_hex(rgb):
        return "#{:02X}{:02X}{:02X}".format(*rgb)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorMixerApp(root)
    root.mainloop()

class UI_2(object):
    def __init__(self, root, blue_frame, white_rectangle, Main_color_label, secondary_color_label, decorative_color_1_label, decorative_color_2_label, decorative_color_3_label, colors):
        self.blue_frame = blue_frame
        self.white_rectangle = white_rectangle
        self.Main_color_label = Main_color_label
        self.secondary_color_label = secondary_color_label
        self.decorative_color_1_label = decorative_color_1_label
        self.decorative_color_2_label = decorative_color_2_label
        self.decorative_color_3_label = decorative_color_3_label

        self.root = root
        root.title("Color Mixer")
        root.geometry('700x500+400+100')
        root.configure(bg="#293C4A", bd=10)
        root.resizable(False, False)

        self.blue_frame = tk.Frame(root, bg="#293C4A")
        self.blue_frame.pack(expand=True, fill="both")

        self.white_rectangle = tk.Frame(self.blue_frame, width=550, height=150, bg="#FFFFFF")
        self.white_rectangle.place(anchor="center", relx=0.5, rely=0.5)

        self.Main_color_label = CustomLabel(self.white_rectangle, text="first", bg="white", width=5)
        self.secondary_color_label = CustomLabel(self.white_rectangle, text="second", bg="white", width=5)
        self.decorative_color_1_label = CustomLabel(self.white_rectangle, text="third", bg="white", width=5)
        self.decorative_color_2_label = CustomLabel(self.white_rectangle, text="fourth", bg="white", width=5)
        self.decorative_color_3_label = CustomLabel(self.white_rectangle, text="fifth", bg="white", width=5)

        self.Main_color_label.place(relx=0.1, rely=0.5)
        self.secondary_color_label.place(relx=0.3, rely=0.5)
        self.decorative_color_1_label.place(relx=0.5, rely=0.5)
        self.decorative_color_2_label.place(relx=0.7, rely=0.5)
        self.decorative_color_3_label.place(relx=0.9, rely=0.5)

        self.colors = ["", "", "", "", ""]



class UI_2(object):
    def __init__(self, root, blue_frame, white_rectangle, Main_color_label, secondary_color_label, decorative_color_1_label, decorative_color_2_label, decorative_color_3_label, colors):
        self.blue_frame = blue_frame
        self.white_rectangle = white_rectangle
        self.Main_color_label = Main_color_label
        self.secondary_color_label = secondary_color_label
        self.decorative_color_1_label = decorative_color_1_label
        self.decorative_color_2_label = decorative_color_2_label
        self.decorative_color_3_label = decorative_color_3_label
        self.root = root
        root.title("Color Mixer")
        root.geometry('700x500+400+100')
        root.configure(bg="#293C4A", bd=10)
        root.resizable(False, False)
        self.blue_frame = tk.Frame(root, bg="#293C4A")
        self.blue_frame.pack(expand=True, fill="both")
        self.white_rectangle = tk.Frame(self.blue_frame, width=550, height=150, bg="#FFFFFF")
        self.white_rectangle.place(anchor="center", relx=0.5, rely=0.5)
        self.Main_color_label = CustomLabel(self.white_rectangle, text="first", bg="white", width=5)
        self.secondary_color_label = CustomLabel(self.white_rectangle, text="second", bg="white", width=5)
        self.decorative_color_1_label = CustomLabel(self.white_rectangle, text="third", bg="white", width=5)
        self.decorative_color_2_label = CustomLabel(self.white_rectangle, text="fourth", bg="white", width=5)
        self.decorative_color_3_label = CustomLabel(self.white_rectangle, text="fifth", bg="white", width=5)
        self.Main_color_label.place(relx=0.05, rely=0.5)
        self.secondary_color_label.place(relx=0.25, rely=0.5)
        self.decorative_color_1_label.place(relx=0.45, rely=0.5)
        self.decorative_color_2_label.place(relx=0.65, rely=0.5)
        self.decorative_color_3_label.place(relx=0.85, rely=0.5)
        self.colors = ["", "", "", "", ""]

class Suggestion(UI_2,Hex):
    def __init__(self, root, import_button=None, suggest_button=None, random_button=None, reset_button=None, manual_input_button=None, two_color=None, three_color=None, four_color=None, five_color=None, color_option=None, secondary_color=None, decorative_color_1=None, decorative_color_2=None, decorative_color_3=None, last_suggested_colors=None, color_options=None, placement_radios=None, number_of_color=None, one_color=None, Main_color_radio=None,deep_colors_executed=False,light_colors_executed=False):
        super().__init__(
            root=root,
            blue_frame=None,
            white_rectangle=None,
            Main_color_label=None,
            secondary_color_label=None,
            decorative_color_1_label=None,
            decorative_color_2_label=None,
            decorative_color_3_label=None,
            colors=None
        )
        self.import_button = import_button
        self.suggest_button = suggest_button
        self.random_button = random_button
        self.reset_button = reset_button
        self.manual_input_button = manual_input_button
        self.number_of_color = number_of_color
        self.one_color = one_color
        self.two_color = two_color
        self.three_color = three_color
        self.four_color = four_color
        self.five_color = five_color
        self.color_option = color_option
        self.Main_color_radio = Main_color_radio
        self.secondary_color = secondary_color
        self.decorative_color_1 = decorative_color_1
        self.decorative_color_2 = decorative_color_2
        self.decorative_color_3 = decorative_color_3
        self.last_suggested_colors = last_suggested_colors
        self.color_options = color_options
        self.placement_radios = placement_radios
        self.deep_colors_executed = False
        self.light_colors_executed = False

        self.import_button = CustomButton(self.blue_frame, text="Import", bg='white', width=8, command=self.import_colors)
        self.suggest_button = CustomButton(self.blue_frame, text="Suggest", bg='white', width=8, command=self.suggest_colors)
        self.random_button = CustomButton(self.blue_frame, text="Random", bg='white', width=8, command=self.random_colors)
        self.reset_button = CustomButton(self.blue_frame, text="Delete", bg='white', width=8, command=self.reset_colors)
        self.manual_input_button = CustomButton(self.blue_frame, text="Manual", bg='white', width=8, command=self.manual_input_color)
        self.import_button.place(anchor="s", relx=0, rely=1, x=340, y=-75)
        self.suggest_button.place(anchor="s", relx=0, rely=1, x=440, y=-75)
        self.random_button.place(anchor="s", relx=0, rely=1, x=140, y=-75)
        self.reset_button.place(anchor="s", relx=0, rely=1, x=540, y=-75)
        self.manual_input_button.place(anchor="s", relx=0, rely=1, x=240, y=-75)
        self.number_of_color = tk.StringVar()
        self.number_of_color.set("1 color")
        self.one_color = tk.Radiobutton(self.blue_frame, text="1 color", variable=self.number_of_color, value="1 color", command=self.check_option)
        self.two_color = tk.Radiobutton(self.blue_frame, text="2 color", variable=self.number_of_color, value="2 color", command=self.check_option)
        self.three_color = tk.Radiobutton(self.blue_frame, text="3 color", variable=self.number_of_color, value="3 color", command=self.check_option)
        self.four_color = tk.Radiobutton(self.blue_frame, text="4 color", variable=self.number_of_color, value="4 color", command=self.check_option)
        self.five_color = tk.Radiobutton(self.blue_frame, text="5 color", variable=self.number_of_color, value="5 color", command=self.check_option)
        self.one_color.place(in_=self.blue_frame, anchor="n", relx=0.2, rely=0.25)
        self.two_color.place(in_=self.blue_frame, anchor="n", relx=0.35, rely=0.25)
        self.three_color.place(in_=self.blue_frame, anchor="n", relx=0.5, rely=0.25)
        self.four_color.place(in_=self.blue_frame, anchor="n", relx=0.65, rely=0.25)
        self.five_color.place(in_=self.blue_frame, anchor="n", relx=0.8, rely=0.25)
        self.color_option = tk.StringVar()
        self.color_option.set("first")
        self.Main_color_radio = tk.Radiobutton(self.blue_frame, text="first", variable=self.color_option, value="first")
        self.secondary_color = tk.Radiobutton(self.blue_frame, text="second", variable=self.color_option, value="second")
        self.decorative_color_1 = tk.Radiobutton(self.blue_frame, text="third", variable=self.color_option, value="third")
        self.decorative_color_2 = tk.Radiobutton(self.blue_frame, text="fourth", variable=self.color_option, value="fourth")
        self.decorative_color_3 = tk.Radiobutton(self.blue_frame, text="fifth", variable=self.color_option, value="fifth")
        self.Main_color_radio.place(in_=self.blue_frame, anchor="n", relx=0.2, rely=0.7)
        self.secondary_color.place(in_=self.blue_frame, anchor="n", relx=0.35, rely=0.7)
        self.decorative_color_1.place(in_=self.blue_frame, anchor="n", relx=0.5, rely=0.7)
        self.decorative_color_2.place(in_=self.blue_frame, anchor="n", relx=0.65, rely=0.7)
        self.decorative_color_3.place(in_=self.blue_frame, anchor="n", relx=0.8, rely=0.7)
        self.last_suggested_colors = []
        self.color_options = ["1 color", "2 color", "3 color", "4 color", "5 color"]
        self.placement_radios = [self.Main_color_radio, self.secondary_color, self.decorative_color_1, self.decorative_color_2, self.decorative_color_3]

    def import_colors(self):
        try:
            selected_color = self.color_option.get()
            color = colorchooser.askcolor()
            if color and color[1]:
                if selected_color == "first":
                    self.colors[0] = color[1]
                    self.Main_color_label.config(text=self.rgb_to_hex_import(color), bg=color[1])
                elif selected_color == "second":
                    self.colors[1] = color[1]
                    self.secondary_color_label.config(text=self.rgb_to_hex_import(color), bg=color[1])
                elif selected_color == "third":
                    self.colors[2] = color[1]
                    self.decorative_color_1_label.config(text=self.rgb_to_hex_import(color), bg=color[1])
                elif selected_color == "fourth":
                    self.colors[3] = color[1]
                    self.decorative_color_2_label.config(text=self.rgb_to_hex_import(color), bg=color[1])
                elif selected_color == "fifth":
                    self.colors[4] = color[1]
                    self.decorative_color_3_label.config(text=self.rgb_to_hex_import(color), bg=color[1])
            self.update_labels()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while importing colors: {e}")

    def manual_input_color(self):
        try:
            selected_color = self.color_option.get()
            color_input = simpledialog.askstring("Input Color", "Enter color in #RRGGBB format:")
            if color_input and self.is_valid_hex_color(color_input):
                color_index = ["first", "second", "third", "fourth", "fifth"].index(selected_color)
                self.colors[color_index] = color_input
                self.update_labels()
            else:
                messagebox.showerror("Error", "Invalid color input. Please use the #RRGGBB format.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while manually inputting color: {e}")

    def is_valid_hex_color(self, color_str):
        if not color_str:
            return False
        return bool(re.match(r"^#[A-Fa-f0-9]{6}$", color_str))


    def suggest_colors(self):
        try:
            num_colors = self.color_options.index(self.number_of_color.get()) + 1

            if num_colors == 1:
                self.show_popup_message("One color for UI is too simple. \nSuggest you try to use Layer program for more options.")
                return  

            if self.colors[0]:
                main_color_rgb = self.hex_to_rgb(self.colors[0])
                main_color_hsv = colorsys.rgb_to_hsv(*[x/255.0 for x in main_color_rgb])
                suggested_colors = []
                for i in range(1, num_colors):
                    hue_offset = (main_color_hsv[0] + 0.1 * i) % 1
                    new_color_hsv = (hue_offset, main_color_hsv[1], main_color_hsv[2])
                    new_color_rgb = colorsys.hsv_to_rgb(*new_color_hsv)
                    suggested_color = self.rgb_to_hex([int(x * 255) for x in new_color_rgb])
                    if self.colors[i] == suggested_color or self.colors[i] == "#FFFFFF":
                        suggested_colors.append(f"{self.colors[i]} (Perfect Color)")
                    else:
                        suggested_colors.append(suggested_color)
                if all('(Perfect Color)' in color for color in suggested_colors):
                    self.show_popup_message("Current colors are already perfect")
                else:
                    self.show_suggested_colors_popup(suggested_colors)
            else:
                self.show_popup_message("Please select a main color first.")
        except Exception as e:
            messagebox.showerror("Error", f"Error suggesting colors: {e}")

    def show_suggested_colors_popup(self, suggested_colors):
        try:
            popup_message = ""
            color_labels = ["second", "third", "fourth", "fifth"]
            for i, color in enumerate(suggested_colors, start=1):
                if i <= len(color_labels):
                    if '(Perfect Color)' in color:
                        perfect_color = color.replace(' (Perfect Color)', '')
                        popup_message += f"{color_labels[i-1]}: {perfect_color} (Already Perfect), "
                    else:
                        popup_message += f"{color_labels[i-1]}: {color}, "
            popup_message = popup_message.rstrip(', ')
            self.show_popup_message("Suggested colors:"  + popup_message+"\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error showing suggested colors popup: {e}\n")

    def generate_analogous_colors(self, base_rgb, num_colors):
        try:
            hue_step = 30
            base_hsv = colorsys.rgb_to_hsv(*base_rgb)
            analogous_colors = []
            for i in range(1, num_colors + 1):
                offset = (base_hsv[0] + i * hue_step) % 360
                hsv = (offset / 360.0, base_hsv[1], base_hsv[2])
                rgb = colorsys.hsv_to_rgb(*hsv)
                analogous_colors.append(tuple(int(x * 255) for x in rgb))
            return analogous_colors
        except Exception as e:
            messagebox.showerror("Error", f"Error generating analogous colors: {e}")

    def generate_suggested_colors(self, current_colors):
        try:
            suggested_colors = []
            for color in current_colors:
                rgb_color = self.hex_to_rgb(color)
                complementary_color = self.get_complementary_color(rgb_color)
                suggested_color = self.rgb_to_hex(complementary_color)
                if self.is_color_good(color, suggested_color):
                    message = f"Color combination is great! Suggested color: {suggested_color}\n"
                else:
                    message = f"Color combination is not ideal. Suggested color: {suggested_color}\n"
                self.show_popup_message(message)
                suggested_colors.append(suggested_color)
            return suggested_colors
        except Exception as e:
            messagebox.showerror("Error", f"Error generating suggested colors: {e}\n")

    def generate_complementary_scheme(self, color):
        try:
            rgb_color = self.hex_to_rgb(color)
            complementary_color = self.get_complementary_color(rgb_color)
            return [self.rgb_to_hex(complementary_color)]
        except Exception as e:
            messagebox.showerror("Error", f"Error generating complementary color scheme: {e}")

    def generate_split_complementary_scheme(self, colors):
        try:
            base_color = self.hex_to_rgb(colors[0])
            complementary_color = self.get_complementary_color(base_color)

            split_colors = [self.adjust_color(complementary_color), self.adjust_color(complementary_color)]
            return [self.rgb_to_hex(color) for color in split_colors]
        except Exception as e:
            messagebox.showerror("Error", f"Error generating split complementary color scheme: {e}")

    def show_popup_message(self, message):
        try:
            print(f"Attempting to show popup message: {message}")
            print(f"Showing popup message: {message}")
            popup = tk.Toplevel(self.root)
            popup.title("Color Combination Suggestions")
            popup.geometry('400x100+500+300')
            label = tk.Label(popup, text=message, padx=10, pady=10)
            label.pack()

            close_button = tk.Button(popup, text="Close", command=popup.destroy)
            close_button.pack()

            popup.lift()
            popup.attributes('-topmost', True)
            popup.focus_set()
            popup.wait_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying popup message: {e}")

    def is_color_good(self):
        try:
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error checking if color is good: {e}")

    def random_colors(self):
        try:
            random_color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))

            selected_color = self.color_option.get()
            if selected_color == "first":
                self.colors[0] = self.rgb_to_hex_random(random_color)
                self.Main_color_label.config(text=self.colors[0], bg=self.colors[0])
            elif selected_color == "second":
                self.colors[1] = self.rgb_to_hex_random(random_color)
                self.secondary_color_label.config(text=self.colors[1], bg=self.colors[1])
            elif selected_color == "third":
                self.colors[2] = self.rgb_to_hex_random(random_color)
                self.decorative_color_1_label.config(text=self.colors[2], bg=self.colors[2])
            elif selected_color == "fourth":
                self.colors[3] = self.rgb_to_hex_random(random_color)
                self.decorative_color_2_label.config(text=self.colors[3], bg=self.colors[3])
            elif selected_color == "fifth":
                self.colors[4] = self.rgb_to_hex_random(random_color)
                self.decorative_color_3_label.config(text=self.colors[4], bg=self.colors[4])
        except Exception as e:
            messagebox.showerror("Error", f"Error generating random colors: {e}")

    def reset_colors(self):
        try:
            selected_color = self.color_option.get()
            if selected_color == "first":
                self.colors[0] = ""
                self.Main_color_label.config(text="first", bg="white")
            elif selected_color == "second":
                self.colors[1] = ""
                self.secondary_color_label.config(text="second", bg="white")
            elif selected_color == "third":
                self.colors[2] = ""
                self.decorative_color_1_label.config(text="third", bg="white")
            elif selected_color == "fourth":
                self.colors[3] = ""
                self.decorative_color_2_label.config(text="fourth", bg="white")
            elif selected_color == "fifth":
                self.colors[4] = ""
                self.decorative_color_3_label.config(text="fifth", bg="white")
        except Exception as e:
            messagebox.showerror("Error", f"Error resetting colors: {e}")

    def check_option(self):
        try:
            selected_option = self.number_of_color.get()

            self.color_option.set("first")

            num_enabled_options = self.color_options.index(selected_option) + 1
            for i, radio in enumerate(self.placement_radios):
                radio.config(state=tk.NORMAL if i < num_enabled_options else tk.DISABLED)

            self.update_labels()
        except Exception as e:
            messagebox.showerror("Error", f"Error checking options: {e}")

    def update_labels(self):
        try:
            labels = [
                self.Main_color_label,
                self.secondary_color_label,
                self.decorative_color_1_label,
                self.decorative_color_2_label,
                self.decorative_color_3_label
            ]
            for i, label in enumerate(labels):
                if self.colors[i] and self.is_valid_hex_color(self.colors[i]):
                    label.config(bg=self.colors[i], text=self.colors[i])
                else:
                    label.config(bg="white", text=['first', 'second', 'third', 'fourth', 'fifth'][i])
        except Exception as e:
            messagebox.showerror("Error", f"Error updating labels: {str(e)}")

    def rgb_to_hex_random(self, color):
        try:
            return "#{:02X}{:02X}{:02X}".format(int(color[0]), int(color[1]), int(color[2]))
        except Exception as e:
            messagebox.showerror("Error", f"Error converting RGB to hexadecimal: {e}")

    def rgb_to_hex_import(self, color):
        try:
            if color and isinstance(color, tuple) and len(color) > 0 and isinstance(color[0], tuple):
                return "#{:02X}{:02X}{:02X}".format(int(color[0][0]), int(color[0][1]), int(color[0][2]))
            else:
                return None  #or #FFFF
        except Exception as e:
            messagebox.showerror("Error", f"Error converting imported RGB to hexadecimal: {e}")
            return None

    def hex_to_rgb(self, hex_color):
        try:
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            messagebox.showerror("Error", "Invalid hexadecimal color format")
        except Exception as e:
            messagebox.showerror("Error", f"Error converting hexadecimal to RGB: {e}")

    def rgb_to_hex(self, rgb_color):
        try:
            return "#{:02X}{:02X}{:02X}".format(*rgb_color)
        except Exception as e:
            messagebox.showerror("Error", f"Error converting RGB to hexadecimal: {e}")

    def adjust_color(self, rgb_color):
        try:
            adjusted_color = [min(255, max(0, value + np.random.randint(-20, 20))) for value in rgb_color]
            return tuple(adjusted_color)
        except Exception as e:
            messagebox.showerror("Error", f"Error adjusting color: {e}")

    def get_complementary_color(self, rgb_color):
        try:
            hsv_color = colorsys.rgb_to_hsv(*[x/255.0 for x in rgb_color])
            complementary_hue = (hsv_color[0] + 0.5) % 1.0
            complementary_hsv = (complementary_hue, hsv_color[1], hsv_color[2])
            complementary_rgb = colorsys.hsv_to_rgb(*complementary_hsv)
            return self.rgb_to_hex([int(x * 255) for x in complementary_rgb])
        except Exception as e:
            messagebox.showerror("Error", f"Error getting complementary color: {e}")

    def generate_color_palette(self, base_color, num_colors):
        try:
            palette = [base_color]
            for _ in range(num_colors - 1):
                new_color = tuple(np.random.randint(0, 256, size=3))
                palette.append(new_color)
            return [self.rgb_to_hex(color) for color in palette]
        except Exception as e:
            messagebox.showerror("Error", f"Error generating color palette: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = Suggestion(root)
    root.mainloop()

class Layer(UI_2,Hex):
    def __init__(self, root,import_button=None,deep_button=None,light_button=None,number_of_color=None,one_color=None,color_option=None,Main_color_radio=None,click_count=None,color_step_0=None,color_step_1=None,color_step_2=None,color_step_3=None,color_step_4=None,color_options=None,placement_radios=None ):
        super().__init__(
            root=root,
            blue_frame=None,
            white_rectangle=None,
            Main_color_label=None,
            secondary_color_label=None,
            decorative_color_1_label=None,
            decorative_color_2_label=None,
            decorative_color_3_label=None,
            colors=None
        )
        self.import_button =import_button
        self.deep_button =deep_button
        self.light_button =light_button
        self.number_of_color =number_of_color
        self.one_color =one_color
        self.color_option =color_option
        self.Main_color_radio =Main_color_radio
        self.click_count =click_count
        self.color_step_0 =color_step_0
        self.color_step_1 =color_step_1
        self.color_step_2 =color_step_2
        self.color_step_3 =color_step_3
        self.color_step_4 =color_step_4
        self.color_options =color_options
        self.placement_radios =placement_radios

        # ui
        self.import_button = CustomButton(self.blue_frame, text="import", bg='white', width=8, command=self.import_colors)
        self.deep_button = CustomButton(self.blue_frame, text="deep", bg='white', width=6, command=self.deep_colors)
        self.light_button = CustomButton(self.blue_frame, text="light", bg='white', width=6, command=self.light_colors)

        self.import_button.place(anchor="s", relx=0, rely=1, x=340, y=-45)
        self.deep_button.place(anchor="s", relx=0, rely=1, x=140, y=-75)
        self.light_button.place(anchor="s", relx=0, rely=1, x=140, y=-15)
        
        self.number_of_color = tk.StringVar()
        self.number_of_color.set("1 color")
        self.one_color = tk.Radiobutton(root, text="1 color", variable=self.number_of_color, value="1 color", command=self.check_option)

        self.one_color.place(in_=self.blue_frame, anchor="n", relx=0.2, rely=0.25)

        self.color_option = tk.StringVar()
        self.color_option.set("first")
        self.Main_color_radio = tk.Radiobutton(root, text="first", variable=self.color_option, value="first")

        self.Main_color_radio.place(in_=self.blue_frame, anchor="n", relx=0.2, rely=0.7)

        self.colors = ["", "", "", "", ""]
        self.click_count = 0
        self.color_step_0 = 20
        self.color_step_1 = 30
        self.color_step_2 = 60
        self.color_step_3 = 90
        self.color_step_4 = 120

        self.color_options = ["1 color"]
        self.placement_radios = [self.Main_color_radio]

    def import_colors(self):
        try:
            selected_option = self.number_of_color.get()
            if selected_option == "1 color":
                selected_color = self.color_option.get()
                if selected_color:
                    selected_color = self.colors[0]
                    color = colorchooser.askcolor()
                    if color:
                        self.colors[0] = color[1]
                        self.colors[1] = color[1]
                        self.colors[2] = color[1]
                        self.colors[3] = color[1]
                        self.colors[4] = color[1]
                    self.Main_color_label.config(text=self.rgb_to_hex_import(color), bg=color[1])                
            self.reset_other_labels()
        except Exception as e:
            messagebox.showerror("Error", f"Error importing colors: {e}")

    def deep_colors(self):
        try:
            base_color = self.hex_to_rgb(self.colors[0])
            for i in range(1, len(self.colors)):
                self.colors[i] = self.rgb_to_hex(self.adjust_color_intensity(base_color, -self.color_step_0 * i))
            self.update_labels()
        except ValueError:
            messagebox.showerror("Error", "Invalid color format")
        except Exception as e:
            messagebox.showerror("Error", f"Error deepening colors: {e}")

    def light_colors(self):
        try:
            base_color = self.hex_to_rgb(self.colors[0])
            for i in range(1, len(self.colors)):
                self.colors[i] = self.rgb_to_hex(self.adjust_color_intensity(base_color, self.color_step_0 * i))
            self.update_labels()
        except ValueError:
            messagebox.showerror("Error", "Invalid color format")
        except Exception as e:
            messagebox.showerror("Error", f"Error lightening colors: {e}")

    def adjust_color(self, index, change):
        try:
            if index < len(self.colors):
                rgb_color = self.hex_to_rgb(self.colors[index])
                adjusted_color = [max(0, min(255, value + change)) for value in rgb_color]
                self.colors[index] = self.rgb_to_hex(adjusted_color)
        except ValueError:
            messagebox.showerror("Error", "Invalid color format")
        except Exception as e:
            messagebox.showerror("Error", f"Error adjusting color: {e}")

    def adjust_color_intensity(self, rgb_color, change):
        try:
            return tuple(max(0, min(255, c + change)) for c in rgb_color)
        except Exception as e:
            messagebox.showerror("Error", f"Error adjusting color intensity: {e}")

    def is_valid_hex_color(self, color_str):
        try:
            return bool(re.match(r"^#[A-Fa-f0-9]{6}$", color_str))
        except Exception as e:
            messagebox.showerror("Error", f"Error validating hexadecimal color format: {e}")

    def update_labels(self):
        try:
            selected_option = self.number_of_color.get()
            if selected_option == "1 color":
                selected_color = self.color_option.get()
                if selected_color:
                    main_color = self.colors[0] if self.colors[0] else "#FFFF"
                    secondary_color = self.colors[1] if self.colors[1] else "#FFFF"
                    decorative_color_1 = self.colors[2] if self.colors[2] else "#FFFF"
                    decorative_color_2 = self.colors[3] if self.colors[3] else "#FFFF"
                    decorative_color_3 = self.colors[4] if self.colors[4] else "#FFFF"
                    self.Main_color_label.config(text=main_color, bg=main_color)
                    self.secondary_color_label.config(text=secondary_color, bg=secondary_color)
                    self.decorative_color_1_label.config(text=decorative_color_1, bg=decorative_color_1)
                    self.decorative_color_2_label.config(text=decorative_color_2, bg=decorative_color_2)
                    self.decorative_color_3_label.config(text=decorative_color_3, bg=decorative_color_3)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating labels: {e}")

    def reset_other_labels(self):
        try:
            self.secondary_color_label.config(text="second", bg="white")
            self.decorative_color_1_label.config(text="third", bg="white")
            self.decorative_color_2_label.config(text="fourth", bg="white")
            self.decorative_color_3_label.config(text="fifth", bg="white")
        except Exception as e:
            messagebox.showerror("Error", f"Error resetting labels: {e}")

    def check_option(self):
        try:
            selected_option = self.number_of_color.get()
            self.color_option.set("first")
            num_enabled_options = self.color_options.index(selected_option) + 1
            for i, radio in enumerate(self.placement_radios):
                radio.config(state=tk.NORMAL if i < num_enabled_options else tk.DISABLED)
            self.update_labels()
        except Exception as e:
            messagebox.showerror("Error", f"Error checking options: {e}")

    def rgb_to_hex_import(self, color):
        return "#{:02X}{:02X}{:02X}".format(int(color[0][0]), int(color[0][1]), int(color[0][2]))

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb_color):
        return "#{:02X}{:02X}{:02X}".format(*rgb_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = Layer(root)
    root.mainloop()