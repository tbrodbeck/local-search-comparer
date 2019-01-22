import numpy as np
from multiprocessing import Process, Manager
import time
import scipy

from itertools import count, compress
import random
from math import exp

from searchutils import value_function, neighbors_func

class Abstract_Search():
    """
    This is an abstract search class that all other search-algorithms can inherit.
    """
    def __init__(self, warehouse, order, log_var = None, window = None):
        self.directories = [warehouse, order]
        self.items = self.get_items(warehouse)
        self.order = self.open_order(order, self.items)
        self.psus, self.psu_nrs = self.get_psus(warehouse, self.items, self.order)
        self.start_state = np.random.choice([True, False], len(self.psus), p=[np.count_nonzero(self.order)/ len(self.items), 1 - (np.count_nonzero(self.order) / len(self.items))])
        self.log_var = log_var
        self.window = window


    def start(self):
        """
        Initializes the start states of a search
        :return: current-state, value, neighbors, value_neighbors
        """
        current = self.start_state
        value = self.value_function(current)
        neighbors = self.neighbors(current)
        value_neighbors = np.apply_along_axis(self.value_function, 1, neighbors)

        return current, value, neighbors, value_neighbors


    def get_items(self, path):
        """
        Retrieves a list of all items from the given file

        :param path: file path
        :return: list of items
        """
        with open(path) as f:
            data = f.read()

        lines = data.split("\n")
        items = lines[0].split(" ")

        return items


    def get_psus(self, path, items, order):
        """
        Retrieves a list of the PSUs that contain items of the current order
        A PSU is described by a binary array that contains the order items

        :param path: file path
        :param items: list of all items
        :return: 2D array containing the psus
        """
        with open(path) as f:
            data = f.read()

        lines = data.split("\n")

        # collect the important psus for our search and remember their psu-nr
        psus = []
        psu_nrs = []

        order_index = np.nonzero(order)

        for index, line in enumerate(lines[2:]):
            psu_temp = np.zeros(len(items), dtype=bool)
            psu_items = line.split(" ")

            for item in psu_items:
                item_index = items.index(item)
                psu_temp[item_index] = 1

            if np.any(psu_temp[order_index]):
                psus.append(psu_temp[order_index])
                psu_nrs.append(index)

        psus = np.asarray(psus)
        psu_nrs = np.asarray(psu_nrs)
        return psus, psu_nrs


    def open_order(self, path, items):
        """
        Retrieves the order from the given file

        :param path: file path
        :param items: list of all get_items
        :return: list of all ordered items
        """
        with open(path) as f:
            order_raw = f.read()

        order_raw = order_raw.split(' ')
        order = np.zeros(len(items), dtype=bool)

        for item_in_order in order_raw:
            order[items.index(item_in_order)] = True

        return order


    def print_solution(self, final_state):
        """
        """
        #print(final_state)

        output = ""


        # Numbers of psus needed
        number_of_psus = np.count_nonzero(final_state)
        output += "Number of PSUs needed: {}\n\n".format(number_of_psus)

        psus_state = np.compress(final_state, self.psus, axis=0)
        order_raw = np.compress(self.order, self.items)
        output += "Order: " + str(set(order_raw)) + '\n\n'

        output += f"Value of end state: {self.value_function(final_state)}\n\n"

        for index, psu in enumerate(psus_state):
            items_in_psu = np.compress(psu, order_raw)
            output += f"PSU Nr.{self.psu_nrs[index] + 1}: {items_in_psu}" + '\n'


        #
        # psus_used_indices = np.nonzero(final_state)
        # psus_used = self.psus[psus_used_indices]
        #
        # order_raw = set(compress(self.items, self.order))
        #
        # output += "Order: {}\n\n".format(order_raw)
        #
        # for i in range(number_of_psus):
        #     output += "PSU n°{}\t".format(psus_used_indices[i] + 1)
        #
        #     items_in_psu = np.nonzero(np.asarray(psus_used[i]))
        #     items_in_psu = set(np.asarray(self.order)[items_in_psu])
        #
        #     items_in_order = items_in_psu.intersection(order_raw)
        #
        #     output += str(items_in_order) + "\n"

        return output



    def value_function(self, state):
        """
        Evaluates how good a subset of PSU fulfills the order

        :param state: binary array describing used PSUs
        :return: value of state
        """

        return value_function(state, self.order, self.psus)


    def neighbors(self, state):
        """
        Creates all neighbors of a given state
        A state's neighbor is identical to the state except at exactly one
        position

        :param state: binary array describing used PSUs
        :return: 2D array containing all state's neighbors
        """

        return neighbors_func(state)

    def termination(self, value, value_neighbors):
        """
        Checks if there is a higher value in its neighborhood
        :param value: value
        :param value_neighbors: list of values
        :return: Bool
        """
        return not np.any(value_neighbors > value)


