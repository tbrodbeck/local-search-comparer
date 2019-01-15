import numpy as np
from multiprocessing import Process, Manager 

from search import Abstract_Search
from searchutils import value_function, neighbors_func

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
                    p = Process(target=search_step, args=(neighborss[i], i, return_dict, self.order, self.items, self.psus))
                    jobs.append(p)
                    p.start()

            # run them in parallel and wait for all to end their iteration
            for p in jobs:
                p.join()

            # checks if the termination condition is fullfilled and extracts states
            terminated = True
            for i in range(k):
                if not terminations[i]:
                    terminations[i] = self.termination(return_dict[i][1], return_dict[i][3])
                    terminated = terminations[i] and terminated
                    neighborss[i] = return_dict[i][2]
                    value_neighbors[i] = return_dict[i][3]
                    values[i] = return_dict[i][1]

            # Update graph
            if self.log_var == None:
                print('value:', values, 'done:', terminations)
            else:
                self.log_var.set(values)
                self.window.update()




def search_step(neighbors, procnum, return_dict, order, items, psus):
    """
    This is a function that does one single hillclimb step.
    :param neighbors:
    :param procnum: number of this parallel process
    :param return_dict: current, value, neighbors, value_neighbors are returned via this dictionary
    """



    # Choose the biggest neighbour
    max_neighbor = neighbors[np.argmax(np.apply_along_axis(lambda x: value_function(x, order, items, psus), 1, neighbors))]

    # Calculate new current and view it
    current = max_neighbor
    value = value_function(current, order, items, psus)

    # Create new neighbours and their values
    neighbors = neighbors_func(current)
    value_neighbors = np.apply_along_axis(lambda x: value_function(x, order, items, psus), 1, neighbors)

    return_dict[procnum] = current, value, neighbors, value_neighbors
