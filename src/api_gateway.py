from clize import run
import pprint
# from lambda_functions import V
from settings import PYTHON_LAMBDA_NAME, AWS_REGION, AWS_ACCOUNT_NUMBER, PYTHON_LAMBDA_API_PERMISSION_STATEMENT_ID
from helpers import apigateway_client, lambda_client, test_endpoint
from lambda_functions import remove_permission as remove_lambda_permission

API_NAME = 'hello-world-v2'

def get_or_create_api(api_name):
    apis = apigateway_client().get_apis()
    for api in apis.get('Items'):
        if api.get('Name') == api_name:
            return api
    
    return apigateway_client().create_api(
        # AllowMethods=['GET'],
        Name=api_name,
        ProtocolType='HTTP'
    )

def remove_api():
    remove_lambda_permission()
    api = get_or_create_api(API_NAME)
    ret = apigateway_client().delete_api(ApiId=api.get('ApiId'))
    resp = ret['ResponseMetadata']
    if resp.get('HTTPStatusCode') == 204:
        ret = f"API {api.get('ApiId')} removed."
    else:
        ret = f"Error removing API {api.get('ApiId')}"
    return ret


def create_api():
    api = get_or_create_api(API_NAME)
    api_id = api.get('ApiId')
    ret = api

    # get URI of Lambda
    try:
        fn = lambda_client().get_function(FunctionName=PYTHON_LAMBDA_NAME)
        fn_arn = fn.get('Configuration')['FunctionArn']
    except (KeyError, lambda_client().exceptions.ResourceNotFoundException):
        return f"\nLambda {PYTHON_LAMBDA_NAME} non-existent. Unable to continue.\n"

    # Create an integration
    integration = apigateway_client().create_integration(
        ApiId=api_id,
        IntegrationMethod='POST',
        IntegrationType='AWS_PROXY',
        IntegrationUri=fn_arn,
        PayloadFormatVersion='2.0'
    )
    # Create a route in the API
    route = apigateway_client().create_route(
        ApiId=api_id,
        Target=f"integrations/{integration.get('IntegrationId')}",
        RouteKey='GET /hello-world'
    )
    return api, route

def deploy_api(api):
    api_id = api.get('ApiId')
    deployment = apigateway_client().create_deployment(
        ApiId=api.get('ApiId'),
        Description='Deploys the hello-world endpoint.'
    )
    stage = apigateway_client().create_stage(
        ApiId=api.get('ApiId'),
        DeploymentId=deployment.get('DeploymentId'),
        StageName='$default',
        AutoDeploy=True
    )

    response = lambda_client().add_permission(
        FunctionName=PYTHON_LAMBDA_NAME,
        StatementId=PYTHON_LAMBDA_API_PERMISSION_STATEMENT_ID,
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:{AWS_REGION}:{AWS_ACCOUNT_NUMBER}:{api_id}/*/GET/hello-world'
    )
    return deployment

def test_api(api, route):
    method, route = route.get('RouteKey').split(' ')
    endpoint = f"{api.get('ApiEndpoint')}{route}"
    endpoint_title = f'{method} {endpoint}'
    # print(f"API Status: {deployment.get('DeploymentStatus')}.\nCalling: {endpoint_title}\n")

    return f"SERVERLESS ENDPOINT RESPONSE from {endpoint} : \n{test_endpoint(endpoint)}"

def api_operations(type = None):
    '''
        see: https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway-tutorial.html
    '''
    if type == 'create':
        remove_api()
        api, route = create_api()
        deployment = deploy_api(api)
        return test_api(api, route)

    if type == 'reset':
        return remove_api()

if __name__ == '__main__':
    output = run(api_operations)
    print(output)