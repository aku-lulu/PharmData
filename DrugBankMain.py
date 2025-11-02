from DataDownload.DrugBankDownload import DrugbankDownload
from DataParse.DrugBankParse import DrugBankParse
from Utilities.DrugBankTools import extract_zip_file
from DataToMongo.DrugBankToMongo import DrugBanktoMongo
from DataUpdate.DrugBankUpdate import DrugBankUpdate

if __name__ == "__main__":
    # 检查更新
    drugbank_updater = DrugBankUpdate()
    need_update = drugbank_updater.auto_update_check()
    print(f"\n {need_update}")

    if need_update:
        # 下载
        downloader = DrugbankDownload()
        downloader.start_download()

        # 解压
        extract_zip_file()

        # 解析
        parser = DrugBankParse()
        for entry in parser:
            print(entry)
            break

        # 上传数据库
        drugbanktomongo = DrugBanktoMongo()
        drugbanktomongo.clear_drugbank_data()
        drugbanktomongo.save_to_mongo()

