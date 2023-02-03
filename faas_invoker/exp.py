# 运行实验，用于实验测试，并画出主要的结果
from pyplotter import plot
import os

class Exp:
    def __init__(self, root_path="./results", exp_name="exp"):
        self.my_plotter = plot.Plotter()
        self.root_path = root_path
        self.exp_name = exp_name
        # 创建保存结果的文件夹
        self.save_path = os.path.join(root_path, exp_name)
        os.makedirs(name=self.save_path,exist_ok=True)
        pass

    def config(self):
        # 用于配置实验的条件
        pass

    def start_replay(self):
        pass

    def plot_cdf(self, ):

        self.my_plotter.plot_cdfs()
        pass