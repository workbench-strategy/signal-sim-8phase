# Example GCP Cloud Function
import functions_framework

@functions_framework.http
def hello_http(request):
    return "Hello from Cloud Function!"
