import os
from flask import Flask, request, Response
import requests
import time

app = Flask(__name__)

backend_services = os.environ.get('BACKEND_SERVICES', '').split()

# Initialize a dictionary to store the response times for each backend service
response_times = {service: 0 for service in backend_services}

# Current service index and weights
current_service_index = 0
weights = [1] * len(backend_services)  # You can assign weights as needed

# Initialize request number
request_number = 0

@app.route('/')
def load_balancer():
    global current_service_index, request_number

    # Increment the request number for each request
    request_number += 1

    # Find the service with the least response time
    min_response_time = min(response_times.values())
    for service, response_time in response_times.items():
        if response_time == min_response_time:
            current_service = service
            break

    try:
        start_time = time.time()
        response = requests.get(f'http://{current_service}', timeout=5)
        end_time = time.time()

        # Update response time for the selected service
        response_times[current_service] += (end_time - start_time)

        # Log the response times array and request number
        with open('logs.txt', 'a') as log_file:
            log_message = f"Request {request_number}: {response_times}\n"
            log_file.write(log_message)

        return Response(response.content, status=response.status_code, content_type=response.headers['content-type'])
    except requests.exceptions.RequestException as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
