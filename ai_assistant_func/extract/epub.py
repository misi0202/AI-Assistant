from ebooklib import epub
from bs4 import BeautifulSoup
import ebooklib

# 提取章节的 href 和 title
def extract_chapter_links(epub_file):
    book = epub.read_epub(epub_file)
    toc = book.toc  # 获取TOC（Table of Contents）
    
    chapter_list = []

    # 通用的递归解析TOC目录项
    def parse_toc(toc_items):
        for item in toc_items:
            if isinstance(item, epub.Link):  # 如果是章节链接
                href = item.href
                title = item.title
                chapter_list.append((href, title))  # 保存章节的href和title
            elif isinstance(item, tuple):  # 如果是元组 (epub.Link, [sub_items])
                link, sub_items = item
                if isinstance(link, epub.Link):
                    href = link.href
                    title = link.title
                    chapter_list.append((href, title))  # 保存父章节的href和title
                # 递归处理子章节
                parse_toc(sub_items)
            elif isinstance(item, list):  # 如果是嵌套的子章节列表
                chapter_list.append(parse_toc(item))

    parse_toc(toc)
    
    return chapter_list
# 根据章节标题获取内容
def get_chapters_from_toc(chapter_list, book):
    chapters = []
    
    for chapter_href, chapter_title in chapter_list:

        # 查找与该章节对应的内容
        html, page_num = chapter_href.split('#')[0], chapter_href.split('#')[1]
        print(html, page_num)
        # for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        #     if doc.file_name in chapter_href:
        #         soup = BeautifulSoup(doc.get_body_content(), 'html.parser')
        #         text = soup.get_text()  # 提取纯文本内容
        #         chapters.append((chapter_title, text))  # 保存章节标题和内容
        #         break


    return chapters

# 获取 EPUB 文件中的所有部分
def get_epub_parts(epub_file):
    book = epub.read_epub(epub_file)
    
    parts = []
    
    # 遍历 EPUB 中的每个部分
    for item in book.get_items():
        part_info = {
            "file_name": item.file_name,      # 获取文件名
            "media_type": item.media_type     # 获取MIME类型
        }
        
        # 如果是文档类型，获取内容
        if item.media_type == 'application/xhtml+xml':
            content = item.get_body_content().decode('utf-8')  # 获取章节内容
            part_info["content"] = content 
        
            parts.append(part_info)
    
    return parts

# 使用示例
epub_file_path = 'E:\py_code\course_assistant\data\epub\Hands-On Machine Learning with Scikit-Learn and TensorFlow_ Concepts, Tools, and Techniques to Build Intelligent Systems ( PDFDrive ).epub'
chapters_list = extract_chapter_links(epub_file_path)
chapters = get_chapters_from_toc(chapters_list, epub.read_epub(epub_file_path))

htmls = get_epub_parts(epub_file_path)

soup = BeautifulSoup(htmls[0]['content'], 'lxml')
element = soup.find(id='p4')

# 输出内容
if element:
    print(element.text)
else:
    print("没有找到对应的片段")

# 打印每个章节的标题和内容
# for chapter_title, text in chapters:
    # print(f"Chapter: {chapter_title}")
    # # print(text[:500])  # 打印章节前500个字符
    # print("\n\n")
