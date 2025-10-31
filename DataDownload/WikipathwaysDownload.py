import traceback
import configparser
import os
from tqdm import tqdm
from urllib import request
from Utilities.ReadConfig import ConfigRoad


class HTTP:
    @staticmethod
    def download(url, dir, filename):
        """
        下载文件函数
        :param url:文件下载网址
        :param dir: 保存目录
        :param filename: 保存文件名
        :return:
        """
        # 创建目录
        os.makedirs(dir, exist_ok=True)
        save_path = os.path.join(dir, filename)
        print(f"Downloading from {url} to {save_path}")
        try:
            # tqdm创建进度条
            with tqdm(unit='B', unit_scale=True, miniters=1, desc=filename) as t:
                # 下载文件
                request.urlretrieve(url, save_path, reporthook=HTTP.report_hook(t))
            print(f"Downloaded to {save_path}")
        except Exception as e:
            print(f"Failed to download {url}. Error: {e}")

    @staticmethod
    def report_hook(t):
        """
        创建下载进度回调函数
        :param t: tqdm进度条对象
        :return: update_to进度更新函数
        """
        last_b = [0]

        def update_to(b=1, bsize=1, tsize=None):
            """
            进度更新函数
            :param b: 已下载块数
            :param bsize: 块大小
            :param tsize: 总大小
            :return:
            """
            if tsize is not None:
                # 设置总大小
                t.total = tsize
            # 更新进度条
            t.update((b - last_b[0]) * bsize)
            # 更新块数
            last_b[0] = b

        return update_to


class Wikipathway_Download:
    """
    Wikipathway数据下载类
    """
    def __init__(self):
        self.cfgfile = ConfigRoad

    def start(self):
        """
        数据下载函数
        :return:
        """
        # 读取配置文件
        config = configparser.ConfigParser()
        config.read(self.cfgfile, encoding="utf-8")
        # 从配置文件中获取相关参数
        ur = config.get('wikipathway', 'source_url_1')
        file_name = config.get('wikipathway', 'file_name')
        data_path = config.get('wikipathway', 'data_path_1')
        url = ur + file_name

        filename = os.path.basename(url)

        print(f"Wikipathway download URL: {url}")
        print(f"Wikipathway save path: {data_path}")

        print(f"Checking if file needs to be downloaded to {os.path.join(data_path, filename)}")

        if not os.path.exists(os.path.join(data_path, filename)):
            try:
                HTTP.download(url, data_path, filename)
            except Exception:
                traceback.print_exc()

    def pause(self):
        pass

    def stop(self):
        pass

    def get_status(self):
        pass
