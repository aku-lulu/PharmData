import configparser

from DataDownload.BiogridDownload import BiogridDownload
from DataParse.BiogridParse import BiogridParse
from Utilities.BiogridVersion_LatesTime import extract_biogrid_version_name, generate_and_save_biogrid_zipname, build_and_save_biogrid_download_url
from DataToMongo.BiogridToMongo import BiogridToMongo
from DataUpdate.BiogridUpdate import BiogridUpdate
from Utilities.ReadConfig import ConfigRoad

if __name__ == "__main__":
    config_path = ConfigRoad
    config = configparser.ConfigParser()
    config.read(ConfigRoad)
    source_url = config.get('biogrid', 'directory_url')

    checker = BiogridUpdate()
    result = checker.check_biogrid_version_update(source_url)
    print(result['message'])
    if not result['is_same']:
        # 提取最新的版本号、名称和下载地址，存到配置文件当中
        extract_biogrid_version_name()
        generate_and_save_biogrid_zipname()
        build_and_save_biogrid_download_url()

        # 下载数据
        biogrid = BiogridDownload()
        biogrid.start()

        # 解析数据
        parser = BiogridParse()
        for record in parser.run():
            print(record)

        biogrid_to_mongo = BiogridToMongo()

        biogrid_to_mongo.clear_biogrid_data()
        biogrid_to_mongo.to_mongo()

