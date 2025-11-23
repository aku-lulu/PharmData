import configparser
import os
import re
import requests
from bs4 import BeautifulSoup
from Utilities.ReadConfig import ConfigRoad


class BiogridUpdate:
    def __init__(self, config_path=ConfigRoad):
        self.config_path = config_path
        self.config = configparser.ConfigParser()

    def extract_version_from_html(self, html_content):
        """
        提取版本号
        :param html_content: 页面内容
        :return: 提前到的版本号
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        page_text = soup.get_text()
        version_matches = re.findall(r'BIOGRID-\d+\.\d+\.\d+', page_text)

        if version_matches:
            unique_versions = list(set(version_matches))
            latest_version = self._select_latest_version(unique_versions)
            return latest_version
        return None

    def _select_latest_version(self, versions):
        """
        从版本列表中选择最新版本
        :param versions: 版本列表
        :return: 最新版本号
        """
        if not versions:
            return None

        def version_key(version_str):
            """
            版本号排序函数
            :param version_str: 版本字符串
            :return: 版本号元组
            """
            match = re.search(r'BIOGRID-(\d+)\.(\d+)\.(\d+)', version_str)
            if match:
                return tuple(map(int, match.groups()))
            return (0, 0, 0)

        try:
            sorted_versions = sorted(versions, key=version_key, reverse=True)
            return sorted_versions[0]
        except:
            return versions[0]

    def get_file_name_from_config(self):
        """
        从配置文件中获取版本信息
        :return: 获取到的文件信息
        """
        if not os.path.exists(self.config_path):
            return None

        self.config.read(self.config_path, encoding='utf-8')
        file_name = self.config.get('biogrid', 'file_name')
        return file_name

    def compare_versions(self, web_version, config_version):
        """
        比较版本号是否一致
        :param web_version: 网页中的版本号
        :param config_version: 配置文件中的版本号
        :return: 比较结果
        """
        if not web_version or not config_version:
            return {
                'is_same': False,
                'message': '版本信息不完整，无法比较',
                'web_version': web_version,
                'config_version': config_version
            }

        is_same = (web_version == config_version)

        if is_same:
            message = "无需更新"
        else:
            message = "需要更新"

        return {
            'is_same': is_same,
            'message': message,
            'web_version': web_version,
            'config_version': config_version
        }

    def check_biogrid_version_update(self, url):
        """
        检查版本更新
        :param url: 网页
        :return: 检查结果
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            web_version = self.extract_version_from_html(response.text)
            config_version = self.get_file_name_from_config()
            result = self.compare_versions(web_version, config_version)
            return result

        except requests.RequestException as e:
            return {
                'is_same': False,
                'message': f'网络请求失败: {e}',
                'web_version': None,
                'config_version': None
            }
        except Exception as e:
            return {
                'is_same': False,
                'message': f'检查失败: {e}',
                'web_version': None,
                'config_version': None
            }