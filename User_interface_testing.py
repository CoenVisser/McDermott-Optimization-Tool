import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import math

# Threshold for connecting nearby endpoints
CONNECTION_THRESHOLD = 100  # Adjust this as needed

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

        self.save_button = tk.Button(self, text="Save Coordinates", command=self.save_coordinates)
        self.save_button.pack(side=tk.RIGHT)

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
            x_center = (current_width - new_width) // 2
            y_center = (current_height - new_height) // 2

            # Clear canvas and draw the centered image
            self.canvas.delete("all")
            self.image_id = self.canvas.create_image(x_center, y_center, anchor=tk.NW, image=self.image)

            # Redraw previous shapes with correct colors and thickness
            for rect in self.storage_sites:
                self.canvas.create_rectangle(
                    rect["x1"], rect["y1"], rect["x2"], rect["y2"], outline='red', width=2
                )
            for rect in self.construction_sites:
                self.canvas.create_rectangle(
                    rect["x1"], rect["y1"], rect["x2"], rect["y2"], outline='#00FF7F', width=2
                )
            for road in self.roads:
                self.canvas.create_line(
                    road["x1"], road["y1"], road["x2"], road["y2"], fill='light blue', width=2
                )

    def find_closest_line(self, x1, y1):
        """Find the closest existing road line's endpoint to the given point"""
        closest_distance = CONNECTION_THRESHOLD
        closest_index = -1
        closest_point = None

        for index, road in enumerate(self.roads):
            # Calculate distances to the start and end of the road line
            dist_to_start = math.sqrt((x1 - road["x1"])**2 + (y1 - road["y1"])**2)
            dist_to_end = math.sqrt((x1 - road["x2"])**2 + (y1 - road["y2"])**2)

            # Find the closest point and distance
            if dist_to_start < closest_distance:
                closest_distance = dist_to_start
                closest_index = index
                closest_point = (road["x1"], road["y1"])
            elif dist_to_end < closest_distance:
                closest_distance = dist_to_end
                closest_index = index
                closest_point = (road["x2"], road["y2"])

        return closest_index, closest_point

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

            shape_type = self.rect_type_var.get()
            if shape_type == "Roads":
                self.canvas.create_line(x1, y1, x2, y2, fill='light blue', width=2, tag='preview')
            else:
                outline_color = 'red' if shape_type == "Storage sites" else '#00FF7F'
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, width=2, tag='preview')

    def end_draw(self, event):
        if self.drawing:
            self.drawing = False
            self.current_shape.append((event.x, event.y))
            x1, y1 = self.current_shape[0]
            x2, y2 = event.x, event.y

            shape_type = self.rect_type_var.get()

            if shape_type == "Roads":
                # Find the closest existing road line to connect to
                closest_index, closest_point = self.find_closest_line(x2, y2)

                # Draw a new connected line if there's a close point
                if closest_point:
                    self.roads.append({
                        "x1": x1,
                        "y1": y1,
                        "x2": closest_point[0],
                        "y2": closest_point[1],
                    })
                    self.canvas.create_line(x1, y1, closest_point[0], closest_point[1], fill='light blue', width=2)
                    
                    # Delete the old unconnected lines
                    if closest_index >= 0:
                        self.roads.pop(closest_index)
                        self.canvas.delete("all")  # Clear all shapes to update the view
                        self.update_image_display()  # Redraw with updated road lines
                else:
                    # If no connection, draw a normal line
                    self.roads.append({
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    })
                    self.canvas.create_line(x1, y1, x2, y2, fill='light blue', width=2)
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
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, width=2)

    def save_coordinates(self):
        if self.storage_sites or self.construction_sites or self.roads:
            # Create numpy arrays for rectangle coordinates and road lines
            storage_site_coords = np.array([[rect["x1"], rect["y1"], rect["x2"], "y2"]
                                           for rect in self.storage_sites])
            construction_site_coords = np.array([[rect["x1"], rect["y1"], rect["x2"], "y2"]
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

# Run the application
if __name__ == "__main__":
    app = DrawShapesApp()
    app.mainloop()
