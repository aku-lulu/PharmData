from bs4 import BeautifulSoup
import re

def extract_homo_sapiens_files_precise(html_content):
    """
    使用正则表达式匹配Homo_sapiens文件信息
    :param html_content: 包含文件下载目录的html页面内容
    :return: 包含文件信息的字典列表
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    file_info = []

    # 使用正则表达式匹配包含Homo_sapiens的zip文件名
    pattern = re.compile(r'.*Homo_sapiens.*\.zip', re.IGNORECASE)

    rows = soup.find_all('tr')

    for row in rows:
        # 查找匹配的文件链接
        zip_links = row.find_all('a', href=pattern)

        for link in zip_links:
            filename = link.text.strip()

            # 不区分大小写
            if re.search(r'homo_sapiens', filename, re.IGNORECASE):

                # 查找时间信息
                tds = row.find_all('td')
                for td in tds:
                    td_text = td.text.strip()
                    # 匹配日期格式
                    if re.search(r'\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\s+\d{1,2}:\d{2}\s+[AP]M', td_text):
                        file_info.append({
                            'file_name': filename,
                            'last_modified': td_text
                        })
                        break

    return file_info


