import requests
from bs4 import BeautifulSoup
import re
import configparser
import os

from Utilities.ReadConfig import ConfigRoad

def extract_biogrid_version_name():
    config = configparser.ConfigParser()
    config.read(ConfigRoad, encoding="utf-8")
    url = config.get('biogrid', 'directory_url')

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        text_content = soup.get_text()

        version_pattern = r'BIOGRID-\d+\.\d+\.\d+'
        matches = re.findall(version_pattern, text_content)

        if matches:
            unique_matches = list(set(matches))

            latest_version = select_latest_version(unique_matches)

            if latest_version:
                if save_filename_to_config(latest_version, ConfigRoad):
                    return latest_version
        else:
            print("未找到BIOGRID版本名称")

        return extract_from_links(soup, ConfigRoad)

    except Exception as e:
        print(f"提取biogrid版本名称失败: {e}")
        return None


def extract_from_links(soup, config_file):
    all_links = soup.find_all('a', href=True)
    version_files = []

    for link in all_links:
        href = link.get('href', '')
        text = link.get_text().strip()

        sources = [href, text]

        for source in sources:
            version_pattern = r'BIOGRID-\d+\.\d+\.\d+'
            matches = re.findall(version_pattern, source)

            for match in matches:
                if match not in version_files:
                    version_files.append(match)

    if version_files:
        latest_version = select_latest_version(version_files)
        if latest_version:
            if save_filename_to_config(latest_version, config_file):
                return latest_version

    return None


def select_latest_version(versions):
    if not versions:
        return None

    def version_key(version_str):
        match = re.search(r'BIOGRID-(\d+)\.(\d+)\.(\d+)', version_str)
        if match:
            return tuple(map(int, match.groups()))
        return (0, 0, 0)

    try:
        sorted_versions = sorted(versions, key=version_key, reverse=True)
        latest = sorted_versions[0]
        return latest
    except Exception as e:
        print(f"版本排序失败: {e}")
        return versions[0]


def save_filename_to_config(filename, config_file):
    try:
        config = configparser.ConfigParser()

        if os.path.exists(config_file):
            config.read(config_file, encoding="utf-8")

        if not config.has_section('biogrid'):
            config.add_section('biogrid')

        config.set('biogrid', 'file_name', filename)

        with open(config_file, 'w', encoding="utf-8") as configfile:
            config.write(configfile)

        return True

    except Exception as e:
        print(f"保存文件名到配置文件失败: {e}")
        return False


def generate_and_save_biogrid_zipname():
    config = configparser.ConfigParser()
    config.read(ConfigRoad, encoding="utf-8")
    version_name = config.get('biogrid', 'file_name')

    try:
        # 验证版本号格式
        if not re.match(r'^BIOGRID-\d+\.\d+\.\d+$', version_name):
            print(f"版本号格式不正确: {version_name}")
            return None

        zip_filename = version_name.replace('BIOGRID-', 'BIOGRID-ALL-') + '.mitab.zip'

        if save_zipname_to_config(zip_filename, ConfigRoad):
            return zip_filename
        else:
            return None

    except Exception as e:
        print(f"生成文件名失败: {e}")
        return None


def save_zipname_to_config(zip_filename, config_file):
    try:
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        if not config.has_section('biogrid'):
            config.add_section('biogrid')

        config.set('biogrid', 'zip_name', zip_filename)

        with open(config_file, 'w', encoding='utf-8') as configfile:
            config.write(configfile)

        return True

    except Exception as e:
        print(f"保存失败: {e}")
        return False


def build_and_save_biogrid_download_url():
    try:
        if not os.path.exists(ConfigRoad):
            return None

        config = configparser.ConfigParser()
        config.read(ConfigRoad, encoding='utf-8')

        required_options = ['file_name', 'zip_name']
        missing_options = []

        for option in required_options:
            if not config.has_option('biogrid', option):
                missing_options.append(option)

        if missing_options:
            return None

        file_name = config.get('biogrid', 'file_name')
        zip_name = config.get('biogrid', 'zip_name')

        base_url = "https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive"

        download_url = f"{base_url}/{file_name}/{zip_name}"

        if not config.has_section('biogrid'):
            config.add_section('biogrid')

        config.set('biogrid', 'source_url_1', download_url)

        with open(ConfigRoad, 'w', encoding='utf-8') as configfile:
            config.write(configfile)

        return download_url

    except Exception as e:
        print(f"失败: {e}")
        return None