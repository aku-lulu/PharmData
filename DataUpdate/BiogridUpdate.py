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
        soup = BeautifulSoup(html_content, 'html.parser')
        page_text = soup.get_text()
        version_matches = re.findall(r'BIOGRID-\d+\.\d+\.\d+', page_text)

        if version_matches:
            unique_versions = list(set(version_matches))
            latest_version = self._select_latest_version(unique_versions)
            return latest_version
        return None

    def _select_latest_version(self, versions):
        if not versions:
            return None

        def version_key(version_str):
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
        if not os.path.exists(self.config_path):
            return None

        self.config.read(self.config_path, encoding='utf-8')
        file_name = self.config.get('biogrid', 'file_name')
        return file_name

    def compare_versions(self, web_version, config_version):
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