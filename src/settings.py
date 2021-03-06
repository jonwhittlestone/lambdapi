import os

AWS_REGION = 'eu-west-2'
AWS_ACCOUNT_NUMBER = os.environ.get('AWS_ACCOUNT_NUMBER')

PYTHON_LAMBDA_NAME = 'PythonLambdaFunction'
LAMBDA_POLICY_NAME = 'LambdaS3AccessPolicy'
LAMBDA_ROLE = 'Lambda_Execution_Role'
LAMBDA_TIMEOUT=10
LAMBDA_MEMORY=128
PYTHON_36_RUNTIME = 'python3.6'

PYTHON_LAMBDA_API_PERMISSION_STATEMENT_ID = f'{PYTHON_LAMBDA_NAME}_APIGATEWAY_EXAMPLE'
