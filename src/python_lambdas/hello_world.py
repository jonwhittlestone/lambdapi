import json

def respond(err, res=None):
    return {
        'statusCode': 400 if err else 200,
        'body': 'Python error' if err else json.dumps(res),
        'message': 'Python error' if err else res.get('message'),
        'headers': {
            'Content-Type': 'application/json'
        }
    }

def parse_parameters(event):
    e = None
    returnParameters = {}
    try:
        if event.get('queryStringParameters',False):
            returnParameters = event['queryStringParameters'].copy()
    except Exception as e:
        print(e)
        returnParameters = {}

    return {'querystring_params:': returnParameters, 'err':e}

def handler(event, context):
    validated_parameters = {}
    response = {}

    try:
        validated_parameters = parse_parameters(event)
    except Exception as e:
        return respond(e, validated_parameters.get('querystring_params', None))
    
    response = validated_parameters
    response['message'] = 'Hello Serverless World'
    return respond(None, response)