import configparser
from DataParse.BiogridParse import BiogridParse
from Utilities.Database.dbutils import DBconnection
from Utilities.ReadConfig import ConfigRoad


class BiogridToMongo:
    def __init__(self):
        self.confile = ConfigRoad
        self.config = configparser.ConfigParser()
        self.config.read(self.confile)
        self.db_connection = DBconnection(
            self.confile,
            self.config.get('biogrid', 'db_name'),
            self.config.get('biogrid', 'col_name_1')
        )
        self.biogrid_parser = BiogridParse(self.confile)
        self.data_path = self.config.get('biogrid', 'data_path_1')

    def to_mongo(self):
        self.biogrid_parser.to_csv(self.data_path)
        dict_data_generator = self.biogrid_parser.parse(self.data_path)

        # 获取第一个条目并插入到 MongoDB
        for entry in dict_data_generator:
            self.db_connection.collection.insert_one(entry)

    def close(self):
        # 关闭 MongoClient
        self.db_connection.collection.database.client.close()
        print("Database connection closed.")

    def clear_biogrid_data(self):
        config = configparser.ConfigParser()
        config.read(ConfigRoad)

        # 建立数据库连接
        db = DBconnection(ConfigRoad,
                          config.get('biogrid', 'db_name'),
                          config.get('biogrid', 'col_name_1'))

        # 删除所有数据
        result = db.collection.delete_many({})
        print(f"已删除 {result.deleted_count} 条记录")

        return result





