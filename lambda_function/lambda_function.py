import json
import requests
from requests_ip_rotator import ApiGateway

def lambda_handler(event, context):
    # Extract the URL from the query string parameters
    target_url = event['queryStringParameters'].get('url')
    
    if not target_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No target URL provided.'})
        }
    
    # Initialize the gateway object
    gateway = ApiGateway(target_url, regions=['ca-west-1', 'ca-central-1'])
    gateway.start()

    # Create a session and attach the gateway to the session
    session = requests.Session()
    session.mount(target_url, gateway)

    # Send the request through the rotated IP
    try:
        response = session.get(target_url)
        status_code = response.status_code
        response_text = response.text

        # Shutdown the gateway to avoid extra charges
        gateway.shutdown()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'status_code': status_code,
                'response': response_text[:1000]  # Output a snippet for debugging
            })
        }

    except Exception as e:
        gateway.shutdown()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
