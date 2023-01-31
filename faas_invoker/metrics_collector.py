# 用于从Prometheus中获取函数的调用日志
'''
获取所有metrics的名称: curl http://127.0.0.1:9090/api/v1/label/__name__/values

'''
import requests
from urllib.parse import urljoin
import json


class Metric_collector:
    def __init__(self, prometheus_ip="127.0.0.1", port=9090) -> None:
        self.base_url = f"http://{prometheus_ip}:{port}"
        pass

    # 获取Prometheus的所有metrics name
    def get_all_metric_name_list(self):
        req_url = urljoin(self.base_url, "api/v1/label/__name__/values")
        response = requests.get(
            url=req_url
        )
        res_dict = json.loads(response.content)
        if res_dict["status"] == "success":
            return res_dict["data"]
        else:
            return []

    # 获取指定metric name的历史数据
    def get_by_metric_name(self, metric_name):
        pass


if __name__ == "__main__":
    my_metric_collector = Metric_collector()
    res = my_metric_collector.get_all_metric_name_list()
    print(f"get_all_metric_name_list:{res}")
    print(f"type:{type(res)}")