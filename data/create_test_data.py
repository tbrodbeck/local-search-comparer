import random
import numpy as np


data_size = 100
psus_number = 50
order_size = 35

# Create items list

list_items = [f'Item_{number} ' for number in list(range(data_size))]
list_items[-1] = list_items[-1].rstrip() 


# create PSUs

psus = []

for i in range(psus_number):
    current_psu = set()
    
    for j in range(random.randint(1, int(data_size *  2 / 4))):
        current_psu.add(random.choice(list_items))

    current_psu = [f'{elem} ' for elem in list(current_psu)]
    current_psu[-1] = current_psu[-1].rstrip()
    
    psus.append(current_psu)

# Create problem file

example_id = str(data_size) + "_items"

                   
with open(f'problem_{example_id}.txt', 'w+') as problem:
    problem.writelines(list_items)
    problem.write("\n")

    for psu in psus:
        problem.write('\n')
        problem.writelines(psu)                     
    

# create order and order file

order = np.random.choice(list_items, order_size, replace=False)

with open(f'order_{example_id}.txt', 'w+') as f:
    
    for item in order:
        f.write(item)
        f.write(' ')

