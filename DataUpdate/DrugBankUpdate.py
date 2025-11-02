import configparser
import os
import re
import requests
from bs4 import BeautifulSoup
from Utilities.ReadConfig import ConfigRoad


class DrugBankUpdate:
    def __init__(self, config_path=ConfigRoad):
        self.config_path = config_path
        self.config = configparser.ConfigParser()

    def extract_version_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        version_pattern = r'\b(\d+\.\d+\.\d+)\b'

        td_elements = soup.find_all('td')
        for td in td_elements:
            td_text = td.get_text().strip()
            version_match = re.search(version_pattern, td_text)
            if version_match:
                version = version_match.group(1)
                return version
        return None

    def update_config_version(self, new_version):
        try:
            self.config.read(self.config_path, encoding='utf-8')
            if not self.config.has_section('drugbank'):
                self.config.add_section('drugbank')

            self.config.set('drugbank', 'version', new_version)

            with open(self.config_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            return True
        except Exception as e:
            return False

    def compare_versions(self, web_version, config_version):
        if not web_version or not config_version:
            return {
                'is_same': False,
                'need_update': True,
                'message': '版本信息不完整，建议更新',
                'web_version': web_version,
                'config_version': config_version
            }

        is_same = (web_version == config_version)

        if is_same:
            message = f"无需更新"
            need_update = False
        else:
            message = f"需要更新"
            need_update = True

        return {
            'is_same': is_same,
            'need_update': need_update,
            'message': message,
            'web_version': web_version,
            'config_version': config_version
        }

    def check_drugbank_version_update(self):
        try:
            self.config.read(self.config_path, encoding='utf-8')
            url = self.config.get('drugbank', 'url')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()

            web_version = self.extract_version_from_html(response.text)
            config_version = self.config.get('drugbank', 'version')

            result = self.compare_versions(web_version, config_version)

            return result

        except Exception as e:
            return {
                'is_same': False,
                'need_update': False,
                'message': f'检查失败: {e}',
                'web_version': None,
                'config_version': None
            }

    def auto_update_check(self):
        result = self.check_drugbank_version_update()

        if result['need_update'] and result['web_version']:
            print("需要更新")
            success = self.update_config_version(result['web_version'])
            if success:
                print("配置文件已更新")
                return True
            else:
                print("配置文件更新失败")
                return True
        else:
            print("无需更新")
            return False