import time
database = [
    "Learning", "Ray"
    "Learning", "Ray"
    "Learning", "Ray"
    "Learning", "Ray"
    "Learning", "Ray"
]

def retrieve(item):
    time.sleep(item/10.00)
    return item, database[item]

def print_runtime(input_data, start_time):
    print(f'Runtime:{time.time() - start_time:.2f} seconds; data:')
    print(*input_data, sep='\n')


start_time = time.time()
input_data = [retrieve(item) for item in range(len(database))]
print_runtime(input_data, start_time)

"""
Runtime:1.52 seconds; data:
(0, 'Learning')
(1, 'RayLearning')
(2, 'RayLearning')
(3, 'RayLearning')
(4, 'RayLearning')
(5, 'Ray')
"""
