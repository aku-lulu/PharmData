from DataDownload.EntrezDownload import EntrezDownload
from DataParse.EntrezParse import EntrezParse
from DataToMongo.EntrezToMongo import EntrezToMongo
from DataUpdate.EntrezUpdate import EntrezUpdate

if __name__ == "__main__":
    updater = EntrezUpdate()
    update = updater.check_and_update()

    if update:
        # 创建下载器实例
        downloader = EntrezDownload()

        # 下载文件
        downloader.download_file()
        downloader.extract_file()

        # 解析
        parser = EntrezParse()
        for entry in parser.parse_gene_info():
            print(entry)

        # 上传数据库
        entrez_mongo = EntrezToMongo()
        entrez_mongo.clear_entrez_data()
        entrez_mongo.save_to_mongo()


