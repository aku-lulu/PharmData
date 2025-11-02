import configparser
import os
from tqdm import tqdm
import requests
from requests.auth import HTTPBasicAuth
from Utilities.ReadConfig import ConfigRoad

class DrugbankDownload:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(ConfigRoad)
        self.url_front = self.config.get('drugbank', 'source_url_1_front')
        self.url_back = self.config.get('drugbank', 'source_url_1_back')
        self.version = self.config.get('drugbank', 'version')
        self.version = self.version.replace('.', '-')

        self.save_path = self.config.get('drugbank', 'data_path_1')
        self.username = self.config.get('drugbank', 'username', fallback=None)
        self.password = self.config.get('drugbank', 'password', fallback=None)

        self.url = self.url_front + self.version + self.url_back

    def download_file(self, url, save_path):
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))

        try:
            auth = HTTPBasicAuth(self.username, self.password)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, stream=True, auth=auth, headers=headers, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            print(f"文件大小: {total_size / (1024 * 1024):.2f} MB")

            with open(save_path, 'wb') as f, tqdm(
                    desc=os.path.basename(save_path),
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=8192):
                    if data:
                        f.write(data)
                        bar.update(len(data))

            actual_size = os.path.getsize(save_path)
            print(f"下载完成,文件大小: {actual_size / (1024 * 1024):.2f} MB")
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("认证失败：用户名或密码错误")
            else:
                print(f"HTTP错误: {e}")
            return False
        except Exception as e:
            print(f"下载失败: {e}")
            return False

    def start_download(self):
        success = self.download_file(self.url, self.save_path)
        if success:
            print("下载成功！")
        else:
            print("下载失败")