import tkinter as tk
from tkinter import filedialog, messagebox, Button, Toplevel, Label, Entry, Frame
from PIL import Image, ImageTk
import numpy as np
import io

# Application class
class DrawShapesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Plot Plan Drawer")

        # Canvas for displaying and drawing on the image
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(self, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Buttons for loading image and saving data
        self.load_button = tk.Button(self, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT)

        # self.save_button = tk.Button(self, text="Save Coordinates", command=self.save_coordinates)
        # self.save_button.pack(side=tk.RIGHT)

        # Rectangle/Line type selection
        self.rect_type_var = tk.StringVar(value="Storage sites")  # Default to Storage sites
        self.rect_type_menu = tk.OptionMenu(
            self,
            self.rect_type_var,
            "Storage sites",  # Red rectangles
            "Construction sites",  # Green rectangles
            "Roads"  # Light blue lines
        )
        self.rect_type_menu.pack(side=tk.LEFT)

        # Variables for drawing shapes
        self.image = None
        self.original_image = None  # Store the original image for resizing
        self.image_id = None
        self.storage_sites = []  # Rectangles for storage sites
        self.construction_sites = []  # Rectangles for construction sites
        self.roads = []  # Lines for roads
        self.current_shape = []
        self.drawing = False

        # Bind mouse events for drawing
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.drawing_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        # Bind window resize event
        self.bind("<Configure>", self.on_resize)  # Handle resizing

        # Add a "Materials" button
        materials_button = Button(self, text="Materials", command=self.open_materials_window)
        materials_button.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            image = Image.open(file_path)

            # Store the original image for future resizing
            self.original_image = image.copy()

            # Resize the image to fit within the initial canvas
            self.update_image_display()

    def update_image_display(self):
        if self.original_image:
            # Determine the new canvas dimensions
            current_width = self.canvas.winfo_width()
            current_height = self.canvas.winfo_height()

            # Maintain aspect ratio of the image
            aspect_ratio = self.original_image.width / self.original_image.height
            if current_width / current_height > aspect_ratio:
                new_height = current_height
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = current_width
                new_height = int(new_width / aspect_ratio)

            # Resize the image while keeping aspect ratio
            resized_image = self.original_image.resize(
                (new_width, new_height)
            )
            self.image = ImageTk.PhotoImage(resized_image)

            # Calculate the centered position
            self.x_center = (current_width - new_width) // 2
            self.y_center = (current_height - new_height) // 2

            # Clear canvas and draw the centered image
            self.canvas.delete("all")
            self.image_id = self.canvas.create_image(self.x_center, self.y_center, anchor=tk.NW, image=self.image)

            # Redraw previous shapes with correct colors and thickness
            for idx, rect in enumerate(self.storage_sites):
                self.canvas.create_rectangle(
                    rect["x1"], rect["y1"], rect["x2"], rect["y2"], outline='red', width=4, fill = 'white'
                )
                x_center = (rect["x1"] + rect["x2"]) / 2
                y_center = (rect["y1"] + rect["y2"]) / 2
                self.canvas.create_text(x_center, y_center, text=str(idx + 1), fill='black', font=('Helvetica 20 bold'))

            for idx, rect in enumerate(self.construction_sites):
                self.canvas.create_rectangle(
                    rect["x1"], rect["y1"], rect["x2"], rect["y2"], outline='#00FF7F', width=4, fill = 'white'
                )
                x_center = (rect["x1"] + rect["x2"]) / 2
                y_center = (rect["y1"] + rect["y2"]) / 2
                self.canvas.create_text(x_center, y_center, text=str(idx + 1), font=('Helvetica 20 bold'), fill='black')
            
            dot_radius = 5
            for road in self.roads:
                self.canvas.create_line(
                    road["x1"], road["y1"], road["x2"], road["y2"], fill='#42bff5', width=4
                )
                self.canvas.create_oval(road["x1"] - dot_radius, road["y1"] - dot_radius, road["x1"] + dot_radius, road["y1"] + dot_radius, fill='white', outline='black')
                self.canvas.create_oval(road["x2"] - dot_radius, road["y2"] - dot_radius, road["x2"] + dot_radius, road["y2"] + dot_radius, fill='white', outline='black')
                

    def on_resize(self, event):
        # Recalculate the image size and position upon window resizing
        self.update_image_display()

    def start_draw(self, event):
        self.drawing = True
        self.current_shape = [(event.x, event.y)]

    def drawing_motion(self, event):
        if self.drawing:
            self.canvas.delete("preview")
            x1, y1 = self.current_shape[0]
            x2, y2 = event.x, event.y

            shape_type = self.rect_type_var.get()  # Get current drawing type
            if shape_type == "Roads":
                self.canvas.create_line(x1, y1, x2, y2, fill='#42bff5', width=4, tag='preview')
            else:
                outline_color = 'red' if shape_type == "Storage sites" else '#00FF7F'
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, width=4, tag='preview')

    def end_draw(self, event):
        if self.drawing:
            self.drawing = False
            self.current_shape.append((event.x, event.y))
            x1, y1 = self.current_shape[0]
            x2, y2 = event.x, event.y

            shape_type = self.rect_type_var.get()

            if shape_type == "Roads":
                new_road = {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                }

                # Define a threshold for how close points should be to be considered the same
                threshold = 15  # Adjust this value as needed

                for road in self.roads:
                    for new_point, point in [((x1, y1), (road["x1"], road["y1"])),
                                            ((x1, y1), (road["x2"], road["y2"])),
                                            ((x2, y2), (road["x1"], road["y1"])),
                                            ((x2, y2), (road["x2"], road["y2"]))]:
                        # Calculate Euclidean distance
                        distance = ((new_point[0] - point[0]) ** 2 + (new_point[1] - point[1]) ** 2) ** 0.5
                        if distance < threshold:
                            # Replace the new point with the existing point
                            if new_point == (x1, y1):
                                new_road["x1"], new_road["y1"] = point
                            else:
                                new_road["x2"], new_road["y2"] = point

                self.roads.append(new_road)
                self.canvas.create_line(new_road["x1"], new_road["y1"], new_road["x2"], new_road["y2"], fill='#42bff5', width=4)

            else:
                outline_color = 'red' if shape_type == "Storage sites" else '#00FF7F'
                if shape_type == "Storage sites":
                    self.storage_sites.append({
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    })
                elif shape_type == "Construction sites":
                    self.construction_sites.append({
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    })

                self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, width=4)

            # refresh the canvas
            self.update_image_display()

    def save_coordinates(self):
        if self.storage_sites or self.construction_sites or self.roads:
            # Create numpy arrays for rectangle coordinates
            storage_site_coords = np.array([[rect["x1"], rect["y1"], rect["x2"], rect["y2"]]
                                           for rect in self.storage_sites])
            construction_site_coords = np.array([[rect["x1"], rect["y1"], rect["x2"], rect["y2"]]
                                               for rect in self.construction_sites])
            road_coords = np.array([[road["x1"], road["y1"], road["x2"], road["y2"]]
                                  for road in self.roads])

            # File dialog for saving each numpy array
            file_path_storage = filedialog.asksaveasfilename(
                title="Save Storage Site Coordinates",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )
            if file_path_storage:
                np.savetxt(file_path_storage, storage_site_coords, fmt='%d', delimiter=',')  # Save as CSV

            file_path_construction = filedialog.asksaveasfilename(
                title="Save Construction Site Coordinates",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )
            if file_path_construction:
                np.savetxt(file_path_construction, construction_site_coords, fmt='%d', delimiter=',')  # Save as CSV

            file_path_roads = filedialog.asksaveasfilename(
                title="Save Road Coordinates",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )
            if file_path_roads:
                np.savetxt(file_path_roads, road_coords, fmt='%d', delimiter=',')  # Save as CSV

        else:
            messagebox.showinfo("No Shapes", "No shapes to save.")

    def open_materials_names_window(self):
        # Create a new window
        self.materials_names_window = Toplevel(self)

        # Create an input form for each material
        self.materials_name_entries = []
        for i in range(self.num_materials):
            material_frame = Frame(self.materials_names_window)
            material_frame.pack(fill='x')

            Label(material_frame, text=f"Material {i+1}:").pack(side='left')
            entry = Entry(material_frame)
            entry.pack(side='left')
            self.materials_name_entries.append(entry)

        # Add a "Submit" button
        Button(self.materials_names_window, text="Submit", command=self.submit_materials_names).pack()

    def submit_materials_names(self):
        # Get the names of the materials from the entries
        self.materials_names = [entry.get() for entry in self.materials_name_entries]

        # Close the materials names window
        self.materials_names_window.destroy()

        # Open the sites window
        self.open_sites_window()
        print(self.materials_names)

    def open_materials_window(self):
        # Create a new window
        self.materials_window = Toplevel(self)

        # Add a label and an entry for the number of materials
        Label(self.materials_window, text="Number of materials:").pack()
        self.materials_entry = Entry(self.materials_window)
        self.materials_entry.pack()

        # Add a "Submit" button
        Button(self.materials_window, text="Submit", command=self.submit_materials).pack()

    def submit_materials(self):
        # Get the number of materials from the entry
        self.num_materials = int(self.materials_entry.get())

        # Close the materials window
        self.materials_window.destroy()

        # Open the materials names window
        self.open_materials_names_window()

    def submit_sites(self):
        # Get the materials for each site from the entries
        self.site_materials = [entry.get() for entry in self.site_entries]

        # Close the sites window
        self.sites_window.destroy()

    def open_sites_window(self):
        # Create a new window
        self.sites_window = Toplevel(self)

        # Create a title label
        Label(self.sites_window, text="Enter the amount of each material in metric tons").pack()


        # Create a section for each construction site
        for i in range(len(self.construction_sites)):
            site_frame = Frame(self.sites_window)
            site_frame.pack(fill='x', padx=5, pady=5)

            Label(site_frame, text=f"Construction Site {i+1}").pack()

            # Create an input form for each material in each section
            self.site_entries = []
            for j in range(self.num_materials):
                material_frame = Frame(site_frame)
                material_frame.pack(fill='x')

                Label(material_frame, text=self.materials_names[j]).pack(side='left')
                entry = Entry(material_frame)
                entry.pack(side='right')
                self.site_entries.append(entry)

        # Add a "Submit" button
        Button(self.sites_window, text="Submit", command=self.submit_sites).pack()



# Run the application
if __name__ == "__main__":
    app = DrawShapesApp()
    app.mainloop()
