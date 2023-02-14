import time
from datetime import datetime
import copy
from faas_invoker.knative import KnativeInvoker
from multiprocessing import Manager
import multiprocessing as mp
import json
import csv
import os


class Replayer:
    def __init__(self, invoker=KnativeInvoker(), log_dir="./logs", ):
        self.invoker = invoker
        self.log_dir = log_dir
        pass

    def trace_replayer(self, namespace, function_name, handler, invocation_in_sec_list, is_save_csv=False, save_name=None):
        m = Manager()
        res_queue = m.Queue()

        process_list = []

        for timestamp, invocation in enumerate(invocation_in_sec_list):
            start_time = time.time()
            print(f"当前模拟调用第{timestamp}秒")
            n_request = invocation
            # 如果 n_request == 0，跳过调用
            if n_request == 0:
                pass
            else:
                p = mp.Process(target=self.invoke_in_sec,
                                            args=(res_queue, namespace, function_name, handler, timestamp, n_request))
                process_list.append(p)
                p.start()
            end_time = time.time()
            send_time = end_time - start_time
            print(f"休息{1 - send_time}秒")
            time.sleep(1 - send_time)

        for process in process_list:
            process.join()

        # 展示结果保存
        print("从缓存队列中取结果!")
        result_dict_list = []
        while not res_queue.empty():
            res = res_queue.get()
            # print(f"get from queue res: {res}")
            try:
                res = [json.loads(item) for item in res]
                result_dict_list.extend(res)
            except:
                pass

        # print(f"log_dict_list:{result_dict_list}")

        if is_save_csv:
            os.makedirs(self.log_dir, exist_ok=True)
            date = str(datetime.now())
            if save_name == None:
                save_name = f"replayer_log_{date}.csv"
            else:
                save_name = save_name.split(".")[0] + f".csv"

            log_path = os.path.join(self.log_dir, save_name)

            with open(log_path, 'w', newline='') as csvfile:
                fieldnames = list(result_dict_list[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(result_dict_list)
            print(f"写入csv:{log_path}")

        return result_dict_list

    def invoke_in_sec(self, res_queue, namespace="faas-scaler", function_name="test-intra-parallelism", handler="matmul", timestamp=0, n_request=1):
        input_obj = {
            "function_name": function_name, # 调用的函数名称
            "namespace": namespace, # 调用的函数命名空间
            "invoke_t": time.time(),  # 发出调用请求的时间戳
            "timestamp": timestamp,  # 模拟请求调用的第几秒
            "n_request": n_request,  # 一秒调用有几个并发请求
            "index": 0,  # 第几个并发请求
            "input_data_key": "input_data_key",
            "output_data_key": "output_data_key",
            "handler": handler,
        }
        # 开始并发调用
        data_list = []
        for index in range(n_request):
            _input_obj = copy.deepcopy(input_obj)
            _input_obj["index"] = index
            data_list.append(_input_obj)

        response = self.invoker.sync_map(
            namespace=namespace,
            function_name=function_name,
            data_list=data_list,
        )
        res_queue.put(response)
        return response


    def test_invoke_in_sec(self):
        m = Manager()
        res_queue = m.Queue()
        self.invoke_in_sec(res_queue=res_queue, namespace="faas-scaler", function_name="test-intra-parallelism",handler="matmul", timestamp=0, n_request=3)
        # 展示结果保存
        print("从缓存队列中取结果!")
        data_dict_list = []
        while not res_queue.empty():
            res = res_queue.get()
            data_dict_list.extend(res)

        print(f"data_dict_list:{data_dict_list}")

    def test_trace_replayer(self):
        self.trace_replayer(
            namespace="faas-scaler",
            function_name="test-intra-parallelism",
            handler="matmul",
            invocation_in_sec_list=[1,0,0,5,0,3,0,1,2,4,0,0,0,0,1,1,1,4,4,0,0,0,1],
            is_save_csv=True
        )

    def test_trace_replayer_custom_handler(self):
        handler_name = input("请输入handler_name:")
        self.trace_replayer(
            namespace="faas-scaler",
            function_name="test-intra-parallelism",
            handler=handler_name,
            invocation_in_sec_list=[1,0,0,5,0,0,0,1,2,0,0,0,4,0,1,1,1,4,4,0],
            is_save_csv=True
        )



if __name__ == "__main__":
    replayer = Replayer()
    # replayer.test_invoke_in_sec()

    # 测试 test_invoke_in_sec
    # replayer.test_trace_replayer()
    replayer.test_trace_replayer_custom_handler()

