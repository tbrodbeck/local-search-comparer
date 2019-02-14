import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from search import Hill_Climbing, First_Choice_Hill_Climbing, Local_Beam_Search, Simulated_Annealing
from parallel_hillclimbing import Parallel_Hillclimbing

from listvar import ListVar

# configuration of text output of the io
start_string = "Edmund Hillary welcomes you and invites you to find a local search solution for" \
                    " your intelligent warehouse system.\n\nPlease select a warehouse file and an order " \
                    "file and a configuration of your choice.\n\nAfter completing a search, the results " \
                    "will be displayed in this text field."
end_string = "\n\nFeel free to try another configuration."
err_string = "Please input correct files!\n\n\n"

def ask_filename(title, output_var):
    # on-click handler for open-buttons
    types = [("text files (*.txt)", "*.txt"), ("all files", "*.*")]

    path = tk.filedialog.askopenfilename(title = title, filetypes = types)
    if path != "": output_var.set(path)

def start_algorithm():
    global value_history

    # on-click handler for start button

    button_start["text"] = "Running..."
    button_start["state"] = "disabled"

    w.update()

    alg_string = var_algorithm.get()
    AlgorithmClass = algorithm_lookup[alg_string]


    # reset graph history
    value_history = []
    try:
        if alg_string != "Local Beam Search" and alg_string != "Parallel Hillclimbing":

            # variable that the search algorithms can write to, to communicate the value-function change over time
            var_algorithm_status = tk.IntVar(w)
            # add on-change handler for updating the graph
            var_algorithm_status.trace("w", lambda *args: update_graph([var_algorithm_status.get()]))

            alg = AlgorithmClass(var_warehouse_path.get(), var_order_path.get(), var_algorithm_status, w)
            result = alg.search()

        else:

            # for local beam search and parallel hillclimbing we need a variable that can handle lists
            var_algorithm_status = ListVar(4)
            # again add on-change handler
            var_algorithm_status.trace(lambda: update_graph(var_algorithm_status.get()))

            alg = AlgorithmClass(var_warehouse_path.get(), var_order_path.get(),
                var_algorithm_status, w
            )

            result = alg.search(var_threads.get())

        text_status["state"] = "normal"
        text_status.delete("1.0", tk.END)
        text_status.insert(tk.END, alg.print_solution(result) + end_string)
        text_status["state"] = "disabled"

        button_start["state"] = "normal"
        button_start["text"] = "Start"

    # if a wrong warehouse or order is inserted
    except Exception as err:
        text_status["state"] = "normal"
        text_status.delete("1.0", tk.END)
        text_status.insert(tk.END, err_string + start_string)
        text_status["state"] = "disabled"

        button_start["state"] = "normal"
        button_start["text"] = "Start"
widget_plot = None

def update_graph(value = None):
    # updates the graph with a new value
    # works by just creating a new graph, which is slow, but the alternative is annoying to implement

    global widget_plot

    if value is not None: value_history.append(value)

    ax.clear()

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Value function")

    zipped = zip(*value_history)

    for curve in zipped:
        ax.plot(range(len(curve)), curve)
        ax.plot(range(len(curve)), [0] * len(curve), linestyle = "-.")

    canvas = FigureCanvasTkAgg(fig, master = frame_graph)
    canvas.draw()

    old_widget = widget_plot

    widget_plot = canvas.get_tk_widget()
    widget_plot.grid(row = 0, column = 0, columnspan = 2)

    if old_widget is not None: old_widget.destroy()


