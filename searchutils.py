import numpy as np

def neighbors_func(state):
    """
    Creates all neighbors of a given state
    A state's neighbor is identical to the state except at exactly one
    position

    :param state: binary array describing used PSUs
    :return: 2D array containing all state's neighbors
    """
    neighbors = np.tile(state, (state.size, 1))
    diagonal = np.diagonal(neighbors)

    for i in range(state.size):
        neighbors[i, i] = not diagonal[i]

    return neighbors

def value_function(state, order, items, psus):
    """
    Evaluates how good a subset of PSU fulfills the order

    :param state: binary array describing used PSUs
    :return: value of state
    """
    print(state, order, items, psus)
    psus_state = np.zeros((state.size, len(items)), dtype=int)

    for index, psu in np.ndenumerate(state):
        if psu:
            psus_state[index] = psus[index]

    items = np.bitwise_or.reduce(psus_state, 0)
    total_items = items[order]
    # print(state, total_items, end="")

    if np.all(total_items):
        return 2 * np.count_nonzero(order) - np.count_nonzero(state)

    else:
        return -10 * np.count_nonzero(total_items == 0)
