import configparser
import gzip
import shutil
import requests
from pathlib import Path

from Utilities.ReadConfig import ConfigRoad


class EntrezDownload:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(ConfigRoad)
        self.file_url = self.config.get('entrez', 'source_url_1')
        self.download_dir = self.config.get('entrez', 'data_path_1')
        self.download_dir = Path(self.download_dir)
        self.file_dir = self.config.get('entrez', 'directory_dir')

        # 创建下载目录
        self.download_dir.mkdir(parents=True, exist_ok=True)


    def download_file(self, chunk_size=8192):
        '''
        下载数据库文件
        :param chunk_size:下载块大小
        :return:（success, file_path, message）
        '''
        local_file_path = self.file_dir

        try:
            print(f"开始下载文件: {self.file_url}")

            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            # 获取文件信息
            head_response = session.head(self.file_url, timeout=30)
            head_response.raise_for_status()

            file_size = int(head_response.headers.get('content-length', 0))
            print(f"文件大小: {file_size} bytes")

            # 下载文件
            response = session.get(self.file_url, stream=True, timeout=60)
            response.raise_for_status()

            # 写入文件
            downloaded_size = 0
            with open(local_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # 显示下载进度
                        if file_size > 0:
                            progress = (downloaded_size / file_size) * 100
                            if downloaded_size % (1024 * 1024) == 0:  # 每1MB输出一次
                                print(f"下载进度: {progress:.1f}% ({downloaded_size}/{file_size} bytes)")

            print(f"下载完成: {local_file_path}")

            return True, str(local_file_path), "下载成功"

        except requests.exceptions.RequestException as e:
            error_msg = f"下载失败: {str(e)}"
            print(error_msg)
            return False, None, error_msg

        except Exception as e:
            error_msg = f"发生未知错误: {str(e)}"
            print(error_msg)
            return False, None, error_msg

    def extract_file(self):
        """
        解压.gz文件
        :return: (success, extracted_path, message)
        """
        gz_file_path = self.file_dir
        extracted_file_path = self.file_dir.replace('.gz', '')

        try:
            print(f"开始解压文件: {gz_file_path}")

            with gzip.open(gz_file_path, 'rb') as f_in:
                with open(extracted_file_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            print(f"解压完成: {extracted_file_path}")
            return True, str(extracted_file_path), "解压成功"

        except Exception as e:
            error_msg = f"解压失败: {str(e)}"
            print(error_msg)
            return False, None, error_msg