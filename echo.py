import ray
from ray import serve

# Initialize Ray and start Ray Serve
ray.init()
serve.start()

# Define the deployment
@serve.deployment
def echo(request):
    return f"Received data: {request.query_params['data']}"

# Deploy the service
serve.run(echo.bind())

# Sending a request to the service
import requests
response = requests.get("http://localhost:8000/", params={"data": "Hello"})
print(response.text)

"""
2024-10-23 21:42:24,973	INFO worker.py:1777 -- Started a local Ray instance. View the dashboard at 127.0.0.1:8265 
INFO 2024-10-23 21:42:26,744 serve 32467 api.py:277 - Started Serve in namespace "serve".
INFO 2024-10-23 21:42:26,745 serve 32467 api.py:259 - Connecting to existing Serve app in namespace "serve". New http options will not be applied.
(ProxyActor pid=32493) INFO 2024-10-23 21:42:26,724 proxy 127.0.0.1 proxy.py:1188 - Proxy starting on node 0ac326e032cb7205d02860228c843608cadd84d301f27b5f0188edd3 (HTTP port: 8000).
(ServeController pid=32489) INFO 2024-10-23 21:42:26,791 controller 32489 deployment_state.py:1598 - Deploying new version of Deployment(name='echo', app='default') (initial target replicas: 1).
(ServeController pid=32489) INFO 2024-10-23 21:42:26,893 controller 32489 deployment_state.py:1844 - Adding 1 replica to Deployment(name='echo', app='default').
INFO 2024-10-23 21:42:27,754 serve 32467 client.py:492 - Deployment 'echo:s8cys2ug' is ready at `http://127.0.0.1:8000/`. component=serve deployment=echo
INFO 2024-10-23 21:42:27,756 serve 32467 api.py:549 - Deployed app 'default' successfully.
Received data: Hello
(ServeReplica:default:echo pid=32488) INFO 2024-10-23 21:42:27,775 default_echo f8tx91cf 6da86f01-fd35-4de1-9a9d-35817bb13f26 / replica.py:376 - __CALL__ OK 2.5ms
"""
