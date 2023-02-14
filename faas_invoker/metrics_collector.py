# 用于从Prometheus中获取函数的调用日志
'''
获取所有metrics的名称: curl http://127.0.0.1:9090/api/v1/label/__name__/values

'''
import csv

import requests
from urllib.parse import urljoin
import json


class Prometheus_collector:
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


# 从自己做的function runtime中获取metrics
class Runtime_collector:
    def __init__(self) -> None:
        pass

    def load_data_dict_list(self, csv_path=None):
        # 从csv文件中加载result_dict_list
        # 读取csv文件
        data_dict_list = []
        with open(csv_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                input_obj = row.get("input_obj")
                log_dict = row.get("log_dict")
                result_dict = row.get("result_dict")
                resource_dict = row.get("resource_dict")

                # json不规范需要replace修正
                input_obj = json.loads(input_obj.replace("'", '"').replace("True", "true").replace("False", "false"))
                log_dict = json.loads(log_dict.replace("'", '"').replace("True", "true").replace("False", "false"))
                result_dict = json.loads(
                    result_dict.replace("'", '"').replace("True", "true").replace("False", "false"))
                resource_dict = json.loads(
                    resource_dict.replace("'", '"').replace("True", "true").replace("False", "false"))

                res_dict = {
                    "input_obj": input_obj,
                    "log_dict": log_dict,
                    "result_dict": result_dict,
                    "resource_dict": resource_dict
                }
                data_dict_list.append(res_dict)
        return data_dict_list

    def data_dict_list_filter(self, node_name_list=None, cpu_list=None, cold_start=None, data_dict_list=None) -> list:
        # 对data_dict_list进行过滤
        filtered_data_dict_list = []
        for data_dict in data_dict_list:
            input_obj = data_dict.get("input_obj")
            log_dict = data_dict.get("log_dict")
            result_dict = data_dict.get("result_dict")
            resource_dict = data_dict.get("resource_dict")
            # 分别针对指标进行筛选
            if node_name_list is not None:
                node_name = resource_dict.get("node_name")
                if node_name not in node_name_list:
                    continue
            if cpu_list is not None:
                cpu = resource_dict.get("cpu")
                if cpu not in cpu_list:
                    continue
            if cold_start is not None:
                cold_start_flag = log_dict.get("cold_start")
                if cold_start_flag != cold_start:
                    continue
            filtered_data_dict_list.append(data_dict)
        return filtered_data_dict_list

    def get_mapping_delay_time_series(self, data_dict_list):
        # 从result_dict_list中获取mapping_delay的时间序列
        mapping_delay_tuple_list = []

        for data_dict in data_dict_list:
            input_obj = data_dict.get("input_obj")
            log_dict = data_dict.get("log_dict")
            result_dict = data_dict.get("result_dict")

            mapping_delay = log_dict.get("mapping_delay")
            invoke_t = input_obj.get("invoke_t")
            mapping_delay_tuple_list.append((invoke_t, mapping_delay))  # 用元组的第一个元素作为排序的依据

            # print(f"input_obj:{input_obj}")
            # print(f"log_dict:{log_dict}")
            # print(f"result_dict:{result_dict}")

        # 对mapping_delay_tuple_list进行排序
        # print(f"mapping_delay_tuple_list:{mapping_delay_tuple_list}")
        mapping_delay_tuple_list.sort(key=lambda x: x[0])  # 用元组的第一个元素作为排序的依据
        # 用列表中的第二个元素生成新的列表
        mapping_delay_list = [x[1] for x in mapping_delay_tuple_list]
        return mapping_delay_list

    def get_request_count_time_series(self, data_dict_list):
        # 从result_dict_list中获取函数请求量的时间序列

        pass

    def get_latency_time_series(self, data_dict_list):
        # 从result_dict_list中获取函数延迟的时间序列
        latency_time_list = []
        latency_time_tuple_list = []

        for data_dict in data_dict_list:
            input_obj = data_dict.get("input_obj")
            log_dict = data_dict.get("log_dict")
            result_dict = data_dict.get("result_dict")

            finish_t = log_dict.get("finish_t")
            invoke_t = input_obj.get("invoke_t")
            latency_t = finish_t - invoke_t
            latency_time_tuple_list.append((invoke_t, latency_t))  # 用元组的第一个元素作为排序的依据

            # print(f"input_obj:{input_obj}")
            # print(f"log_dict:{log_dict}")
            # print(f"result_dict:{result_dict}")

        # 对mapping_delay_tuple_list进行排序
        # print(f"mapping_delay_tuple_list:{mapping_delay_tuple_list}")
        latency_time_tuple_list.sort(key=lambda x: x[0])  # 用元组的第一个元素作为排序的依据
        # 用列表中的第二个元素生成新的列表
        latency_time_list = [x[1] for x in latency_time_tuple_list]
        return latency_time_list

    def get_compute_time_series(self, data_dict_list):
        # 从data_dict_list中获取函数计算时间的时间序列
        compute_time_list = []
        compute_time_tuple_list = []

        for data_dict in data_dict_list:
            input_obj = data_dict.get("input_obj")
            log_dict = data_dict.get("log_dict")
            result_dict = data_dict.get("result_dict")

            invoke_t = input_obj.get("invoke_t")
            compute_t = log_dict.get("compute_t")

            compute_time_tuple_list.append((invoke_t, compute_t))  # 用元组的第一个元素作为排序的依据

            # print(f"input_obj:{input_obj}")
            # print(f"log_dict:{log_dict}")
            # print(f"result_dict:{result_dict}")

        # 对mapping_delay_tuple_list进行排序
        # print(f"mapping_delay_tuple_list:{mapping_delay_tuple_list}")
        compute_time_tuple_list.sort(key=lambda x: x[0])  # 用元组的第一个元素作为排序的依据
        # 用列表中的第二个元素生成新的列表
        compute_time_list = [x[1] for x in compute_time_tuple_list]
        return compute_time_list

    def get_cold_start_time_series(self, data_dict_list):
        # 从data_dict_list中获取函数冷启动的时间序列
        pass

    def get_scheduled_location_list(self, data_dict_list):
        # 从data_dict_list中获取函数被调度的位置的列表
        # 位置用 pod_name 和 node_name来描述
        scheduled_location_list = []
        scheduled_location_tuple_list = []

        for data_dict in data_dict_list:
            input_obj = data_dict.get("input_obj")
            log_dict = data_dict.get("log_dict")
            result_dict = data_dict.get("result_dict")
            resource_dict = data_dict.get("resource_dict")

            invoke_t = input_obj.get("invoke_t")

            pod_name = resource_dict.get("hostname")
            node_name = resource_dict.get("nodename")

            location = {
                "pod_name": pod_name,
                "node_name": node_name,
            }

            scheduled_location_tuple_list.append((invoke_t, location))  # 用元组的第一个元素作为排序的依据

            # print(f"input_obj:{input_obj}")
            # print(f"log_dict:{log_dict}")
            # print(f"result_dict:{result_dict}")

        # 进行排序
        scheduled_location_tuple_list.sort(key=lambda x: x[0])  # 用元组的第一个元素作为排序的依据
        # 用列表中的第二个元素生成新的列表
        scheduled_location_list = [x[1] for x in scheduled_location_tuple_list]
        return scheduled_location_list
        pass


class Test_Runtime_collector:
    def __init__(self):
        pass

    def test_load_result_dict_list(self):
        my_runtime_collector = Runtime_collector()
        res = my_runtime_collector.load_data_dict_list(csv_path="logs/example.csv")
        print(f"load_result_dict_list:{res}")

    def test_get_concurrency_time_series(self):
        my_runtime_collector = Runtime_collector()
        data_dict_list = my_runtime_collector.load_data_dict_list(csv_path="logs/example_20.csv")
        res = my_runtime_collector.get_mapping_delay_time_series(data_dict_list=data_dict_list[0:20])
        print(f"get_mapping_delay_time_series:{res}")

    def test_get_latency_time_series(self):
        my_runtime_collector = Runtime_collector()
        data_dict_list = my_runtime_collector.load_data_dict_list(csv_path="logs/example_20.csv")
        res = my_runtime_collector.get_latency_time_series(data_dict_list=data_dict_list[0:20])
        print(f"get_latency_time_series:{res}")

    def test_get_compute_time_series(self):
        my_runtime_collector = Runtime_collector()
        data_dict_list = my_runtime_collector.load_data_dict_list(csv_path="logs/example_20.csv")
        res = my_runtime_collector.get_compute_time_series(data_dict_list=data_dict_list[0:20])
        print(f"get_compute_time_series:{res}")

    def test_get_scheduled_location_list(self):
        my_runtime_collector = Runtime_collector()
        data_dict_list = my_runtime_collector.load_data_dict_list(csv_path="logs/example_20.csv")
        res = my_runtime_collector.get_scheduled_location_list(data_dict_list=data_dict_list[0:20])
        print(f"get_scheduled_location_list:{res}")


if __name__ == "__main__":
    my_test = Test_Runtime_collector()
    my_test.test_load_result_dict_list()
    # my_test.test_get_concurrency_time_series()
    # my_test.test_get_latency_time_series()
    # my_test.test_get_compute_time_series()
    my_test.test_get_scheduled_location_list()
