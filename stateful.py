import ray

# Initialize Ray
ray.init()

# Define the Actor class
@ray.remote
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self, value):
        self.count += value
        return self.count

# Create an instance of the Actor
counter = Counter.remote()

# Invoke methods on the Actor
futures = [counter.increment.remote(i) for i in range(5)]
results = ray.get(futures)
print(results)

"""
2024-10-23 22:13:30,975	INFO worker.py:1777 -- Started a local Ray instance. View the dashboard at 127.0.0.1:8265 
[0, 1, 3, 6, 10]
"""
