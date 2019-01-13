import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import numpy as np

import search


w = tk.Tk()
w["bg"] = "#ffffff"
w.resizable(False, False)

# define tkinter variables to be used

var_algorithm = tk.StringVar(w)
var_algorithm.set("Hillclimbing")

var_warehouse_path = tk.StringVar(w)
var_warehouse_path.set("please select warehouse file")

var_order_path = tk.StringVar(w)
var_order_path.set("please select order file")

# define frames for controls (left side) and the graph (right side)

frame_controls = tk.Frame(master = w, bg = "#ffffff")
frame_graph = tk.Frame(master = w,  bg = "#ffffff")

frame_controls.grid(row = 0, column = 0, sticky = "NS", padx = 5, pady = 5)
frame_graph.grid(row = 0, column = 1)

# CONTROLS

def ask_filename(title, output_var):
    types = [("text files (*.txt)", "*.txt"), ("all files", "*.*")]

    path = tk.filedialog.askopenfilename(title = title, filetypes = types)
    if path != "": output_var.set(path)

button_open_warehouse = ttk.Button(frame_controls, width = 25, text = "Open Warehouse",
    command = lambda: ask_filename("Open Warehouse File", var_warehouse_path))
button_open_warehouse.grid(row = 0, column = 0, sticky = "W")

button_open_order = ttk.Button(frame_controls, width = 25, text = "Open Order",
    command = lambda: ask_filename("Open Order File", var_order_path))
button_open_order.grid(row = 0, column = 1, sticky = "E")

text_warehouse = tk.Entry(frame_controls, width = 55, textvariable = var_warehouse_path)
text_warehouse.grid(row = 1, columnspan = 2, pady = (5, 0))
text_warehouse["state"] = "disabled"

text_order = tk.Entry(frame_controls, width = 55, textvariable = var_order_path)
text_order.grid(row = 2, columnspan = 2, pady = (5, 0))
text_order["state"] = "disabled"

sep_1 = ttk.Separator(frame_controls, orient = tk.HORIZONTAL)
sep_1.grid(row = 3, columnspan = 2, pady = (10, 0), sticky = "EW")

option_algorithm = ttk.OptionMenu(frame_controls, var_algorithm, var_algorithm.get(),
    "Hillclimbing", "Local Beam Search")
option_algorithm.grid(row = 4, columnspan = 2, pady = (10, 0), sticky = "EW")

# GRAPH

fig = Figure(figsize = (5, 5))
ax = fig.add_subplot(1, 1, 1)

ax.plot(np.arange(10), 1 / (1 + np.arange(10)))

fig.set_tight_layout(True)

canvas = FigureCanvasTkAgg(fig, master = frame_graph)
canvas.draw()
plt_widget = canvas.get_tk_widget()
plt_widget.grid(row = 0, column = 0, columnspan = 2)

button_start = ttk.Button(frame_graph, text = "Start")
button_start.grid(row = 1, column = 0)

button_cancel = ttk.Button(frame_graph, text = "Cancel")
button_cancel.grid(row = 1, column = 1)


w.mainloop()
