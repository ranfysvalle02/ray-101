import time
import ray

ray.init()

database = [
    "Learning", "Ray"
    "Learning", "Ray"
    "Learning", "Ray"
    "Learning", "Ray"
    "Learning", "Ray"
]

@ray.remote
def retrieve(item):
    time.sleep(item/10.00)
    return item, database[item]

def print_runtime(input_data, start_time):
    print(f'Runtime:{time.time() - start_time:.2f} seconds; data:')
    print(*input_data, sep='\n')


start_time = time.time()
object_references = [retrieve.remote(item) for item in range(len(database))]
input_data = ray.get(object_references)
print_runtime(input_data, start_time)

"""
2024-10-18 10:56:44,268	INFO worker.py:1777 -- Started a local Ray instance. View the dashboard at 127.0.0.1:8265 
Runtime:0.87 seconds; data:
(0, 'Learning')
(1, 'RayLearning')
(2, 'RayLearning')
(3, 'RayLearning')
(4, 'RayLearning')
(5, 'Ray')
"""
