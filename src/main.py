from clize import run
from api_gateway import remove_api, create_api, deploy_api, test_api
from lambda_functions import remove_function, create_lambda, deploy_lambda
from settings import PYTHON_LAMBDA_NAME, AWS_ACCOUNT_NUMBER

def start(op = None):
    
    if not AWS_ACCOUNT_NUMBER:
        return 'You need to export the `AWS_ACCOUNT_NUMBER`. Exiting.'

    if op == 'reset':
        remove_api()
        remove_function(PYTHON_LAMBDA_NAME)
        step = "✅ Removed existing named lambda/api"
        return step

    # -- Step 1/7 -- #
    step = "1. Remove existing named lambda/api"
    remove_api()
    remove_function(PYTHON_LAMBDA_NAME)
    step = "\n✅ Remove existing named lambda/api"
    output = step
    # -- Step 2/7 -- #
    step = "\n2. Create the lambda"
    role_arn = create_lambda()
    step = "\n✅ Create the lambda"
    output += step
    # -- Step 3/7 -- #
    step = "\n3. Deploy the lambda"
    role_arn = deploy_lambda(role_arn)
    step = "\n✅ Deploy the lambda"
    output += step
    # -- Step 4/7 -- #
    step = "\n4. Remove any existing API"
    remove_api()
    step = "\n✅ Remove any existing API"
    output += step
    # -- Step 5/7 -- #
    step = "\n5. Create API"
    api, route = create_api()
    step = "\n✅ Create API"
    output += step
    # -- Step 6/7 -- #
    step = "\n6. Deploy API"
    deployment = deploy_api(api)
    step = "\n✅ Deploy API"
    output += step
    # -- Step 7/7 -- #
    step = "\n7. Test API"
    response = test_api(api, route)
    step = "\n✅ Test API"
    output += step
    output += f"\n{response}"

    return output

if __name__ == '__main__':
    output = run(start)
    print(output)