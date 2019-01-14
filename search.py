import numpy as np
from view import Print_View
from multiprocessing import Process, Manager
import time
import scipy

from itertools import count, compress
import random
from math import exp

class Abstract_Search():
    """
    This is an abstract search class that all other search-algorithms can inherit.
    """
    def __init__(self, warehouse, order, log_var = None, window = None):
        self.directories = [warehouse, order]
        self.items = self.get_items(warehouse)
        self.psus = self.get_psus(warehouse, self.items)
        self.order = self.open_order(order, self.items)
        self.start_state = np.random.choice([True, False], len(self.psus), p=[np.count_nonzero(self.order)/ len(self.psus), 1 - (np.count_nonzero(self.order) / len(self.psus))])
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


    def get_psus(self, path, items):
        """
        Retrieves a list of all PSUs from the given file
        A PSU is described by a binary array

        :param path: file path
        :param items: list of all items
        :return: 2D array containing all psus
        """
        with open(path) as f:
            data = f.read()

        lines = data.split("\n")
        psus = np.zeros((len(lines) - 2, len(items)), dtype=bool)

        for index, line in enumerate(lines[2:]):
            psu_items = line.split(" ")

            for item in psu_items:
                item_index = items.index(item)

                psus[index, item_index] = 1

        psus = np.array(psus)

        return psus


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

        # Numbers of psus needed
        number_of_psus = np.count_nonzero(final_state)
        print('Number of PSUs needed:', number_of_psus)

        psus_used_indices = np.nonzero(final_state)[0]
        psus_used = self.psus[psus_used_indices]

        order_raw = set(compress(self.items, self.order))
        print("Order:", order_raw)
        print()

        for i in range(number_of_psus):
            print(f"PSU n°{psus_used_indices[i] + 1}", end="\t")

            items_in_psu = np.nonzero(np.asarray(psus_used[i]))
            items_in_psu = set(np.asarray(self.items)[items_in_psu])

            items_in_order = items_in_psu.intersection(order_raw)

            print(items_in_order)







    def value_function(self, state):
        """
        Evaluates how good a subset of PSU fulfills the order

        :param state: binary array describing used PSUs
        :return: value of state
        """

        psus_state = np.zeros((state.size, len(self.items)), dtype=int)

        for index, psu in np.ndenumerate(state):
            if psu:
                psus_state[index] = self.psus[index]

        items = np.bitwise_or.reduce(psus_state, 0)
        total_items = items[self.order]
        # print(state, total_items, end="")

        if np.all(total_items):
            return 2 * np.count_nonzero(self.order) - np.count_nonzero(state)

        else:
            return -10 * np.count_nonzero(total_items == 0)


    def neighbors(self, state):
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

    def termination(self, value, value_neighbors):
        """
        Checks if there is a higher value in its neighborhood
        :param value: value
        :param value_neighbors: list of values
        :return: Bool
        """
        if np.any(value_neighbors > value):
            return False
        else:
            return True


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

    def schedule(self, temp, t):
        # Temperature is lowered by one in each step
        if t % 2 == 0:
            return temp - 1
        else:
            return temp

    def search(self):

        current = self.start_state
        temp = 170

        for t in count():

            # Updates temperature using the time schedule
            temp = self.schedule(temp, t)

            # Returns current state if temperature is 0
            if temp == 0:
                return current

            # Choose random neighbour and calculates ∆E
            next_neighbor = random.choice(self.neighbors(current))
            delta_e = self.value_function(next_neighbor) - self.value_function(current)

            # If the random neighbour is better, continue search with it
            if delta_e > 0:
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
                if self.window is not None:
                    self.window.update()



class Parallel_Hillclimbing(Abstract_Search):
    """
    Perform k independent hillclimb searches started from randomly generated initial states
    """
    def search(self, k):
        # Process manager for value extraction in multiprocessing
        manager = Manager()

        # value to check if all searches terminated
        terminated = False
        # list to extract if a single search terminated
        terminations = [False for i in range(k)]

        # save states
        values = [0 for i in range(k)]
        neighborss = [0 for i in range(k)]
        value_neighbors = [0 for i in range(k)]

        # initialize k neighbors from a start state

        for i in range(k):
            # we need to create a random initialization for every start-state first
            start_state = np.random.choice([True, False], len(self.psus), p=[np.count_nonzero(self.order)/ len(self.psus), 1 - (np.count_nonzero(self.order) / len(self.psus))])
            neighborss[i] = self.neighbors(start_state)

        while not terminated:
            # dict for value extraction
            return_dict = manager.dict()

            # start k jobs
            jobs = []
            for i in range(k):
                if not terminations[i]:
                    p = Process(target=self.search_step, args=(neighborss[i], i, return_dict,))
                    jobs.append(p)
                    p.start()

            # run them in parallel and wait for all to end their iteration
            for p in jobs:
                p.join()

            # checks if the termination condition is fullfilled and extracts states
            terminated = True
            for i in range(k):
                if not terminations[i]:
                    terminated = terminated and self.termination(return_dict[i][1], return_dict[i][3])
                    terminations[i] = self.termination(return_dict[i][1], return_dict[i][3])
                    neighborss[i] = return_dict[i][2]
                    value_neighbors[i] = return_dict[i][3]
                    values[i] = return_dict[i][1]

            # Update graph
            if self.log_var == None:
                print('value:', values, 'done:', terminations)
            else:
                self.log_var.set(values)
                self.window.update()

    def search_step(self, neighbors, procnum, return_dict):
        """
        This is a function that does one single hillclimb step.
        :param neighbors:
        :param procnum: number of this parallel process
        :param return_dict: current, value, neighbors, value_neighbors are returned via this dictionary
        """
        # Choose the biggest neighbour
        max_neighbor = neighbors[np.argmax(np.apply_along_axis(self.value_function, 1, neighbors))]

        # Calculate new current and view it
        current = max_neighbor
        value = self.value_function(current)

        # Create new neighbours and their values
        neighbors = self.neighbors(current)
        value_neighbors = np.apply_along_axis(self.value_function, 1, neighbors)

        return_dict[procnum] = current, value, neighbors, value_neighbors

''' Testing the Search '''

if __name__ == '__main__':
    s = Hill_Climbing('data/problem1.txt', 'data/order12.txt')
    # s.search()

    s4 = First_Choice_Hill_Climbing('data/problem1.txt', 'data/order11.txt')
    s3 = Hill_Climbing('data/problem1.txt', 'data/order12.txt')
    # s2 = Parallel_Hillclimbing('data/problem1.txt', 'data/order11.txt')

    sa.print_solution(s.search())

    # s2 = Local_Beam_Search('data/problem1.txt', 'data/order11.txt')
    s2 = Parallel_Hillclimbing('data/problem1.txt', 'data/order11.txt')

    s2.search(2)
