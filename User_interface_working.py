import tkinter as tk
from tkinter import END, filedialog, messagebox, Button, Toplevel, Label, Entry, Frame
from PIL import Image, ImageTk
import numpy as np
import math
from Distance_calculation import Dijkstra_algorithm
from Optimization_Tool import optimization_tool
from Extensions import vehicle

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

        

        # self.save_button = tk.Button(self, text="Save Coordinates", command=self.save_coordinates)
        # self.save_button.pack(side=tk.RIGHT)

        # Variables for drawing shapes
        self.image = None
        self.original_image = None  # Store the original image for resizing
        self.image_id = None

        self.vehicle_property_names = ['Fuel consumption [L/h]', 'Speed [km/h]', 'Capacity [kg]']

        self.storage_sites = []  # Rectangles for storage sites
        self.construction_sites = []  # Rectangles for construction sites
        self.roads = []  # Lines for roads
        self.scale_line = []  # Line for scale

        self.storage_sites_centers = []  # storage sites centers
        self.construction_sites_centers = []  # construction sites centers

        self.storage_sites_ee_points = []   # storage sites possible entry/exit points
        self.construction_sites_ee_points = []  # construction sites possible entry/exit points

        self.storage_sites_ee_points_selected = []
        self.construction_sites_ee_points_selected = []

        self.storage_sites_hidden_roads = []   # storage sites entry/exit points
        self.construction_sites_hidden_roads = []  # storage sites entry/exit points

        self.amount_of_ee_points = 2

        self.current_shape = []
        self.drawing = False

        self.scale = 1   # scale in m per pixel

        # Bind mouse events for drawing
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.drawing_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        # Bind window resize event
        self.bind("<Configure>", self.on_resize)  # Handle resizing

        # Buttons for loading image and saving data
        self.load_button = tk.Button(self, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT)

        # Add a "Materials" button
        materials_button = Button(self, text="Specify Materials and Scale", command=self.open_materials_window)
        materials_button.pack(side=tk.RIGHT)

        # Rectangle/Line type selection
        self.rect_type_var = tk.StringVar(value="Roads")  # Default to Storage sites
        self.rect_type_menu = tk.OptionMenu(
            self,
            self.rect_type_var,
            "Storage sites",  # Red rectangles
            "Construction sites",  # Green rectangles
            "Roads",  # Light blue lines
            "Scale" # Orange line
        )
        self.rect_type_menu.pack(side=tk.LEFT)

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
                dot_radius = 3
                for k in range(4):
                    self.canvas.create_oval(self.storage_sites_ee_points[idx][k][0] - dot_radius, self.storage_sites_ee_points[idx][k][1] - dot_radius, self.storage_sites_ee_points[idx][k][0] + dot_radius, self.storage_sites_ee_points[idx][k][1] + dot_radius, fill='white', outline='red')

            for idx, rect in enumerate(self.construction_sites):
                self.canvas.create_rectangle(
                    rect["x1"], rect["y1"], rect["x2"], rect["y2"], outline='#00FF7F', width=4, fill = 'white'
                )
                x_center = (rect["x1"] + rect["x2"]) / 2
                y_center = (rect["y1"] + rect["y2"]) / 2
                self.canvas.create_text(x_center, y_center, text=str(idx + 1), font=('Helvetica 20 bold'), fill='black')
                dot_radius = 3
                for k in range(4):
                    self.canvas.create_oval(self.construction_sites_ee_points[idx][k][0] - dot_radius, self.construction_sites_ee_points[idx][k][1] - dot_radius, self.construction_sites_ee_points[idx][k][0] + dot_radius, self.construction_sites_ee_points[idx][k][1] + dot_radius, fill='white', outline='#00FF7F')
            
            dot_radius = 5
            for road in self.roads:
                self.canvas.create_line(
                    road["x1"], road["y1"], road["x2"], road["y2"], fill='#42bff5', width=4
                )
            
            for road in self.roads:
                self.canvas.create_oval(road["x1"] - dot_radius, road["y1"] - dot_radius, road["x1"] + dot_radius, road["y1"] + dot_radius, fill='white', outline='black')
                self.canvas.create_oval(road["x2"] - dot_radius, road["y2"] - dot_radius, road["x2"] + dot_radius, road["y2"] + dot_radius, fill='white', outline='black')
            
            for scale in self.scale_line:
                self.canvas.create_line(
                    scale["x1"], scale["y1"], scale["x2"], scale["y2"], fill='orange', width=4
                )

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
            
            elif shape_type == "Storage sites":
                outline_color = 'red'
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, width=4, tag='preview')

            elif shape_type == "Construction sites":
                outline_color = '#00FF7F'
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, width=4, tag='preview')
            
            elif shape_type == "Scale":
                outline_color = 'orange'
                self.canvas.create_line(x1, y1, x2, y2, fill='orange', width=4, tag='preview')
            
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
                # outline_color = 'red' if shape_type == "Storage sites" else '#00FF7F'
                if shape_type == "Storage sites":
                    outline_color = 'red'
                    self.storage_sites.append({
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    })
                    self.storage_sites_centers.append(((x1 + x2) / 2, (y1 + y2) / 2))
                    self.storage_sites_ee_points.append([((x1 + x2) / 2, y1), ((x1 + x2) / 2, y2), (x1, (y1 + y2) / 2), (x2, (y1 + y2) / 2)])

                    distances = []
                    for ee_point in self.storage_sites_ee_points[-1]:
                        ee_point_distances = []
                        for road in self.roads:
                            line = [road["x1"], road["y1"], road["x2"], road["y2"]]
                            ee_point_distances.append(self.distance_point_line(ee_point, line))
                        distances.append(ee_point_distances)

                    
                    ee_points = []
                    for ee_idx, ee_point_road_dist in enumerate(distances):
                        # for each point make a list containing the distance to each road and the coordinates of the road vertices
                        ee_point = self.storage_sites_ee_points[-1][ee_idx]
                        ee_road_dict_list = []

                        for idx, road in enumerate(ee_point_road_dist):
                            line = [self.roads[idx]["x1"], self.roads[idx]["y1"], self.roads[idx]["x2"], self.roads[idx]["y2"]]
                            ee_road_dict_list.append([road, line, self.storage_sites_ee_points[-1][ee_idx], idx])

                        ee_road_dict_list_sorted = self.sort_list_by_first_element(ee_road_dict_list)
                        closest_road = ee_road_dict_list_sorted[0]
                        ee_points.append(closest_road)

                    ee_points_sorted = self.sort_list_by_first_element(ee_points)
                    ee_points_cut = ee_points_sorted[0:self.amount_of_ee_points]

                    # remove_indexes = []
                    # for ee_point in ee_points_cut:
                    #     remove_indexes.append(ee_point[3])

                    # for index in sorted(remove_indexes, reverse=True):
                    #     self.roads.pop(index)

                    projected_points = []
                    for ee_point in ee_points_cut:
                        projected_points.append(self.project_point_onto_line(ee_point[2], ee_point[1]))

                        ee_main_road = {
                            "x1": projected_points[-1][0],
                            "y1": projected_points[-1][1],
                            "x2": ee_point[2][0],
                            "y2": ee_point[2][1],
                        }
                        self.roads.append(ee_main_road)

                        ee_first_road = {
                            "x1": projected_points[-1][0],
                            "y1": projected_points[-1][1],
                            "x2": ee_point[1][0],
                            "y2": ee_point[1][1],
                        }
                        self.roads.append(ee_first_road)

                        ee_second_road = {
                            "x1": projected_points[-1][0],
                            "y1": projected_points[-1][1],
                            "x2": ee_point[1][2],
                            "y2": ee_point[1][3],
                        }
                        self.roads.append(ee_second_road)

                        hidden_road = {
                            "x1": self.storage_sites_centers[-1][0],
                            "y1": self.storage_sites_centers[-1][1],
                            "x2": ee_point[2][0],
                            "y2": ee_point[2][1],
                        }

                        self.storage_sites_hidden_roads.append(hidden_road)


                elif shape_type == "Construction sites":
                    outline_color = '#00FF7F'
                    self.construction_sites.append({
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    })
                    self.construction_sites_centers.append(((x1 + x2) / 2, (y1 + y2) / 2))
                    self.construction_sites_ee_points.append([((x1 + x2) / 2, y1), ((x1 + x2) / 2, y2), (x1, (y1 + y2) / 2), (x2, (y1 + y2) / 2)])

                    distances = []
                    for ee_point in self.construction_sites_ee_points[-1]:
                        ee_point_distances = []
                        for road in self.roads:
                            line = [road["x1"], road["y1"], road["x2"], road["y2"]]
                            ee_point_distances.append(self.distance_point_line(ee_point, line))
                        distances.append(ee_point_distances)

                    
                    ee_points = []
                    for ee_idx, ee_point_road_dist in enumerate(distances):
                        # for each point make a list containing the distance to each road and the coordinates of the road vertices
                        ee_point = self.construction_sites_ee_points[-1][ee_idx]
                        ee_road_dict_list = []

                        for idx, road in enumerate(ee_point_road_dist):
                            line = [self.roads[idx]["x1"], self.roads[idx]["y1"], self.roads[idx]["x2"], self.roads[idx]["y2"]]
                            ee_road_dict_list.append([road, line, self.construction_sites_ee_points[-1][ee_idx], idx])

                        ee_road_dict_list_sorted = self.sort_list_by_first_element(ee_road_dict_list)
                        closest_road = ee_road_dict_list_sorted[0]
                        ee_points.append(closest_road)

                    ee_points_sorted = self.sort_list_by_first_element(ee_points)
                    ee_points_cut = ee_points_sorted[0:self.amount_of_ee_points]

                    # remove_indexes = []
                    # for ee_point in ee_points_cut:
                    #     remove_indexes.append(ee_point[3])

                    # for index in sorted(remove_indexes, reverse=True):
                    #     self.roads.pop(index)

                    projected_points = []
                    for ee_point in ee_points_cut:
                        projected_points.append(self.project_point_onto_line(ee_point[2], ee_point[1]))

                        ee_main_road = {
                            "x1": projected_points[-1][0],
                            "y1": projected_points[-1][1],
                            "x2": ee_point[2][0],
                            "y2": ee_point[2][1],
                        }
                        self.roads.append(ee_main_road)

                        ee_first_road = {
                            "x1": projected_points[-1][0],
                            "y1": projected_points[-1][1],
                            "x2": ee_point[1][0],
                            "y2": ee_point[1][1],
                        }
                        self.roads.append(ee_first_road)

                        ee_second_road = {
                            "x1": projected_points[-1][0],
                            "y1": projected_points[-1][1],
                            "x2": ee_point[1][2],
                            "y2": ee_point[1][3],
                        }
                        self.roads.append(ee_second_road)

                        hidden_road = {
                            "x1": self.construction_sites_centers[-1][0],
                            "y1": self.construction_sites_centers[-1][1],
                            "x2": ee_point[2][0],
                            "y2": ee_point[2][1],
                        }

                        self.construction_sites_hidden_roads.append(hidden_road)

                    self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, width=4)
                
                elif shape_type == "Scale":
                    outline_color = 'orange'
                    self.scale_line.append({
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    })

                    self.canvas.create_line(x1, y1, x2, y2, fill='orange', width=4)


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

        # Specify the name of each material
        Label(self.materials_names_window, text="Specify the name of each material").pack()

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
        self.open_vehicles_window()

    def open_materials_window(self):
        # Create a new window
        self.materials_window = Toplevel(self)

        # Add a label and an entry for the number of materials
        frame0 = tk.Frame(self.materials_window)
        frame0.pack(fill='x')
        Label(frame0, text="Number of materials:").pack(side='left')
        self.materials_entry = Entry(frame0)
        self.materials_entry.pack(side='right')

        # Specify the scale
        frame1 = tk.Frame(self.materials_window)
        frame1.pack(fill='x')
        Label(frame1, text="Scale bar length in meters:").pack(side='left')
        self.scale_entry = Entry(frame1)
        self.scale_entry.pack(side='right')

        # Add a label and an entry for the maximum number of sites a material may be spread over
        frame2 = tk.Frame(self.materials_window)
        frame2.pack(fill='x')
        Label(frame2, text="Maximum number of sites a material may be spread over:").pack(side='left')
        self.max_sites_entry = Entry(frame2)
        self.max_sites_entry.pack(side='right')

        # Add a label and an entry for the maximum materials that can be stored at a storage site
        frame3 = tk.Frame(self.materials_window)
        frame3.pack(fill='x')
        Label(frame3, text="Maximum materials that can be stored at a storage site in kilograms:").pack(side='left')
        self.max_storage_possible_entry = Entry(frame3)
        self.max_storage_possible_entry.pack(side='right')

        # Add a "Submit" button
        Button(self.materials_window, text="Submit", command=self.submit_materials).pack()

    def submit_materials(self):
        # Get the number of materials from the entry
        self.num_materials = int(self.materials_entry.get())

        # Get the scale from the entry
        self.scale = float(self.scale_entry.get()) / abs(self.scale_line[0]["x1"] - self.scale_line[0]["x2"])

        # Get the maximum number of sites a material may be spread over
        self.max_sites = int(self.max_sites_entry.get())

        # Get the maximum materials that can be stored at a storage site
        self.max_storage_possible = int(self.max_storage_possible_entry.get())

        # Close the materials window
        self.materials_window.destroy()

        # Open the materials names window
        self.open_materials_names_window()

    def submit_sites(self):
        self.site_materials = np.zeros((len(self.construction_sites), self.num_materials))
        # Get the materials for each site from the entries
        for i in range(len(self.construction_sites)):
            for j in range(self.num_materials):
                # Get the quantity of the material at the site
                quantity = float(self.site_entries[i][j].get())

                # Add the quantity to the list for the material
                self.site_materials[i,j] = quantity

        # Close the sites window
        self.sites_window.destroy()

        # Open the results window
        self.open_results_window()

    def open_sites_window(self):
        # Create a new window
        self.sites_window = Toplevel(self)

        # Create a title label
        Label(self.sites_window, text="Enter the amount of each material in metric tons").pack()

        self.site_entries = []
        # Create a section for each construction site
        for i in range(len(self.construction_sites)):
            site_frame = Frame(self.sites_window)
            site_frame.pack(fill='x', padx=5, pady=5)
            Label(site_frame, text=f"Construction Site {i+1}").pack()

            # Create an input form for each material in each section
            self.site_entries_ind = []
            for j in range(self.num_materials):
                material_frame = Frame(site_frame)
                material_frame.pack(fill='x')

                Label(material_frame, text=self.materials_names[j]).pack(side='left')
                entry = Entry(material_frame)
                entry.pack(side='right')
                self.site_entries_ind.append(entry)
            
            self.site_entries.append(self.site_entries_ind)

        Button(self.sites_window, text="Submit", command=self.submit_sites).pack()

    def distance_point_line(self, point, line):
        x0, y0 = point
        x1, y1, x2, y2 = line

        # Calculate the distance from the point to the line defined by the two points
        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominator = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
        distance_to_line = numerator / denominator

        # Check if the perpendicular from the point to the line falls within the line segment
        dotproduct = (x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)
        length_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2

        if dotproduct < 0 or dotproduct > length_squared:
            # The perpendicular does not fall within the line segment, return the minimum distance to either point
            return min(math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2), math.sqrt((x0 - x2) ** 2 + (y0 - y2) ** 2))
        else:
            # The perpendicular falls within the line segment, return the distance to the line
            return distance_to_line

    def project_point_onto_line(self, point, line):
        x0, y0 = point
        x1, y1, x2, y2 = line

        # Calculate the vectors
        line_vector = [x2 - x1, y2 - y1]
        point_vector = [x0 - x1, y0 - y1]

        # Calculate the proportion along the line that the projection falls
        proportion = (point_vector[0] * line_vector[0] + point_vector[1] * line_vector[1]) / (line_vector[0] ** 2 + line_vector[1] ** 2)

        # Calculate the coordinates of the projection
        projection = [x1 + proportion * line_vector[0], y1 + proportion * line_vector[1]]

        return projection

    def sort_list_by_first_element(self, lst):
        return sorted(lst, key=lambda sublist: sublist[0])

    def open_results_window(self):
        # Create a new window
        self.results_window = Toplevel(self)

        # combine all (hidden) roads
        self.all_roads = self.roads + self.storage_sites_hidden_roads + self.construction_sites_hidden_roads

        # Determine the distance between each construction site and storage site
        distances = Dijkstra_algorithm(self.all_roads, self.construction_sites_centers, self.storage_sites_centers, scale=self.scale)

        construction_coordinates = np.array(self.construction_sites_centers)  
        construction_sites_materials = np.array(self.site_materials) * 1000  # tons to kg
        storage_coordinates = np.array(self.storage_sites_centers)
        materials = self.materials_names
        vehicles = self.vehicles
        max_sites = self.max_sites
        max_storage_possible = self.max_storage_possible

        # Call the optimization tool
        materials_per_site = optimization_tool(construction_coordinates=construction_coordinates, construction_sites_materials=construction_sites_materials, storage_coordinates=storage_coordinates, materials=materials, distances=distances, vehicles=vehicles, max_sites=max_sites, max_storage_possible=max_storage_possible)

        # Print the results
        # print(materials_per_site)

        # code for creating table
        for i in range(materials_per_site.shape[0] + 1):
            row_frame = tk.Frame(self.results_window)  # create a new frame for each row
            row_frame.pack(fill='x')  # pack the frame into the parent widget

            for j in range(materials_per_site.shape[1] + 1):
                if i == 0 and not j == 0:
                    e = tk.Entry(row_frame, width=20, fg='black',
                                 font=('Arial',16,'bold'), bg='light grey', justify='center')
                    e.pack(side='left')  # pack the entry into the row frame
                    e.insert(tk.END, str(materials[j-1])+' [kg]')
                
                elif j == 0 and not i == 0:
                    e = tk.Entry(row_frame, width=20, fg='black',
                                 font=('Arial',16,'bold'), bg='light grey')
                    e.pack(side='left')  # pack the entry into the row frame
                    e.insert(tk.END, 'Storage site ' + str(i))

                elif i == 0 and j == 0:
                    e = tk.Entry(row_frame, width=20, fg='black',
                                 font=('Arial',16,'bold'), bg='light grey')
                    e.pack(side='left')  # pack the entry into the row frame
                    e.insert(tk.END, '')
                    
                else:
                    e = tk.Entry(row_frame, width=20, fg='black',
                                 font=('Arial',16), justify='center')
                    e.pack(side='left')  # pack the entry into the row frame
                    e.insert(tk.END, str(materials_per_site[i-1][j-1]))

    def open_vehicles_window(self):
        # create a new window
        self.vehicle_window = Toplevel(self)

        # Create a title label
        Label(self.vehicle_window, text="Enter the properties of each vehicle").pack()

        self.vehicle_entries = []

        # Create a section for each material
        for i in range(self.num_materials):
            vehicle_frame = Frame(self.vehicle_window)
            vehicle_frame.pack(fill='x', padx=5, pady=5)
            Label(vehicle_frame, text=f"{self.materials_names[i]} vehicle").pack()

            # Create an input form for each property of the vehicle
            self.vehicle_entries_ind = []
            for j in range(3):
                property_frame = Frame(vehicle_frame)
                property_frame.pack(fill='x')

                Label(property_frame, text=self.vehicle_property_names[j]).pack(side='left')
                entry = Entry(property_frame)
                entry.pack(side='right')
                self.vehicle_entries_ind.append(entry)
            
            self.vehicle_entries.append(self.vehicle_entries_ind)

        # Add a "Submit" button
        Button(self.vehicle_window, text="Submit", command=self.submit_vehicles).pack()
    
    def submit_vehicles(self):
        self.vehicle_properties = np.zeros((self.num_materials, len(self.vehicle_property_names)))

        self.vehicles = []

        # Get the materials for each site from the entries
        for i in range(self.num_materials):
            material_vehicle = vehicle(fuel_consumption=float(self.vehicle_entries[i][0].get()), speed=float(self.vehicle_entries[i][1].get()), material=self.materials_names[i], capacity=float(self.vehicle_entries[i][2].get()))
            self.vehicles.append(material_vehicle)

        # Close the sites window
        self.vehicle_window.destroy()

        # Open the sites window
        self.open_sites_window()

# Run the application
if __name__ == "__main__":
    app = DrawShapesApp()
    app.mainloop()