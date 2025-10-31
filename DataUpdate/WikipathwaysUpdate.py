import requests
import configparser

from Utilities.WikipathwayZipName_LatestTime import extract_homo_sapiens_files_precise
from Utilities.ReadConfig import ConfigRoad

class WikipathwaysUpdate:
    """
    Wikipathway数据更新检查类
    """
    def __init__(self, config_file=ConfigRoad):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding="utf-8")

    def get_remote_file_info(self, directory_url):
        """
        获取网站信息
        :param directory_url: wikipathway文件下载目录的url
        :return: 包含文件信息的字典
        """
        try:
            response = requests.get(directory_url, timeout=10)
            response.raise_for_status()

            file_info = extract_homo_sapiens_files_precise(response.text)
            return file_info

        except Exception as e:
            print(f"获取网站信息失败: {e}")
            return []

    def get_local_last_modified(self):
        """
        获取本地的修改时间记录记录
        :return: 配置文件中的last_modified记录
        """
        try:
            if self.config.has_option('wikipathway', 'last_modified'):
                last_modified = self.config.get('wikipathway', 'last_modified')
                return last_modified
            else:
                return None
        except Exception as e:
            print(f"从config文件读取last_modified失败: {e}")
            return None

    def check_wikipathway_update(self):
        """
        检查Wikipathway数据是否需要更新
        :return: 更新检查结果的字典
        """
        try:
            directory_url = self.config.get('wikipathway', 'directory_url')

            # 获取网站信息
            remote_files = self.get_remote_file_info(directory_url)
            if not remote_files:
                print("未找到网站信息")
                return {
                    'needs_update': True,
                    'reason': '未找到网站信息',
                    'remote_info': None
                }

            # 取第一个Homo_sapiens文件
            latest_file = remote_files[0]
            remote_last_modified = latest_file['last_modified']

            # 获取本地记录的Last Modified时间
            local_last_modified = self.get_local_last_modified()

            # 比较时间
            if not local_last_modified:
                print("本地无last_modified记录，需要下载")
                return {
                    'needs_update': True,
                    'reason': '本地无记录',
                    'remote_info': latest_file
                }

            if remote_last_modified != local_last_modified:
                print(f"文件已更新，需要下载 (网站: {remote_last_modified}, 本地: {local_last_modified})")
                return {
                    'needs_update': True,
                    'reason': '文件已更新',
                    'remote_info': latest_file
                }
            else:
                print("文件未更新，无需下载")
                return {
                    'needs_update': False,
                    'reason': '文件未更新',
                    'remote_info': latest_file
                }

        except Exception as e:
            print(f"检查更新失败: {e}")
            return {
                'needs_update': True,
                'reason': f'检查失败: {e}',
                'remote_info': None
            }