if __name__ == "__main__":

    w = tk.Tk()
    w.title("Edmund Hillary")
    w["bg"] = "#ffffff"
    w.resizable(False, False)

    # define tkinter variables to be used

    var_warehouse_path = tk.StringVar(w)
    var_warehouse_path.set("Please select correct warehouse file.")

    var_order_path = tk.StringVar(w)
    var_order_path.set("Please select correct order file.")

    algorithm_lookup = {
        "Hillclimbing": Hill_Climbing,
        "First Choice Hillclimbing": First_Choice_Hill_Climbing,
        "Local Beam Search": Local_Beam_Search,
        "Simulated Annealing with HC": Simulated_Annealing,
        "Parallel Hillclimbing": Parallel_Hillclimbing,
    }

    var_algorithm = tk.StringVar(w)
    var_algorithm.set("Hillclimbing")

    var_threads = tk.IntVar(w)
    var_threads.set(4)

    var_status = tk.StringVar(w)
    var_status.set("Press 'Start' to run the selected algorithm.")

    # define frames for controls (left side) and the graph (right side)

    frame_controls = tk.Frame(master = w, bg = "#ffffff")
    frame_graph = tk.Frame(master = w,  bg = "#ffffff")

    frame_controls.grid(row = 0, column = 0, sticky = "NS", padx = (10, 5), pady = (20, 5))
    frame_graph.grid(row = 0, column = 1)

    # CONTROLS

    # button for opening warehouse files
    button_open_warehouse = ttk.Button(frame_controls, width = 25, text = "Open Warehouse",
        command = lambda: ask_filename("Open Warehouse File", var_warehouse_path))
    button_open_warehouse.grid(row = 0, column = 0, sticky = "W")

    # button for opening order files
    button_open_order = ttk.Button(frame_controls, width = 25, text = "Open Order",
        command = lambda: ask_filename("Open Order File", var_order_path))
    button_open_order.grid(row = 0, column = 1, sticky = "E")

    # read-only text area for path to warehouse file
    text_warehouse = tk.Entry(frame_controls, width = 55, textvariable = var_warehouse_path)
    text_warehouse.grid(row = 1, columnspan = 2, pady = (5, 0))
    text_warehouse["state"] = "disabled"

    # read-only text area for path to order file
    text_order = tk.Entry(frame_controls, width = 55, textvariable = var_order_path)
    text_order.grid(row = 2, columnspan = 2, pady = (5, 0))
    text_order["state"] = "disabled"

    # visual separator
    sep_1 = ttk.Separator(frame_controls, orient = tk.HORIZONTAL)
    sep_1.grid(row = 3, columnspan = 2, pady = (10, 0), sticky = "EW")

    # drop-down menu for selecting the search algorithm
    option_algorithm = ttk.OptionMenu(frame_controls, var_algorithm, var_algorithm.get(),
        *algorithm_lookup.keys())
    option_algorithm.grid(row = 4, columnspan = 2, pady = (10, 0), sticky = "EW")

    # label and drop-down menu for selecting number of threads
    label_threads = tk.Label(frame_controls, text = "Threads / Beams:", bg = "white")
    label_threads.grid(row = 5, column = 0, pady = (10, 0), sticky = "EW")

    option_threads = ttk.OptionMenu(frame_controls, var_threads, 4, *range(1, 11))
    option_threads.grid(row = 5, column = 1, pady = (10, 0), sticky = "EW")

    # text area for displaying the result of the algorithm
    text_status = tk.Text(frame_controls, width = 1, height = 23, bg = "#eeeeee", wrap = tk.WORD)
    text_status.grid(row = 6, columnspan = 2, pady = (5, 0), sticky = "EW")
    text_status["state"] = "normal"
    text_status.delete("1.0", tk.END)
    text_status.insert(tk.END, start_string)
    text_status["state"] = "disabled"

    # button for running the selected algorithm
    button_start = ttk.Button(frame_controls, text = "Start", command = start_algorithm)
    button_start.grid(row = 7, columnspan = 2, pady = (5, 0), sticky = "WE")

    # GRAPH

    # create Figure and Axes object
    value_history = []
    fig = Figure(figsize = (6, 6))
    fig.set_tight_layout(True)

    ax = fig.add_subplot(1, 1, 1)

    # call update_graph once to initialize the widget
    update_graph()



    w.mainloop()
