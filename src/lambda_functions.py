# boto3-lambda/src/lambda_functions.py
import boto3
import json
import os
from helpers import Zipper

LAMBDA_POLICY_NAME = 'LambdaS3AccessPolicy'
LAMBDA_ROLE = 'Lambda_Execution_Role'

LAMBDA_TIMEOUT=10
LAMBDA_MEMORY=128
PYTHON_36_RUNTIME = 'python3.6'
PYTHON_LAMBDA_NAME = 'PythonLambdaFunction'

def lambda_client():
    aws_lambda = boto3.client('lambda', region_name='eu-west-2')
    """ :type : pyboto3.lambda """
    return aws_lambda


def iam_client():
    iam = boto3.client('iam')
    """ :type : pyboto3.iam """
    return iam


def get_or_create_access_policy_for_lambda(policy_name):
    policy = find_policy(policy_name)
    if not policy:
        s3_access_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "s3:*",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "cloudwatch:PutMetricData"
                    ],
                    "Effect": "Allow",
                    "Resource": "*"
                }
            ]
        }

        return iam_client().create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(s3_access_policy_document),
            Description='Allows lambda function to access s3 resources'
        )['Policy']
    
    return policy

    
def find_policy(policy_name):
    for p in iam_client().list_policies(Scope='Local').get('Policies'):
        if p.get('PolicyName') == policy_name:
            return p
        
        
def find_role(lambda_role):
    try:
        role = iam_client().get_role(RoleName=lambda_role)
        if role.get('Role',False):
            return role.get('Role')
    except iam_client().exceptions.NoSuchEntityException:
        pass

    
    
def get_or_create_execution_role_lambda(arn, lambda_role):
    role = find_role(lambda_role)
    if role:
        return role
    
    lambda_execution_assumption_role = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    return iam_client().create_role(
        RoleName=lambda_role,
        AssumeRolePolicyDocument=json.dumps(lambda_execution_assumption_role),
        Description='Gives necessary permissions for lambda to be executed'
    )['Role']

def attach_access_policy_to_execution_role(lambda_role, policy_arn):
     return iam_client().attach_role_policy(RoleName=lambda_role,PolicyArn=policy_arn)
     


def deploy_lambda_function(function_name, runtime, handler, role_arn, source_folder):
    folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), source_folder)
    zip_file = Zipper().make_bytes(path=folder_path)
    return lambda_client().create_function(
        FunctionName=function_name,
        Runtime=runtime,
        Role=role_arn,
        Handler=handler,
        Code={
            'ZipFile': zip_file,
        },
        Timeout=LAMBDA_TIMEOUT,
        MemorySize=LAMBDA_MEMORY,
        Publish=False
    )

def remove_function(lambda_name):
    try:
        return lambda_client().delete_function(FunctionName=lambda_name)
    except lambda_client().exceptions.ResourceNotFoundException:
        pass

def invoke_function(lambda_name):
    return lambda_client().invoke(FunctionName=lambda_name)

if __name__ == '__main__':

    resp = remove_function(PYTHON_LAMBDA_NAME) 
    print(resp)
    print('')

    policy = get_or_create_access_policy_for_lambda(LAMBDA_POLICY_NAME)
    policy_arn = policy.get('Arn')

    role = get_or_create_execution_role_lambda(policy_arn, LAMBDA_ROLE)
    role_arn = role.get('Arn')

    role_policy = attach_access_policy_to_execution_role(LAMBDA_ROLE, policy_arn)
    #print(role_policy)

    print('')
    print('👇 Deploying the Lambda:')
    print(deploy_lambda_function(
        PYTHON_LAMBDA_NAME,
        PYTHON_36_RUNTIME,
        'hello_world.handler',
        role_arn,
        'python_lambdas'
    ))
    
    print('')
    print('👇 Calling it, and printing Lambda response:')
    response = invoke_function(PYTHON_LAMBDA_NAME)
    print(response['Payload'].read().decode())