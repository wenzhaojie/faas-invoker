import time
import copy
from knative import KnativeInvoker
from multiprocessing import Manager


class Replayer:
    def __init__(self, invoker=KnativeInvoker()):
        self.invoker = invoker
        pass

    def trace_replayer(self, invocation_in_sec_list):
        pass

    def invoke_in_sec(self, res_queue, namespace="faas-scaler", function_name="test-intra-parallelism", handler="matmul", timestamp=0, n_request=1):
        input_obj = {
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
        log_dict_list = []
        while not res_queue.empty():
            res = res_queue.get()
            log_dict_list.extend(res)

        print(f"log_dict_list:{log_dict_list}")


if __name__ == "__main__":
    replayer = Replayer()
    replayer.test_invoke_in_sec()