class Hill_Climbing(Abstract_Search):
    """
    Starts with a random state and continues with the best state of its neighborhood until there is no improvement possible
    in the neighborhood (local maximum).
    """
    def search(self):
        current, value, neighbors, value_neighbors = self.start()

        iteration = 0

        while not self.termination(value, value_neighbors):

            iteration += 1

            # Choose the biggest neighbour
            max_neighbor = neighbors[np.argmax(np.apply_along_axis(self.value_function, 1, neighbors))]

            # Calculate new current and view it
            current = max_neighbor
            value = self.value_function(current)
            if self.log_var == None:
                print(iteration, value)
            else:
                self.log_var.set(value)
                self.window.update()

            # Create new neighbours and their values
            neighbors = self.neighbors(current)
            value_neighbors = np.apply_along_axis(self.value_function, 1, neighbors)

        return current


class First_Choice_Hill_Climbing(Abstract_Search):
    """
    Starts with a random state and continues with the first better state of its neighborhood until
    there is no improvement possible in the neighborhood (local maximum).
    """
    def search(self):
        current, value, neighbors, value_neighbors = self.start()

        iteration = 0

        while not self.termination(value, value_neighbors):

            iteration += 1

            # Choose first neighbour that is better than current state
            first_bigger_neighbor = neighbors[np.argmax(value_neighbors > value)]

            # Calculate new current and view it
            current = first_bigger_neighbor
            value = self.value_function(current)
            if self.log_var is not None:    self.log_var.set(value)
            if self.window is not None:     self.window.update()

            # Create new neighbours and their values
            neighbors = self.neighbors(current)
            value_neighbors = np.apply_along_axis(self.value_function, 1, neighbors)

        return current

class Local_Beam_Search(Abstract_Search):
    """
    Starts with k states, does hillclimbing and continues with k best values of the union of the neighborhoods.
    """

    def search(self, k):
        # initializes k start states
        k_states = np.random.choice([True, False], (k, len(self.psus)),
                                    p=[np.count_nonzero(self.order) / len(self.psus),
                                    1 - (np.count_nonzero(self.order) / len(self.psus))])

        # Generate neighbours of current states
        all_neighbors = np.apply_along_axis(self.neighbors, 1, k_states)
        all_neighbors = all_neighbors.reshape(-1, all_neighbors.shape[-1])

        # If no neighbour is better than worst current state return
        value_neighbors = np.apply_along_axis(self.value_function, 1, all_neighbors)
        value = np.amin(np.apply_along_axis(self.value_function, 1, k_states))

        iteration = 0

        while not self.termination(value, value_neighbors):

            iteration += 1

            # Continue with k best neighbours
            sort = np.argsort(value_neighbors)
            k_states = all_neighbors[sort][-k:]

            # Generate neighbours of current states
            all_neighbors = np.apply_along_axis(self.neighbors, 1, k_states)
            all_neighbors = all_neighbors.reshape(-1, all_neighbors.shape[-1])

            # If no neighbour is better than worst current state return
            value_neighbors = np.apply_along_axis(self.value_function, 1, all_neighbors)
            values = np.apply_along_axis(self.value_function, 1, k_states)
            value = np.amin(values)

            # Update graph
            if self.log_var == None:
                print(iteration, values)
            else:
                self.log_var.set(list(values))
                self.window.update()

        return k_states[-1]



class Simulated_Annealing(Abstract_Search):

    def schedule(self, t):
        return 100 * 0.9 ** t

    def search(self):

        current = self.start_state
        temp = 100

        for t in count():

            # Updates temperature using the time schedule
            temp = self.schedule(t)

            # Returns current state if temperature is 0
            if t == 500:
                return current

            # Choose random neighbour and calculates ∆E
            next_neighbor = random.choice(self.neighbors(current))
            delta_e = self.value_function(next_neighbor) - self.value_function(current)

            # If the random neighbour is better, continue search with it
            if delta_e >= 0:
                current = next_neighbor

            # If it is worse, continue with the random neighbour
            # with probability e^(∆E / temperature)
            else:
                if random.random() < exp(delta_e / temp):
                    #print("Probability:", exp(delta_e / temp))
                    current = next_neighbor

            # Update graph
            value = self.value_function(current)
            if self.log_var == None:
                print(current, value)
            else:
                self.log_var.set(value)
                self.window.update()



''' Testing the Search '''

if __name__ == '__main__':
    s = Hill_Climbing('data/problem1.txt', 'data/order11.txt')
    #s.get_psu("data/problem_100_items.txt", s.items, s.order)
    # s.value_function(s.start_state)

    #s4 = First_Choice_Hill_Climbing('data/problem1.txt', 'data/order11.txt')
    #s3 = Hill_Climbing('data/problem1.txt', 'data/order12.txt')
    # s2 = Parallel_Hillclimbing('data/problem1.txt', 'data/order11.txt')
    # s2 = Local_Beam_Search('data/problem1.txt', 'data/order11.txt')
    #s2 = Parallel_Hillclimbing('data/problem1.txt', 'data/order11.txt')

    print(s.print_solution(s.search()))
