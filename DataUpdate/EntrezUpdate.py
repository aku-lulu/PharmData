import configparser
import re
from typing import Optional
from urllib.request import urlopen

from Utilities.ReadConfig import ConfigRoad


class EntrezUpdate:
    """NCBI FTP日期检查器"""

    def __init__(self):
        self.config_file = ConfigRoad
        self.config = configparser.ConfigParser()
        self.config.read(ConfigRoad)

    def get_html_content(self) -> Optional[str]:
        """
        获取网页内容
        :return: 获取到的内容
        """
        try:
            update_url = self.config.get('entrez', 'update_url')
            with urlopen(update_url) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"获取失败: {e}")
            return None

    def extract_date(self, html_content: str) -> Optional[str]:
        """
        在网页中提取日期
        :param html_content: 网页内容
        :return: 日期字符串
        """
        pattern = r'All_Data\.gene_info\.gz[^>]*>.*?<\/a>\s*(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})'
        match = re.search(pattern, html_content)

        if match:
            date_str, time_str = match.groups()
            return f"{date_str} {time_str}"
        return None

    def get_current_date(self) -> Optional[str]:
        """
        获取配置文件中的日期
        :return: 配置文件中的日期
        """
        return self.config.get('entrez', 'last_modified')

    def check_and_update(self) -> bool:
        """
        检查日期，更新配置文件
        :return: 需要更新返回True，不需要更新返回False
        """
        # 获取网页内容
        html_content = self.get_html_content()
        if not html_content:
            print("无法获取网页内容")
            return False

        # 提取日期
        new_date = self.extract_date(html_content)
        if not new_date:
            print("无法提取日期")
            return False

        # 获取当前日期
        current_date = self.get_current_date()
        print(f"当前日期: {current_date}")
        print(f"最新日期: {new_date}")

        # 比较日期
        if current_date == new_date:
            print("无需更新")
            return False
        else:
            print("需要更新")
            self.config['entrez']['last_modified'] = new_date
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            return True