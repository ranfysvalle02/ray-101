# Ray 101: Accelerating Python Workflows with Ray

Parallel computing can significantly speed up data processing tasks by utilizing multiple CPU cores. Ray is an open-source framework that makes it easy to scale Python code from a single machine to a cluster, without the need to manage complex distributed systems. In this post, we'll explore the fundamentals of Ray, demonstrate how it can accelerate Python workflows, and delve into its integration with MongoDB. We'll also discuss scenarios where using Ray may not yield performance benefits.

## Table of Contents

- [Understanding Ray Fundamentals](#understanding-ray-fundamentals)
  - [Sequential Execution without Ray](#sequential-execution-without-ray)
  - [Parallel Execution with Ray](#parallel-execution-with-ray)
- [Task Dependencies in Ray](#task-dependencies-in-ray)
- [Integrating Ray with MongoDB](#integrating-ray-with-mongodb)
  - [Parallel Aggregations with Ray and MongoDB](#parallel-aggregations-with-ray-and-mongodb)
  - [Sequential Aggregations without Ray](#sequential-aggregations-without-ray)
- [When to Use Ray (and When Not To)](#when-to-use-ray-and-when-not-to)
- [Conclusion](#conclusion)

---

## Understanding Ray Fundamentals

### Sequential Execution without Ray

Let's start with a simple Python script that simulates data retrieval from a database. We'll define a `retrieve` function that introduces a delay using `time.sleep()` to mimic a time-consuming operation.

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
    time.sleep(item / 10.00)  # Simulate processing time
    return item, database[item]

def print_runtime(input_data, start_time):
    print(f'Runtime: {time.time() - start_time:.2f} seconds; data:')
    print(*input_data, sep='\n')

start_time = time.time()
input_data = [retrieve(item) for item in range(len(database))]
print_runtime(input_data, start_time)
```

**Output:**

```
Runtime:1.52 seconds; data:
(0, 'Learning')
(1, 'RayLearning')
(2, 'RayLearning')
(3, 'RayLearning')
(4, 'RayLearning')
(5, 'Ray')
```

In this script, each call to `retrieve` is executed sequentially. The total runtime is the sum of the individual delays, which can become significant as the number of tasks increases.

### Parallel Execution with Ray

By incorporating Ray, we can execute these tasks in parallel, leveraging multiple CPU cores to reduce the overall runtime.

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
    time.sleep(item / 10.00)
    return item, database[item]

def print_runtime(input_data, start_time):
    print(f'Runtime: {time.time() - start_time:.2f} seconds; data:')
    print(*input_data, sep='\n')

start_time = time.time()
object_references = [retrieve.remote(item) for item in range(len(database))]
input_data = ray.get(object_references)
print_runtime(input_data, start_time)
```

**Output:**

```
2024-10-18 10:56:44,268	INFO worker.py:1777 -- Started a local Ray instance.
Runtime:0.87 seconds; data:
(0, 'Learning')
(1, 'RayLearning')
(2, 'RayLearning')
(3, 'RayLearning')
(4, 'RayLearning')
(5, 'Ray')
```

In the Ray-enabled script:

- We initialize Ray with `ray.init()`.
- The `retrieve` function is decorated with `@ray.remote`, indicating that it can be executed as a Ray task.
- We invoke `retrieve.remote(item)` for each item, which schedules the tasks for parallel execution.
- `ray.get(object_references)` collects the results once all tasks are completed.

**Performance Improvement:**

The runtime is reduced from **1.52 seconds** to **0.87 seconds**, showcasing the benefits of parallel execution.

## Task Dependencies in Ray

Ray excels not only at parallelizing independent tasks but also at handling tasks with dependencies. Let's consider an example where we process data and then aggregate the results.

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

**Output:**

```
Aggregated result: 20
Runtime: 1.04 seconds
```

**Explanation:**

- The `process` tasks are executed in parallel, each taking 1 second.
- The `aggregate` task waits for all `process` tasks to complete.
- The total runtime is just over 1 second, instead of 5 seconds if executed sequentially.

## Integrating Ray with MongoDB

MongoDB is a popular NoSQL database, and integrating it with Ray can enable parallel data processing tasks such as aggregations. Let's explore how to use Ray with MongoDB and understand when it provides performance benefits.

### Parallel Aggregations with Ray and MongoDB

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

combined_result = result1 + result2

end_time = time.time()

print(f"Number of results: {len(combined_result)}")
print(f"Execution time: {end_time - start_time} seconds")
```

**Output:**

```
Number of results: 44562
Execution time: 1.444197177886963 seconds
```

In this script:

- We define an `Aggregator` actor class that holds a MongoDB client.
- Two aggregator actors are created to perform separate aggregation tasks in parallel.
- The results are combined after both tasks complete.

### Sequential Aggregations without Ray

Now, let's perform the same aggregations sequentially without using Ray.

```python
import time
from pymongo import MongoClient

start_time = time.time()

client = MongoClient('mongodb://localhost:27017/?directConnection=true')
db = client['sample_mflix']

result1 = list(db['embedded_movies'].aggregate([
    {"$match": {}}
]))
result2 = list(db['comments'].aggregate([
    {"$match": {}}
]))

combined_result = result1 + result2

end_time = time.time()

print(f"Number of results: {len(combined_result)}")
print(f"Execution time: {end_time - start_time} seconds")
```

**Output:**

```
Number of results: 44562
Execution time: 0.765700101852417 seconds
```

**Observation:**

- The sequential execution without Ray is faster in this case.
- The execution time without Ray is approximately **0.77 seconds**, compared to **1.44 seconds** with Ray.

## When to Use Ray (and When Not To)

While Ray can significantly speed up tasks by parallelizing them, it's important to consider the overhead introduced by Ray itself. This includes:

- **Serialization and Deserialization:** Data passed between tasks may need to be serialized.
- **Communication Overhead:** Coordination between workers and the Ray scheduler can add latency.
- **Resource Utilization:** Spinning up multiple workers consumes system resources.

**Scenarios Where Ray Shines:**

- **Long-Running Tasks:** Tasks that take a substantial amount of time benefit from parallel execution.
- **Compute-Intensive Operations:** CPU-bound tasks that can be distributed across cores.
- **Large-Scale Data Processing:** When working with large datasets that exceed the capacity of a single machine.

**Scenarios Where Ray May Not Help:**

- **Short Tasks with Low Latency:** The overhead of task scheduling and communication can outweigh the benefits.
- **I/O-Bound Tasks with External Bottlenecks:** If tasks are waiting on I/O operations (e.g., database queries), parallel execution may not improve performance.
- **Limited Resources:** On systems with limited CPU cores or memory, adding parallelism can lead to contention.

**Analysis of Our MongoDB Example:**

In the MongoDB aggregation example:

- **Task Duration:** The aggregation tasks are relatively quick.
- **Overhead Costs:** The overhead introduced by Ray (e.g., starting actors, serializing data) adds to the total execution time.
- **Database Constraints:** MongoDB may become a bottleneck if it cannot handle multiple simultaneous requests efficiently.

As a result, the sequential execution without Ray is faster because it avoids the overhead associated with parallelism in this context.

## Conclusion

Ray is a powerful tool for parallelizing and scaling Python applications. It can lead to significant performance improvements when used appropriately. However, it's crucial to assess whether the tasks at hand will benefit from parallel execution.

**Key Takeaways:**

- **Evaluate Task Complexity:** Use Ray for tasks that are sufficiently long-running or compute-intensive.
- **Consider Overhead:** Be mindful of the overhead introduced by Ray, especially for small or quick tasks.
- **Test and Measure:** Always benchmark your applications with and without Ray to determine if it provides a performance benefit.

By understanding when and how to use Ray, you can optimize your workflows for maximum efficiency.

---
