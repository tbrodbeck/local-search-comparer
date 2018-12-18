import numpy as np

with open("data/problem1.txt") as f:
    data = f.read()

lines = data.split("\n")

items = lines[0].split(" ")[:-1]

n_items = len(items)

psus = np.zeros((len(lines) - 2, n_items), dtype = bool)

for index, line in enumerate(lines[2:]):
    psu_items = line.split(" ")[:-1]


    for item in psu_items:
        item_index = items.index(item)
        
        psus[index, item_index] = 1
