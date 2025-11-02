import configparser
import os
import zipfile

from Utilities.ReadConfig import ConfigRoad


def extract_zip_file():
    config = configparser.ConfigParser()
    config.read(ConfigRoad)
    file_path = config.get('drugbank', 'file_path')
    infile = config.get('drugbank', 'data_path_1')
    # 检查zip文件是否存在
    if not os.path.exists(infile):
        raise FileNotFoundError(f"ZIP文件不存在: {infile}")

    # 创建解压目录（如果不存在）
    os.makedirs(file_path, exist_ok=True)

    # 打开zip文件
    with zipfile.ZipFile(infile, 'r') as zip_ref:
        # 获取zip内文件列表
        file_list = zip_ref.namelist()

        # 获取zip内唯一的文件名
        original_filename = file_list[0]
        output_filename = original_filename

        # 完整的输出路径
        output_path = os.path.join(file_path, output_filename)

        # 解压文件
        zip_ref.extract(original_filename, file_path)

    return output_path
