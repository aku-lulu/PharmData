# -*- coding: utf-8 -*-


import configparser
import os
from Utilities.Database.dbutils import DBconnection
from DataParse.WikipathwaysParse import WikipathwaysParse
from Utilities.ReadConfig import ConfigRoad


class WikipathwaysToMongo:
    """
    Wikipathway数据导入MongoDB数据库类
    """
    def __init__(self, cfgfile):
        self.config = configparser.ConfigParser()
        self.cfgfile = cfgfile
        self.config.read(cfgfile)
        self.name = 'wikipathway'
        self.db = DBconnection(self.cfgfile, self.config.get(self.name, 'db_name'),
                                self.config.get(self.name, 'col_name_1'))

    def insert_pathway(self, pathway):
        """
        插入单条数据
        :param pathway: 包含通路数据的字典
        :return: None
        """
        self.db.collection.insert_one(pathway)
    def insert_all(self, pathways):
        """
        批量插入多组数据
        :param pathways: 数据的生成器
        :return: None
        """
        for pathway in pathways:
            self.insert_pathway(pathway)
    def save_to_mongo(self):
        """
        执行方法，从数据文件到MongoDB的完整流程
        :return:None
        """
        parser = WikipathwaysParse(self.config, self.name)

        url = self.config.get(self.name, 'source_url_1') + self.config.get(self.name, 'file_name')
        infile = os.path.join(self.config.get(self.name, 'data_path_1'), url
                              .split('/')[-1])
        pathways = parser.read_and_index_pathways(infile)

        try:
            print('begin')
            self.insert_all(pathways)

        except StopIteration:
            print("No pathways found in the file.")

    def clear_wikipathways_data(self):
        """
        清空WikiPathways数据
        """
        config = configparser.ConfigParser()
        config.read(ConfigRoad)

        # 建立数据库连接
        db = DBconnection(ConfigRoad,
                          config.get('wikipathway', 'db_name'),
                          config.get('wikipathway', 'col_name_1'))

        # 删除所有数据
        result = db.collection.delete_many({})
        print(f"已删除 {result.deleted_count} 条记录")

        return result
