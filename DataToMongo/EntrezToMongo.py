import configparser

from DataParse.EntrezParse import EntrezParse
from Utilities.Database.dbutils import DBconnection
from Utilities.ReadConfig import ConfigRoad



class EntrezToMongo:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(ConfigRoad)

        # MongoDB连接配置
        self.confile = ConfigRoad
        self.config = configparser.ConfigParser()
        self.config.read(self.confile)
        self.db_connection = DBconnection(
            self.confile,
            self.config.get('entrez', 'db_name'),
            self.config.get('entrez', 'col_name_1')
        )

        # 初始化解析器
        self.entrez_parser = EntrezParse()

        # 批量插入大小
        self.batch_size = 1000

    def _process_chunk_for_mongodb(self, chunk):
        """
        处理数据块
        :param chunk: 数据块
        :return: 处理后的文档列表
        """
        documents = []

        for _, row in chunk.iterrows():
            # 使用EntrezParse已经处理好的数据
            document = {
                # 基本信息
                'tax_id': row.get('tax_id'),
                'GeneID': row.get('GeneID'),
                'Symbol': row.get('Symbol'),
                'LocusTag': row.get('LocusTag'),

                # 多值字段（EntrezParse已处理为列表）
                'Synonyms': row.get('Synonyms', []),
                'dbXrefs': row.get('dbXrefs', []),
                'Other_designations': row.get('Other_designations', []),
                'Feature_type': row.get('Feature_type', []),

                # 基因组信息
                'chromosome': row.get('chromosome'),
                'map_location': row.get('map_location'),

                # 描述信息
                'description': row.get('description'),
                'type_of_gene': row.get('type_of_gene'),

                # 权威命名信息
                'nomenclature': {
                    'symbol': row.get('Symbol_from_nomenclature_authority'),
                    'full_name': row.get('Full_name_from_nomenclature_authority'),
                    'status': row.get('Nomenclature_status')
                },

                # 元数据
                'Modification_date': row.get('Modification_date'),

                # 结构化数据
                'dbXrefs_parsed': row.get('dbXrefs_parsed', [])
            }

            # 清理空值
            document = self._clean_document(document)

            # 设置文档ID为GeneID
            if document.get('GeneID'):
                document['_id'] = document['GeneID']

            documents.append(document)

        return documents

    def _clean_document(self, document):
        """
        清除数据中的空值
        :param document: 原始文档
        :return: 处理后的文档
        """
        # 处理None值
        for key, value in document.items():
            if value is None:
                document[key] = None
            elif isinstance(value, str) and value == '':
                document[key] = None
            elif isinstance(value, dict):
                # 递归清理嵌套字典
                document[key] = self._clean_document(value)
            elif isinstance(value, list) and not value:
                # 空列表保持不变
                pass

        # 特殊处理nomenclature字段
        if document.get('nomenclature'):
            nomenclature = document['nomenclature']
            if all(v is None for v in nomenclature.values()):
                document['nomenclature'] = None

        return document


    def save_to_mongo(self):
        """
        解析数据并保存到MongoDB
        """
        print("开始解析并保存数据到MongoDB...")

        total_inserted = 0
        total_processed = 0
        chunk_count = 0

        try:
            # 调用EntrezParse类的解析方法
            for chunk in self.entrez_parser.parse_gene_info():
                chunk_count += 1

                # 处理当前块用于MongoDB
                documents = self._process_chunk_for_mongodb(chunk)

                # 批量插入
                for i in range(0, len(documents), self.batch_size):
                    batch = documents[i:i + self.batch_size]

                    try:
                        result = self.db_connection.collection.insert_many(batch, ordered=False)
                        inserted_count = len(result.inserted_ids)
                        total_inserted += inserted_count

                    except Exception as e:
                        # 如果批量插入失败，尝试单条插入
                        print(f"批量插入失败，单条插入: {e}")
                        inserted_count = self._insert_one_by_one(batch)
                        total_inserted += inserted_count

                total_processed += len(chunk)

                print(
                    f"数据块 {chunk_count}: 处理 {len(chunk)} 条, "
                    f"累计插入 {total_inserted}/{total_processed} 条记录"
                )

            print(f"解析完成，成功插入 {total_inserted} 条记录到MongoDB")

        except Exception as e:
            print(f"保存数据时发生错误: {e}")
            raise

    def _insert_one_by_one(self, documents):
        """
        将单条数据插入到文档中
        :param documents: 文档列表
        :return: 成功的数据条目
        """
        success_count = 0

        for doc in documents:
            try:
                self.db_connection.collection.insert_one(doc)
                success_count += 1
            except Exception as e:
                print(f"插入单条记录失败 (GeneID: {doc.get('GeneID', 'Unknown')}): {e}")

        return success_count


    def clear_entrez_data(self):
        """
        清空数据
        """
        try:
            result = self.db_connection.collection.delete_many({})
            print(f"已删除 {result.deleted_count} 条记录")
            return result
        except Exception as e:
            print(f"清空数据失败: {e}")
            raise
