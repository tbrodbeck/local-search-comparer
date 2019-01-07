import numpy as np


class Abstract_Search():
    """
    This is an abstract search class that all other search-algorithms can inherit.
    """
    def __init__(self, directory):
        self.items = self.get_items(directory + '/problem1.txt')
        self.psus = self.get_psus(directory + '/problem1.txt', self.items)
        self.order = self.open_order(directory + '/order12.txt', self.items)
        self.start_state = np.random.choice([True, False], len(self.psus), p=[np.count_nonzero(self.order)/ len(self.psus), 1 - (np.count_nonzero(self.order) / len(self.psus))])


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

    def termination(self):
        """
        TODO

        (?)
        """
        return False


class Hill_Climbing(Abstract_Search):

    def search(self):
        current = self.start_state
        max_neighbor = np.full(self.psus[0].size, False)

        while not self.termination():
            neighbors_of_current = self.neighbors(current)
            max_neighbor = neighbors_of_current[np.argmax(np.apply_along_axis(self.value_function, 1, neighbors_of_current))]

            if self.value_function(max_neighbor) <= self.value_function(current):
                return current

            current = max_neighbor
            print(current, self.value_function(current))



class First_Choice_Hill_Climbing(Abstract_Search):

    def search(self):
        current = self.start_state

        while not self.termination():

            # Create neighbours and their values
            neighbors_of_current = self.neighbors(current)
            value_neighbors = np.apply_along_axis(self.value_function, 1, neighbors_of_current)

            # Choose first neighbour that is better than current state
            first_neighbor = neighbors_of_current[np.argmax(value_neighbors > self.value_function(current))]

            bigger_neighbors = value_neighbors > self.value_function(current)

            # If there is no better neighbour return, else continue with first neighbour
            if not np.any(bigger_neighbors):
                return current
            
            else:
                current = first_neighbor
                print(current, self.value_function(current))


class Local_Beam_Search(Abstract_Search):

    def search(self, k):

        k_states = np.random.choice([True, False], (k, len(self.psus)), p=[np.count_nonzero(self.order)/ len(self.psus), 1 - (np.count_nonzero(self.order) / len(self.psus))])
        
        while not self.termination():

            # Generate neighbours of current states
            all_neighbors = np.apply_along_axis(self.neighbors, 1, k_states)
            all_neighbors = all_neighbors.reshape(-1, all_neighbors.shape[-1])

            # If no neighbour is better than worst current state return
            value_neighbors = np.apply_along_axis(self.value_function, 1, all_neighbors)
            value_current = np.amin(np.apply_along_axis(self.value_function, 1, k_states))
            
            if not np.any(value_neighbors > value_current):
                return k_states

            # Else continue with k best neighbours
            sort = np.argsort(value_neighbors)
            k_states = all_neighbors[sort][-k:]
            print(k_states, np.apply_along_axis(self.value_function, 1, k_states), '\n\n')


''' Testing the Search '''

if __name__ == '__main__':
    hill_climb = Hill_Climbing('data')
    first_choice_hill_climb = First_Choice_Hill_Climbing('data')
    local_beam = Local_Beam_Search('data')
    #print(hill_climb.search(), end='\n\n')
    #print(first_choice_hill_climb.search(), end='\n\n')
    print(local_beam.search(3))
