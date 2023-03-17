import json
import os
import time
from multiprocessing.pool import Pool

import boto3

# 如果没有指定 aws_access_key_id, aws_secret_access_key, aws_session_token 则从环境变量中获取
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.environ.get("AWS_SESSION_TOKEN")
region_name = os.environ.get("AWS_REGION_NAME", "us-east-1")

client = boto3.client(
    'lambda', region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token
)


class LambdaInvoker:
    def __init__(self, region_name="us-east-1", aws_access_key_id=None, aws_secret_access_key=None,
                 aws_session_token=None):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token

    @staticmethod
    def invoke_sync_function(namespace=None, function_name=None, data=None):
        res = client.invoke(FunctionName=function_name, InvocationType='RequestResponse', Payload=data)
        return res['Payload'].read().decode('utf-8')

    def invoke_sync_function_dict(self, args):
        function_name = args["function_name"]
        data = args["data"]
        namespace = args["namespace"]
        res = self.invoke_sync_function(namespace=namespace, function_name=function_name, data=data)
        return res

    def sync_map(self, namespace="faas-scaler", function_name="helloworld-python", data_list=None):
        if data_list is None:
            data_list = []
        map_data_list = [{
            "namespace": namespace,
            "function_name": function_name,
            "data": data,
        }
            for data in data_list]

        with Pool(processes=len(map_data_list)) as pool:
            results = pool.map(self.invoke_sync_function_dict, map_data_list)
        return results


if __name__ == '__main__':
    # 测试
    my_invoker = LambdaInvoker(region_name="us-east-1")
    # 测试时延
    start_time = time.time()
    res = my_invoker.invoke_sync_function(function_name="helloworld-python", data=json.dumps({"name": "test"}))
    print(res)
    end_time = time.time()
    print(end_time - start_time)

    response = my_invoker.sync_map(function_name="helloworld-python",
                                   data_list=["123", "234", "345"])
    print(response)
