# 根据平台名称，封装KnativeInvoker以及LambdaInvoker
from faas_invoker.knative import KnativeInvoker
from faas_invoker.aws_lambda import LambdaInvoker

class PlatformInvoker:
    def get_invoker(self, platform):
        if platform == "knative":
            return KnativeInvoker()
        elif platform == "lambda":
            return LambdaInvoker()
        else:
            raise Exception("Unknown platform: {}".format(platform))