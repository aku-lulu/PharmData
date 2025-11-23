import configparser
import pandas as pd
from tqdm import tqdm
import os
import time

from Utilities.ReadConfig import ConfigRoad


class EntrezParse:
    def __init__(self):
        # 列映射配置
        self.column_mapping = {
            0: 'tax_id',  # 物种分类ID
            1: 'GeneID',  # 基因唯一标识符
            2: 'Symbol',  # 默认基因符号
            3: 'LocusTag',  # 基因座标签
            4: 'Synonyms',  # 同义词（竖线分隔）
            5: 'dbXrefs',  # 其他数据库引用（竖线分隔）
            6: 'chromosome',  # 染色体
            7: 'map_location',  # 图谱位置
            8: 'description',  # 基因描述
            9: 'type_of_gene',  # 基因类型
            10: 'Symbol_from_nomenclature_authority',  # 命名权威机构符号
            11: 'Full_name_from_nomenclature_authority',  # 命名权威机构全名
            12: 'Nomenclature_status',  # 命名状态（O为官方，I为临时）
            13: 'Other_designations',  # 其他命名（竖线分隔）
            14: 'Modification_date',  # 修改日期（YYYYMMDD格式）
            15: 'Feature_type'  # 特征类型（竖线分隔）
        }

        self.config = configparser.ConfigParser()
        self.config.read(ConfigRoad)
        self.file_path = self.config.get('entrez', 'file_dir')
        self.chunk_size = 10000

    def parse_gene_info(self):
        """
        解析gene_info文件的所有列
        :return: 生成解析后的数据块
        """
        print(f"读取文件: {os.path.basename(self.file_path)}")
        print(f"文件大小: {os.path.getsize(self.file_path) / (1024 ** 3):.2f} GB")
        print(f"解析列数: {len(self.column_mapping)}")
        print(f"分块大小: {self.chunk_size} 行")

        # 获取总行数
        print("文件总行数")
        total_rows = self._count_total_rows(self.file_path)
        print(f"总数据行数: {total_rows:,}")
        print("开始解析数据")

        start_time = time.time()

        # 创建进度条解析数据
        with tqdm(total=total_rows, desc="解析进度", unit="行") as pbar:
            for chunk in pd.read_csv(
                    self.file_path,
                    sep='\t',
                    comment='#',  # 跳过以#开头的注释行
                    header=None,  # 没有列头
                    chunksize=self.chunk_size,
                    low_memory=False,
                    dtype=str,  # 所有列作为字符串
                    encoding='utf-8',
                    skiprows=1  # 跳过第一行（列头行）
            ):
                # 处理当前块
                processed_chunk = self._process_chunk(chunk)

                # 更新进度
                pbar.update(len(chunk))
                pbar.set_postfix({
                    '当前块大小': f"{len(chunk):,}",
                    '列数': f"{len(processed_chunk.columns)}"
                })

                yield processed_chunk

        processing_time = time.time() - start_time
        print(f"解析完成，总处理时间: {processing_time:.2f} 秒")

    def _count_total_rows(self, file_path):
        """
        计算文件总行数，跳过注释行和列头行
        :param file_path: 文件路径
        :return: 总行数
        """
        total_rows = 0
        header_skipped = False

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                if not header_skipped:
                    header_skipped = True
                    continue
                total_rows += 1
        return total_rows

    def _process_chunk(self, chunk):
        """
        处理数据块
        :param chunk: 原始数据块
        :return: 处理后的数据块
        """
        # 重命名列
        chunk = chunk.rename(columns=self.column_mapping)

        # 确保所有列都存在
        for col_name in self.column_mapping.values():
            if col_name not in chunk.columns:
                chunk[col_name] = None

        # 重新排列列顺序
        chunk = chunk[list(self.column_mapping.values())]

        # 数据清洗和标准化
        chunk = self._clean_and_standardize_data(chunk)

        return chunk

    def _clean_and_standardize_data(self, chunk):
        """
        数据清洗和标准化
        :param chunk: 数据块
        :return: 清洗后的数据块
        """
        # 确保所有列都是字符串类型并去除空白
        for col in chunk.columns:
            chunk[col] = chunk[col].fillna('').astype(str).str.strip()

        # 处理多值字段（竖线分隔）
        multi_value_columns = ['Synonyms', 'dbXrefs', 'Other_designations', 'Feature_type']
        for col in multi_value_columns:
            if col in chunk.columns:
                chunk[col] = chunk[col].apply(
                    lambda x: [] if x in ['', '-'] else [item.strip() for item in str(x).split('|') if item.strip()]
                )

        # 处理dbXrefs字段，解析为结构化数据
        if 'dbXrefs' in chunk.columns:
            chunk['dbXrefs_parsed'] = chunk['dbXrefs'].apply(self._parse_db_xrefs)

        # 处理空值表示
        empty_indicators = ['-', '']
        for col in chunk.columns:
            if col not in multi_value_columns:  # 多值字段已经处理过
                chunk[col] = chunk[col].apply(lambda x: None if x in empty_indicators else x)

        return chunk

    def _parse_db_xrefs(self, xrefs_list):
        """
        解析dbXrefs字段为结构化数据
        :param xrefs_list: 数据列表
        :return: 解析后的结构化数据列表
        """
        if not xrefs_list:
            return []

        parsed_xrefs = []
        for xref in xrefs_list:
            if ':' in xref:
                db, value = xref.split(':', 1)
                parsed_xrefs.append({
                    'database': db.strip(),
                    'value': value.strip()
                })
        return parsed_xrefs
