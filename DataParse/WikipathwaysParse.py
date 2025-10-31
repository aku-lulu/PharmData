# -*- coding: utf-8 -*-
# @Time    : 2022/10/30 21:06
# @Author  : SunZehua
# @Email   : sunzh857@nenu.edu.cn
# @File    : Wikipathway_Parser.py
# @Software: PyCharm

import gzip
import os
import re
from xml.etree.ElementTree import fromstring
from zipfile import ZipFile
from xmljson import yahoo


def _strip_namespace(xml):
    """
    移除xml字符串中的命名空间函数
    :param xml: 包含命名空间的原始xml字符串
    :return:移除命名空间后的xml字符串
    """
    return re.sub(' xmlns="[^"]+"', '', xml, count=1)


class WikipathwaysParse:
    """
    Wikipathway数据解析类
    """
    def __init__(self, config, section_name):
        self.config = config
        self.section_name = section_name

    def read_and_index_pathways(self, infile):
        """
        读取数据类型函数
        :param infile: 文件路径
        :return: 处理后的数据
        """
        if os.path.isdir(infile):
            for child in os.listdir(infile):
                c = os.path.join(infile, child)
                if child.endswith(".zip"):
                    yield from self.read_and_index_wikipathways_zipfile(c)
                else:
                    yield from self.read_and_index_wikipathways_file(c)
        elif infile.endswith(".zip"):
            yield from self.read_and_index_wikipathways_zipfile(infile)
        else:
            yield from self.read_and_index_wikipathways_file(infile)

    def read_and_index_wikipathways_zipfile(self, zipfile):
        """
        从zip文件中读取并解析Wikipathway数据
        :param zipfile: zip文件路径
        :return: 从文件中解析出的数据
        """
        with ZipFile(zipfile) as myzip:
            for fname in myzip.namelist():
                with myzip.open(fname) as jfile:
                    xml = jfile.read()
                    if not isinstance(xml, str):
                        xml = xml.decode('utf-8')
                    yield from self.read_and_index_wikipathways_xml(xml)

    def read_and_index_wikipathways_file(self, infile):
        """
        从单个文件中读取Wikipathway数据
        :param infile: 文件路径
        :return: 从文件中解析出的数据
        """
        if infile.endswith(".gz"):
            with gzip.open(infile, 'rt') as f:
                xmls = f.read()
        else:
            with open(infile, 'r') as f:
                xmls = f.read()
        yield from self.read_and_index_wikipathways_xml(xmls)

    def read_and_index_wikipathways_xml(self, xml):
        """
        解析xml字符串
        :param xml: 包含Wikipathway数据的xml字符串
        :return: 处理后的单个通路字典
        """
        xml = _strip_namespace(xml)
        pathway = yahoo.data(fromstring(xml))["Pathway"]
        for a in ["Biopax", "BiopaxRef", "Graphics", "Shape", "Group", "InfoBox"]:
            if a in pathway:
                del pathway[a]
        for a in ["Interaction", "DataNode", "Label"]:
            if a in pathway:
                for i in pathway[a]:
                    if isinstance(i, str):
                        continue
                    if "Graphics" in i:
                        del i["Graphics"]
                    if "GraphId" in i:
                        del i["GraphId"]
        yield pathway
