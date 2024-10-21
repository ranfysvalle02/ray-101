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
