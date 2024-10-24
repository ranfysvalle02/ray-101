from ray.dag import InputNode
import ray

ray.init()

@ray.remote
def task1():
    return "Result from task1"

@ray.remote
def task2():
    return "Result from task2"

@ray.remote
def task3(result1, result2):
    return f"Task3 received: {result1} and {result2}"

# Define input nodes (if any)
# In this case, task1 and task2 do not require inputs, so we can proceed to build the DAG

# Build the DAG
result1_node = task1.bind()
result2_node = task2.bind()
result3_node = task3.bind(result1_node, result2_node)

# Execute the DAG
result = ray.get(result3_node.execute())
print(result)
"""
2024-10-23 22:22:05,202	INFO worker.py:1777 -- Started a local Ray instance. View the dashboard at 127.0.0.1:8265 
Task3 received: Result from task1 and Result from task2
"""
