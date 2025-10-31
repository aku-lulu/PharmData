import configparser
import requests

from DataDownload.WikipathwaysDownload import Wikipathway_Download
from DataToMongo.WikipathwaysToMongo import WikipathwaysToMongo
from Utilities.WikipathwayZipName_LatestTime import extract_homo_sapiens_files_precise
from DataUpdate.WikipathwaysUpdate import WikipathwaysUpdate
from Utilities.ReadConfig import ConfigRoad


if __name__ == '__main__':
    cfgfile = ConfigRoad

    # 检查更新
    checker = WikipathwaysUpdate()
    update_result = checker.check_wikipathway_update()

    print("检查结果:")
    print(f"是否需要更新: {update_result['needs_update']}")

    if update_result['needs_update']:
        # 提取网页中的文件名和更新时间
        config = configparser.ConfigParser()
        config.read(cfgfile, encoding="utf-8")
        url = config.get('wikipathway', 'directory_url')
        try:
            response = requests.get(url, timeout=10)
            files = extract_homo_sapiens_files_precise(response.text)
            for file in files:
                config.set('wikipathway', 'last_modified', file['last_modified'])
                config.set('wikipathway', 'file_name', file['file_name'])
                with open(cfgfile, 'w', encoding="utf-8") as configfile:
                    config.write(configfile)
        except Exception as e:
            print(f"匹配失败: {e}")

        # 下载数据
        wikipathwaydownload = Wikipathway_Download()
        wikipathwaydownload.start()

        # 解析数据并存入数据库
        wikipathwaytomongo = WikipathwaysToMongo(cfgfile)

        # 删除数据库中原始数据
        wikipathwaytomongo.clear_wikipathways_data()

        wikipathwaytomongo.save_to_mongo()




