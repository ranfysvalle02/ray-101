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

"""
Runtime:1.52 seconds; data:
(0, 'Learning')
(1, 'RayLearning')
(2, 'RayLearning')
(3, 'RayLearning')
(4, 'RayLearning')
(5, 'Ray')
"""
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
```

## Ray 101: Speeding Up Your Workflows with Ray

In this post, we’ll explore how Ray can help accelerate Python workflows by distributing tasks across multiple cores, allowing for parallel execution. We’ll start with a simple example that demonstrates the difference between a traditional Python script and one powered by Ray. Then, we’ll dive into task dependencies and how Ray handles them with meaningful examples.

### No Ray: A Simple Python Workflow

Let’s begin with a traditional Python setup where we retrieve data from a database. The `retrieve` function simulates a task that takes some time to complete, and we'll execute it in sequence. Here’s the code:

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
    time.sleep(item/10.00)  # Simulate processing time
    return item, database[item]

def print_runtime(input_data, start_time):
    print(f'Runtime:{time.time() - start_time:.2f} seconds; data:')
    print(*input_data, sep='\n')


start_time = time.time()
input_data = [retrieve(item) for item in range(len(database))]
print_runtime(input_data, start_time)
```

This function goes through each item in the database, waits for a specified time (simulating some work), and returns the result. The runtime output looks like this:

```
Runtime: 1.52 seconds; data:
(0, 'Learning')
(1, 'RayLearning')
(2, 'RayLearning')
(3, 'RayLearning')
(4, 'RayLearning')
(5, 'Ray')
```

While it works, the sequential execution means that even small delays add up. This is where Ray can step in to optimize performance.

### Adding Ray: Parallel Execution

Now, let’s use Ray to execute these tasks in parallel, taking advantage of multiple CPU cores. By using Ray's `remote` decorator, we can distribute the workload across different workers.

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

Here, the `retrieve` function is now decorated with `@ray.remote`, which allows Ray to distribute it as a task. When we call `retrieve.remote(item)`, Ray schedules these tasks in parallel, and we use `ray.get()` to gather the results. This gives us a much faster runtime:

```
2024-10-18 10:56:44,268	INFO worker.py:1777 -- Started a local Ray instance. 
Runtime: 0.87 seconds; data:
(0, 'Learning')
(1, 'RayLearning')
(2, 'RayLearning')
(3, 'RayLearning')
(4, 'RayLearning')
(5, 'Ray')
```

With Ray, we’ve cut the runtime almost in half by running tasks concurrently instead of sequentially. 

### Task Dependencies in Ray

Ray can handle more complex workflows involving task dependencies. For example, one task may depend on the results of another, but Ray still allows for concurrent execution when possible. Let’s look at a more meaningful example where tasks need to wait for the result of a previous one.

#### Example: Task Dependencies

Consider a scenario where we first need to process data before aggregating the results. Here's a simplified example:

```python
import ray
import time

ray.init()

@ray.remote
def process(item):
    time.sleep(1)
    return item * 2

@ray.remote
def aggregate(results):
    return sum(results)

start_time = time.time()

# Step 1: Process data in parallel
object_references = [process.remote(i) for i in range(5)]

# Step 2: Aggregate the results (dependent on Step 1)
aggregated_result = aggregate.remote(object_references)

# Gather the final result
final_result = ray.get(aggregated_result)
print(f'Aggregated result: {final_result}')

print(f'Runtime: {time.time() - start_time:.2f} seconds')
```

In this example:
1. The `process` function processes each item in parallel.
2. The `aggregate` function depends on the results of `process`, but we still execute the processing step in parallel.

The output demonstrates how Ray efficiently handles the dependencies:

```
Aggregated result: 20
Runtime: 1.04 seconds
```

Even though the `aggregate` task depends on the `process` results, Ray allows for parallel execution of independent tasks, speeding up the workflow significantly.

### Why Ray?

Ray makes it easy to parallelize Python code without needing to worry about the intricacies of managing multiple processes or threads. It automatically scales to available resources and is a great fit for projects requiring distributed execution. By reducing runtime, Ray enables faster iterations, which is crucial when dealing with large datasets or time-consuming computations.

--- 

## MongoDB + Ray

**ray-mdb.py**

```python
import time
import pymongo
import ray

ray.init()

@ray.remote
class Aggregator:
    def __init__(self, host, port, max_pool_size=10):
        # Create a MongoDB client with connection pooling
        self.client = pymongo.MongoClient(host, port, maxPoolSize=max_pool_size)

    def aggregate(self, database, collection, pipeline):
        db = self.client[database]
        return list(db[collection].aggregate(pipeline))

start_time = time.time()

# Create actors for each aggregation with connection pooling
aggregator1 = Aggregator.remote("mongodb://127.0.0.1/?directConnection=true", 27017)
aggregator2 = Aggregator.remote("mongodb://127.0.0.1/?directConnection=true", 27017)

# Submit aggregation tasks to the actors
result1_future = aggregator1.aggregate.remote("sample_mflix", "embedded_movies", [{"$match": {}}])
result2_future = aggregator2.aggregate.remote("sample_mflix", "comments", [{"$match": {}}])

# Get the results asynchronously
result1 = ray.get(result1_future)
result2 = ray.get(result2_future)

result = result1 + result2

end_time = time.time()

print(f"Number of results: {len(result)}")
print(f"Execution time: {end_time - start_time} seconds")


"""
If the aggregation tasks are relatively small, the overhead from Ray can overshadow the benefits of parallel execution. 
The time taken for communication and coordination can exceed the time saved by parallel processing.

with-ray
Number of results: 44562
Execution time: 1.444197177886963 seconds

no-ray
Number of results: 44562
Execution time: 0.765700101852417 seconds
"""
```

**no-ray-mdb.py**

```python
import time
from pymongo import MongoClient

start_time = time.time()

client = MongoClient('mongodb://localhost:27017/?directConnection=true')
db = client['sample_mflix']

result1 = list(db['embedded_movies'].aggregate([
    {"$match":{}}
]))
result2 = list(db['comments'].aggregate([
    {"$match":{}}
]))

combined_result = result1 + result2

end_time = time.time()

print(f"Number of results: {len(combined_result)}")
print(f"Execution time: {end_time - start_time} seconds")

"""
If the aggregation tasks are relatively small, the overhead from Ray can overshadow the benefits of parallel execution. 
The time taken for communication and coordination can exceed the time saved by parallel processing.

with-ray
Number of results: 44562
Execution time: 1.444197177886963 seconds

no-ray
Number of results: 44562
Execution time: 0.765700101852417 seconds
"""
```
