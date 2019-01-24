from searchutils import neighbors_func, neighbors_func_v2
from time import time
import numpy as np


for i in range(1000000):
    a = i ** 2

state = np.ones((100, ), dtype = np.bool)

print("v1")

t = time()

for i in range(1000):
    n = neighbors_func(state)

t = time() - t
print(t)

print("v2")
t = time()

for i in range(1000):
    n = neighbors_func_v2(state)


t = time() - t
print(t)
