import os
import io
import boto3
import requests
from zipfile import ZipFile
from settings import AWS_REGION

def lambda_client():
    aws_lambda = boto3.client('lambda', region_name=AWS_REGION)
    """ :type : pyboto3.lambda """
    return aws_lambda


def iam_client():
    iam = boto3.client('iam')
    """ :type : pyboto3.iam """
    return iam

def apigateway_client():
    apigateway = boto3.client('apigatewayv2', region_name=AWS_REGION)
    """ :type : pyboto3.apigatewayv2 """
    return apigateway

def test_endpoint(url):

    payload = {}
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    return response.text.encode('utf8')


class Zipper:
    
    @staticmethod
    def make_bytes(path):
        buf = io.BytesIO()
        with ZipFile(buf, 'w') as z:
            for full_path, archive_name in Zipper.files_to_zip(path):
                z.write(full_path, archive_name)
        total = buf.getvalue()
        return total
    
    @staticmethod
    def files_to_zip(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                full_path = os.path.join(root, f)
                archive_name = full_path[len(path) + len(os.sep):]
                yield full_path, archive_name