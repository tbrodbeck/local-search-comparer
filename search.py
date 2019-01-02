import numpy as np


class Abstract_Search():

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
        with open(path) as f:
            order_raw = f.read()

        order_raw = order_raw.split(' ')
        order = np.zeros(len(items), dtype=bool)

        for item_in_order in order_raw:
            order[items.index(item_in_order)] = True

        return order


    def value_function(self, state):

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
        neighbors = np.tile(state, (state.size, 1))
        diagonal = np.diagonal(neighbors)

        for i in range(state.size):
            neighbors[i, i] = not diagonal[i]

        return neighbors

    def termination(self):
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


hill_climb = Hill_Climbing('data')
print(hill_climb.search())
