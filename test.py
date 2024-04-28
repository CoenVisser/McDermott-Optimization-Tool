import tkinter as tk
import numpy as np

class Table:
    def __init__(self, root):
        # code for creating table
        for i in range(materials_per_site.shape[0] + 1):
            row_frame = tk.Frame(root)  # create a new frame for each row
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

# take the data
materials = np.array(['A', 'B', 'C'])
materials_per_site = np.array([[3, 2, 1],
       [4, 5, 6],
       [7, 8, 9]])

# create root window
root = tk.Tk()
t = Table(root)
root.mainloop()