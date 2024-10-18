# ray-101
Ray fundamentals

## no ray

```python
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
```

## ray

```python
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
```
