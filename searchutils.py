""" Contains a function that returns the neighbors of a state, and a function that computes the value of a state. """

import numpy as np

def neighbors_func(state):
    """
    Creates all neighbors of a given state
    A state's neighbor is identical to the state except at exactly one
    position

    :param state: binary array describing used PSUs
    :return: 2D array containing all state's neighbors
    """
    # create output array with copies of the state
    neighbors = np.broadcast_to(state, (state.size, state.size)).copy()

    # create diagonal matrix as mask where to invert values
    mask = np.eye(state.size, dtype = np.bool)

    # apply logical not to mask values (i.e. along the diagonal)
    np.logical_not(neighbors, out = neighbors, where = mask)

    return neighbors


def value_function(state, order, psus):
    """
    Evaluates how good a subset of PSU fulfills the order

    :param state: binary array describing used PSUs
    :param order: binary representation of current order
    :param psus: 2d array containing binary representation of all psus
    :return: value of state
    """
    # a list of the psus (including its items) used in the state
    psus_in_state = np.compress(state, psus, axis=0)

    # CALCULATE VALUES
    # if the state is empty
    if len(psus_in_state) == 0:
        return -10 * (np.size(state))
    # else count the missing elements
    items = np.bitwise_or.reduce(psus_in_state, 0)

    # if all elements are covered, minimize the amount of used psus
    if np.all(items):
        return np.count_nonzero(state == False)
    # else elements are missing
    else:
        return -1 * (np.size(items) - np.count_nonzero(items))
