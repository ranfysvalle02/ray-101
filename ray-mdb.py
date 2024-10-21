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
