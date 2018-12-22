import numpy as np


def get_items(path):
    with open(path) as f:
        data = f.read()

    lines = data.split("\n")
    items = lines[0].split(" ")

    return items



def get_psus(path, items):
    with open(path) as f:
        data = f.read()

    lines = data.split("\n")
    psus = np.zeros((len(lines) - 2, len(items)), dtype = bool)

    for index, line in enumerate(lines[2:]):
        psu_items = line.split(" ")

        for item in psu_items:
            item_index = items.index(item)
            
            psus[index, item_index] = 1

    psus = np.array(psus)

    return psus




def open_order(path, items):
    with open(path) as f:
        order_raw = f.read()

    order_raw = order_raw.split(' ')
    order = np.zeros(len(items), dtype=bool)

    for item_in_order in order_raw:
        order[items.index(item_in_order)] = True

    return order


items = get_items("data/problem1.txt")
psus = get_psus('data/problem1.txt', items)
order = open_order("data/order12.txt", items)




def value_function(state, o=order, p=psus, i=items):
    psus_state = np.zeros((state.size, len(i)), dtype=int)
    
    for index, psu in np.ndenumerate(state):
        if psu:
            psus_state[index] = p[index]

    items = np.bitwise_or.reduce(psus_state, 0)
    total_items = items[o]
    #print(state, total_items, end="")
    
    if np.all(total_items):
        return 2 * np.count_nonzero(o) - np.count_nonzero(state)
    
    else:
        return -10 * np.count_nonzero(total_items == 0)
        
    
    

def termination():
    return False



def neighbors(state):
    neighbors = np.tile(state, (state.size, 1))
    diagonal = np.diagonal(neighbors)
    
    for i in range(state.size):
        neighbors[i, i] = not diagonal[i]

    return neighbors



def hill_climbing(p=psus):
    current = start_state
    max_neighbor = np.full(p[0].size, False)
    
    while not termination():
        neighbors_of_current = neighbors(current)
        max_neighbor = neighbors_of_current[np.argmax(np.apply_along_axis(value_function, 1, neighbors_of_current))]

        if value_function(max_neighbor) <= value_function(current):
            return current
            
        current = max_neighbor
        print(current, value_function(current))


    


start_state = np.random.choice([True, False], len(psus), p=[np.count_nonzero(order)/ len(psus), 1 - (np.count_nonzero(order) / len(psus))])
#start_state = np.random.choice([True, False], len(psus))
#start_state = np.zeros(len(psus))

print(start_state)
#print(value_function(start_state, order, psus))
#print(value_function(np.ones(len(psus), dtype=int), order, psus))

#print(neighbors(start_state))
#print(np.apply_along_axis(value_function, 1, neighbors(start_state)))
hill_climbing()
