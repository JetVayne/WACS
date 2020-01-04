# coding: utf-8
import re
import time
import requests
import bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
import urllib.request
import json
from selenium import webdriver
from PIL import Image
from io import BytesIO
import os


class WebPape(object):
    def __init__(self, input_url, html_save_path=None, screen_save_path=None, gsjs_save_path=None):
        self.task_id = abs(hash(input_url)) % (10 ** 8)
        self.reduc_score = 0
        self.error_list = []
        self.sys_log = []
        self.url = input_url

        self.hs_path = 'D:/' + str(self.task_id) + '_index.html'
        if html_save_path:
            self.hs_path = html_save_path

        self.ss_path = 'D:/' + str(self.task_id) + '_screen.jpg'
        if screen_save_path:
            self.ss_path = screen_save_path

        self.gs_path = 'D:/' + str(self.task_id) + '_google_speed_result.json'
        if gsjs_save_path:
            self.gs_path = gsjs_save_path


    def mark(self):
        self.static()
        self.dynamic()

    def static(self):
        # print('[Info] - STATIC progress start.')
        res = None
        try:
            res = requests.get(self.url)
        except Exception as e:
            self.reduc_score += -100
            error_info = '無法讀取作業網頁。 url: ' + self.url + ' error: ' + str(e)
            self.error_list.append({'code': 1, 'info': error_info, 'times': 1})
            return

        res.encoding = 'utf-8'
        status = res.status_code
        if status != 200:
            self.reduc_score += -100
            error_info = '網站不存在，或路徑錯誤。 status: ' + str(status) + ' url: ' + self.url
            self.error_list.append({'code': 1, 'info': error_info, 'times': 1})
            return

        html = res.text

        # 獲取 document
        doc = None
        try:
            doc = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            self.reduc_score += -100
            error_info = '作業網頁無法解析。 url: ' + self.url + ' error: ' + str(e)
            self.error_list.append({'code': 1, 'info': error_info, 'times': 1})
            return

        # 儲存 html
        try:
            self.save_html(self.url)
        except Exception as e:
            se_list = ['[stage] - save_html 錯誤 ', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - HTML 存取完畢')

        # 查看是否為空白網頁:
        page_text_list = self.is_empty_page(doc)
        if page_text_list[0]:
            self.reduc_score += -100
            error_info = '網頁內容趨近空白 字數: ' + str(page_text_list[1])
            self.error_list.append({'code': 1, 'info': error_info, 'times': 1})
            return

        # 判斷 DOCTYPE
        try:
            self.check_doc_type(html)
        except Exception as e:
            se_list = ['[stage] - check_doc_type 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - DOCTYPE 檢查完畢')

        # 判斷 charset
        try:
            self.check_charset(doc)
        except Exception as e:
            se_list = ['[stage] - check_charset 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - charset 檢查完畢')

        # 判斷 lang
        try:
            self.check_lang(doc)
        except Exception as e:
            se_list = ['[stage] - check_lang 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - lang 檢查完畢')

        # 判斷 title
        try:
            self.check_title(doc)
        except Exception as e:
            se_list = ['[stage] - check_title 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - title 檢查完畢')

        # 判斷 head 標籤， 以及網頁內容是否在 body 以外的區域
        try:
            self.check_head(doc)
        except Exception as e:
            se_list = ['[stage] - check_head 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - head 檢查完畢')

        # 判斷圖片顯示
        try:
            self.check_img_display(doc)
        except Exception as e:
            se_list = ['[stage] - check_img_display 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - img_display 檢查完畢')

        # 判斷圖片路徑
        try:
            self.check_img_path_name(doc)
        except Exception as e:
            se_list = ['[stage] - check_img_path_name 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - img_path 檢查完畢')

        # 判斷網頁檔案命名
        try:
            self.check_file_path_name(self.url)
        except Exception as e:
            se_list = ['[stage] - check_file_path_name 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - file_path 檢查完畢')

        # 判斷所有上傳檔案的命名
        try:
            self.check_uploaded_src_name(doc)
        except Exception as e:
            se_list = ['[stage] - check_uploaded_src_name 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - all_src_name 檢查完畢')

        # 判斷連結外網連結，是否有新開視窗
        try:
            self.check_new_window(doc)
        except Exception as e:
            se_list = ['[stage] - check_new_window 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - new_window 檢查完畢')

        # 判斷 css
        try:
            self.check_css(doc)
        except Exception as e:
            se_list = ['[stage] - check_css 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - css 檢查完畢')

        # 判斷 js
        try:
            self.check_js(doc)
        except Exception as e:
            se_list = ['[stage] - check_js 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - js 檢查完畢')

        # 判斷 img 顯示比例
        try:
            self.check_img_setting(doc)
        except Exception as e:
            se_list = ['[stage] - check_img_setting 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - img_setting 檢查完畢')

        # 判斷 tag 符號
        try:
            self.check_tags(doc, html)
        except Exception as e:
            se_list = ['[stage] - check_tags 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - tag 檢查完畢')

        # 檢查 ul ol li 使用
        try:
            self.check_list_tag(doc)
        except Exception as e:
            se_list = ['[stage] - check_list_tag 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - ul ol li 檢查完畢')

        # 檢查 屬性 " "
        try:
            self.check_attr_quote(doc, html)
        except Exception as e:
            se_list = ['[stage] - check_attr_quote 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - attr " " 檢查完畢')

        # 檢查 屬性 空白隔開
        try:
            self.check_attr_space(doc, html)
        except Exception as e:
            se_list = ['[stage] - check_attr_space 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - attr space 檢查完畢')

        # 判斷 < >
        try:
            self.check_gls(doc, html)
        except Exception as e:
            se_list = ['[stage] - check_gls 錯誤', str(e)]
            self.sys_log.append(se_list)
        # print('[Info] - gls 檢查完畢')

    # ult - 1
    def is_empty_page(self, doc: bs4.BeautifulSoup):
        result = []
        text = doc.text.strip().replace(' ', '')
        text_num = len(text)
        if text_num < 150:
            result.append(True)
            result.append(text_num)
        else:
            result.append(False)
            result.append(text_num)

        return result

    def save_html(self, url: str):
        if not os.path.exists(os.path.dirname(self.hs_path)):
            try:
                os.makedirs(os.path.dirname(self.hs_path))
                urllib.request.urlretrieve(url, self.hs_path)
            except Exception as e:
                se_list = ['[Inner - save_html] 存取 html 失敗', 'url: ' + url + ' ' + str(e)]
                self.sys_log.append(se_list)
                raise
        else:
            urllib.request.urlretrieve(url, self.hs_path)

    def check_doc_type(self, html: str):
        if '<!DOCTYPE html>' not in html:
            self.reduc_score += -20
            error_info = '<!DOCTYPE> 標籤錯誤'
            self.error_list.append({'code': 2, 'info': error_info, 'times': 1})

    def check_charset(self, doc: bs4.BeautifulSoup):
        tag = doc.select('meta[charset]')
        if len(tag) == 0:
            self.reduc_score += -20
            error_info = 'charset 標籤未建立'
            self.error_list.append({'code': 3, 'info': error_info, 'times': 1})
            return

        charset = tag[0].get('charset')
        if charset not in ['utf-8', 'utf8', 'UTF8', 'UTF-8']:
            self.reduc_score += -20
            error_info = 'charset 標籤錯誤。 tag: ' + charset
            self.error_list.append({'code': 3, 'info': error_info, 'times': 1})

    def check_lang(self, doc: bs4.BeautifulSoup):
        tag = doc.select('html[lang]')
        if len(tag) == 0:
            self.reduc_score += -20
            error_info = 'lang 屬性未建立'
            self.error_list.append({'code': 4, 'info': error_info, 'times': 1})
            return

        lang = tag[0].get('lang')
        if lang not in ['zh-TW', 'zh-tw', 'ZH-TW']:
            self.reduc_score += -20
            error_info = 'lang 屬性錯誤。 tag: ' + lang
            self.error_list.append({'code': 4, 'info': error_info, 'times': 1})

    def check_title(self, doc: bs4.BeautifulSoup):
        tag = doc.select('head > title')
        if len(tag) == 0:
            self.reduc_score += -20
            error_info = 'title 標籤未建立'
            self.error_list.append({'code': 5, 'info': error_info, 'times': 1})
            return

        title = tag[0].text
        if len(title) == 0 or title is None:
            self.reduc_score += -20
            error_info = 'title 標籤錯誤'
            self.error_list.append({'code': 5, 'info': error_info, 'times': 1})

    def check_head(self, doc: bs4.BeautifulSoup):
        tag_list = doc.select('head')[0].children

        for tag in tag_list:
            if type(tag) is not bs4.element.Tag:
                continue

            if tag.name not in ['base', 'link', 'meta', 'script', 'style', 'title']:
                self.reduc_score += -20
                error_info = '網頁內容不在 <body></body> 區間內'
                self.error_list.append({'code': 7, 'info': error_info, 'times': 1})

    def check_img_display(self, doc: bs4.BeautifulSoup):
        img_list = doc.find_all('img')
        for img in img_list:
            path = img.get('src')
            abs_url = urljoin(self.url, path)
            res = None
            try:
                res = requests.get(abs_url)
            except Exception as e:
                self.reduc_score += -5
                error_info = '圖片完全無法讀取。 img_path: ' + path
                self.error_list.append({'code': 10, 'info': error_info, 'times': 1})

            status = res.status_code
            if status != 200 and status != 403:
                # print(abs_url)
                self.reduc_score += -5
                error_info = '圖片顯示狀態錯誤。 status: ' + str(status) + '  img_path: ' + path
                self.error_list.append({'code': 10, 'info': error_info, 'times': 1})

    def check_img_path_name(self, doc: bs4.BeautifulSoup):
        img_list = doc.find_all('img')

        for img in img_list:
            path = img.get('src')
            abs_url = urljoin(self.url, path)
            if self.is_external_domain(abs_url):
                continue
            else:
                check_list = path.split('/')
                # 是否在圖片資料夾
                if 'images' not in check_list and 'img' not in check_list and 'image' not in check_list:
                    self.reduc_score += -5
                    error_info = '圖片未放在圖片資料夾(images or img or image) 或是路徑設定錯誤。 tag: ' + path
                    self.error_list.append({'code': 15, 'info': error_info, 'times': 1})

                # 查看檔名
                for sub_path in check_list:
                    regex_check = re.findall(r'([\u4E00-\u9FFF]+|[A-Z]+|\s+)', sub_path)
                    if len(regex_check) != 0:
                        self.reduc_score += -5
                        error_info = '圖片檔名或是路徑含有中文/大寫/空白字元。 path_string: ' + sub_path
                        self.error_list.append({'code': 12, 'info': error_info, 'times': 1})

    def check_file_path_name(self, url: str):
        check_list = url.split('/')
        if len(check_list) == 0:
            return
        file_name = check_list[-1]
        regex_check = re.findall(r'([\u4E00-\u9FFF]+|[A-Z]+|\s+)', file_name)
        if len(regex_check) != 0:
            self.reduc_score += -5
            error_info = '網頁檔名或是含有中文/大寫/空白字元。 path_string: ' + file_name
            self.error_list.append({'code': 11, 'info': error_info, 'times': 1})

    def check_uploaded_src_name(self, doc: bs4.BeautifulSoup):
        elements = doc.select('[href]')
        for tag in elements:
            link = tag.get('href')
            if 'tel:' in link and '+' in link:
                continue
            if 'mailto:' in link and '@' in link:
                continue

            abs_url = urljoin(self.url, link)
            if not self.is_external_domain(abs_url):
                path_list = link.split('/')
                file = path_list.pop()
                file_check = re.findall(r'([\u4E00-\u9FFF]+|[A-Z]+|\s+)', file)
                if len(file_check) != 0:
                    self.reduc_score += -5
                    error_info = '上傳的檔案中，有的名稱含有 中文 or 大寫 or 空白字元。 file name: ' + file
                    self.error_list.append({'code': 13, 'info': error_info, 'times': 1})

                for folder in path_list:
                    folder_check = re.findall(r'([\u4E00-\u9FFF]+|[A-Z]+|\s+)', folder)
                    if len(folder_check) != 0:
                        self.reduc_score += -5
                        error_info = '上傳的資料夾中，有的名稱含有 中文 or 大寫 or 空白字元。 folder name: ' + folder
                        self.error_list.append({'code': 13, 'info': error_info, 'times': 1})

    def check_new_window(self, doc: bs4.BeautifulSoup):
        elements = doc.select('body [href]')

        for tag in elements:
            link = tag.get('href')
            if 'tel:' in link and '+' in link:
                continue
            if 'mailto:' in link and '@' in link:
                continue

            abs_url = urljoin(self.url, link)

            if self.is_external_domain(abs_url) and tag.get('target') != '_blank':
                self.reduc_score += -5
                error_info = '連結到外部連結沒有新開視窗。 tag: ' + str(tag)
                self.error_list.append({'code': 14, 'info': error_info, 'times': 1})

    # ult - 2
    def is_external_domain(self, url: str) -> bool:
        self_domain = urlparse(self.url).netloc
        check_domain = urlparse(url).netloc
        if check_domain != self_domain:
            return True
        else:
            return False

    def check_css(self, doc: bs4.BeautifulSoup):
        elements = doc.select('link[rel = "stylesheet"][type = "text/css"]')
        for tag in elements:
            path = tag.get('href')
            check_list = path.split('/')
            if 'css' not in check_list:
                self.reduc_score += -5
                error_info = 'css未放入css資料夾中。 path: ' + path
                self.error_list.append({'code': 16, 'info': error_info, 'times': 1})

    def check_js(self, doc: bs4.BeautifulSoup):
        elements = doc.select('script')
        for tag in elements:
            path = tag.get('src')
            if path is None:
                self.reduc_score += -5
                error_info = 'script 標籤內沒有設定 src  tag: ' + str(tag)
                self.error_list.append({'code': 17, 'info': error_info, 'times': 1})
                continue
            else:
                regex_check = re.findall(
                    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                    path)
                if regex_check != 0:
                    continue
                else:
                    check_list = path.split('/')
                    if 'js' not in check_list:
                        self.reduc_score += -5
                        error_info = 'javascript未寫在js資料夾中。 path: ' + path
                        self.error_list.append({'code': 17, 'info': error_info, 'times': 1})

    def check_img_setting(self, doc: bs4.BeautifulSoup):
        elements = doc.select('body img')

        for tag in elements:
            path = tag.get('src')
            abs_url = urljoin(self.url, path)
            height = tag.get('height')
            width = tag.get('width')

            if height is not None and re.match(r'[0-9]+%', str(width)):
                if re.match(r'[0-9]+\s*px', str(height)) and re.match(r'[0-9]+\s*px', str(width)):
                    h = int(height.replace('px', ''))
                    w = int(width.replace('px', ''))
                    hwp = round(h / w, 2)

                    raw_hwp = self.get_img_hwp(abs_url)

                    if hwp != raw_hwp:
                        self.reduc_score += -3
                        error_info = '圖片設定後的寬高比例與原圖比例不同。 tag: ' + str(tag)
                        self.error_list.append({'code': 18, 'info': error_info, 'times': 1})
                else:
                    self.reduc_score += -3
                    error_info = '圖片設定錯誤。 tag: ' + str(tag)
                    self.error_list.append({'code': 19, 'info': error_info, 'times': 1})

    def get_img_hwp(self, url: str):
        image = Image.open(urllib.request.urlopen(url))
        h = image.height
        w = image.width
        if h == 0 or w == 0:
            return 0
        return round(h / w, 2)

    def check_tags(self, doc: bs4.BeautifulSoup, html: str):
        self_closing = ['area', 'base', 'br', 'embed', 'hr', 'iframe', 'img',
                        'input', 'link', 'meta', 'param', 'source', 'track']
        tag_list = [tag.name for tag in doc.find_all()]
        tag_list = list(set(tag_list))

        temp_html = self.esc_content_gls(doc, html)

        for tag in tag_list:
            if tag in self_closing:
                continue
            pattern = r'<{1}' + tag + ' [^<,>]*>{1}'
            normal_start = '<' + tag + '>'
            normal_end = '</' + tag + '>'
            sp_case_list = re.findall(pattern, temp_html)
            start_count = len(sp_case_list) + temp_html.count(normal_start)
            end_count = temp_html.count(normal_end)

            if start_count != end_count:
                dev = abs(start_count - end_count)
                minus = 3 * dev
                info = ''
                if start_count > end_count:
                    info = normal_start + ' 多於 ' + normal_end
                else:
                    info = normal_end + ' 多於 ' + normal_start

                self.reduc_score += -minus
                error_info = 'tag 的開始與結束有錯誤。 ' + info + ' 相差數: ' + str(dev)
                self.error_list.append({'code': 20, 'info': error_info, 'times': dev})

    def check_list_tag(self, doc: bs4.BeautifulSoup):
        self.check_ul(doc)
        self.check_ol(doc)
        self.check_li(doc)

    def check_ul(self, doc):
        wrong_elements = []
        self.get_wrong_ul(doc, wrong_elements)
        for el in wrong_elements:
            self.reduc_score += -5
            error_info = 'ul使用錯誤  錯誤元素: ' + str(el).replace('\n', '') + '。 ' + \
                         '當前標籤: ' + el.name + '  父標籤: ' + el.parent.name
            self.error_list.append({'code': 24, 'info': error_info, 'times': 1})

    def get_wrong_ul(self, doc: bs4.BeautifulSoup, wrong_elements: list):
        ul_list = doc.select('ul')
        for ul in ul_list:
            child_list = ul.findChildren(recursive=False)
            for child in child_list:

                if child.name not in ['ul', 'li', 'br'] and child.parent.name != 'li':
                    wrong_elements.append(child)

                if child.name == 'ul':
                    self.get_wrong_ul(child, wrong_elements)

    def check_ol(self, doc):
        wrong_elements = []
        self.get_wrong_ol(doc, wrong_elements)
        for el in wrong_elements:
            self.reduc_score += -5
            error_info = 'ol使用錯誤  錯誤元素: ' + str(el).replace('\n', '') + '。 ' + \
                         '當前標籤: ' + el.name + '  父標籤: ' + el.parent.name
            self.error_list.append({'code': 25, 'info': error_info, 'times': 1})

    def get_wrong_ol(self, doc: bs4.BeautifulSoup, wrong_elements: list):
        ol_list = doc.select('ol')
        for ol in ol_list:
            child_list = ol.findChildren(recursive=False)
            for child in child_list:

                if child.name not in ['ol', 'li', 'br'] and child.parent.name != 'li':
                    wrong_elements.append(child)

                if child.name == 'ol':
                    self.get_wrong_ol(child, wrong_elements)

    def check_li(self, doc: bs4.BeautifulSoup):
        li_list = doc.select('li')
        for li in li_list:
            parent_tag = li.parent.name
            if parent_tag not in ['ul', 'ol']:
                self.reduc_score += -5
                error_info = 'li標籤單獨使用  錯誤元素: ' + str(li).replace('\n', '') + '。 父標籤: ' + parent_tag
                self.error_list.append({'code': 26, 'info': error_info, 'times': 1})

    def check_attr_quote(self, doc: bs4.BeautifulSoup, html: str):
        temp_html = self.esc_content_gls(doc, html)
        tag_list = [tag.name for tag in doc.find_all()]
        tag_list = list(set(tag_list))

        for tag in tag_list:
            pattern = r'<{1}' + tag + ' [^<,>]*>{1}'
            find_list = re.findall(pattern, temp_html)
            for check_tag in find_list:
                hp = r'href=\"([^"]*)\"'
                temp_tag = re.sub(hp, '', check_tag)
                srcp = r'src=\"([^"]*)\"'
                temp_tag = re.sub(srcp, '', temp_tag)

                attr_num = temp_tag.count('=')
                quot_num = temp_tag.count('"') + temp_tag.count('\'')
                if quot_num != attr_num * 2:
                    self.reduc_score += -3
                    error_info = '屬性的 " " 符號沒有正確使用。 錯誤元素: ' + check_tag
                    self.error_list.append({'code': 23, 'info': error_info, 'times': 1})

    def check_attr_space(self, doc: bs4.BeautifulSoup, html: str):
        tag_list = [tag.name for tag in doc.find_all()]
        tag_list = list(set(tag_list))
        hp = r'href=\"([^"]*)\"'
        srcp = r'src=\"([^"]*)\"'

        for tag in tag_list:
            pattern = r'<{1}' + tag + ' [^<,>]*>{1}'
            find_list = re.findall(pattern, html)
            for check_tag in find_list:
                temp_tag = check_tag
                if bool(re.findall(hp, temp_tag)):
                    replace_p = r' href=\"([^"]*)\"'
                    temp_tag = re.sub(replace_p, '', temp_tag)

                if bool(re.findall(srcp, temp_tag)):
                    replace_p = r' src=\"([^"]*)\"'
                    temp_tag = re.sub(replace_p, '', temp_tag)

                req_p = r'\"([^"]*)\"'
                re_list = re.findall(req_p, temp_tag)
                for re_str in re_list:
                    re_str = re_str.replace('"', '')
                    temp_tag = temp_tag.replace(re_str, '')

                class_num = temp_tag.count('=')
                space_num = temp_tag.count(' ')

                if space_num < class_num:
                    self.reduc_score += -3
                    error_info = '元素屬性之間沒有用空白隔開 tag: ' + check_tag
                    self.error_list.append({'code': 22, 'info': error_info, 'times': 1})

    def esc_content_gls(self, doc: bs4.BeautifulSoup, html: str):
        result = html
        remove_list = doc.find_all(text=re.compile("(<|>)"))
        for replace_str in remove_list:
            result = result.replace(replace_str, '')

        return result

    def check_gls(self, doc: bs4.BeautifulSoup, html: str):
        temp_html = self.esc_content_gls(doc, html)
        ls_count = temp_html.count('<')
        gs_count = temp_html.count('>')

        if ls_count != gs_count:
            dev = abs(ls_count - gs_count)
            minus = 3 * dev
            self.reduc_score += -minus
            error_info = '<、> 符號數量錯誤。 相差: ' + str(dev)
            self.error_list.append({'code': 21, 'info': error_info, 'times': dev})

    def dynamic(self):
        # 判斷 page 速度
        try:
            self.check_page_speed(self.url)
        except:
            self.sys_log.append('[stage] - check_page_speed 錯誤')
        # print('[Info] - page_speed 檢查完畢')

        # 判斷 scroll_bar
        self.view_page(self.url)

    def check_page_speed(self, url: str):
        api_domain = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url='
        api_key = 'AIzaSyCX6I9oT1-dt46NpLF4Hk2S-TVRrxvCFTs'
        test_url = api_domain + url + '&key=' + api_key

        res = None
        try:
            res = requests.get(test_url)
        except Exception as e:
            se_list = ['[Inner - check_page_speed] 存取 google speed test 失敗', 'url: ' + url + ' ' + str(e)]
            self.sys_log.append(se_list)
            return

        res.encoding = 'utf-8'
        html = res.text
        speed_json = json.loads(html)
        self.save_gs_js(speed_json)
        speed_score = speed_json.get('lighthouseResult').get('audits').get('speed-index').get('score')
        speed_score = speed_score * 100
        if speed_score < 80:
            self.reduc_score += -10
            error_info = 'google api tested speed too slow. score:' + str(speed_score)
            self.error_list.append({'code': 9, 'info': error_info, 'times': 1})

    def save_gs_js(self, json_data: dict):
        if not os.path.exists(os.path.dirname(self.gs_path)):
            try:
                os.makedirs(os.path.dirname(self.gs_path))
                with open(self.gs_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)

            except Exception as e:
                se_list = ['[Inner - save_html] failed to write google speed json to local. ', str(e)]
                self.sys_log.append(se_list)
                raise
        else:
            with open(self.gs_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

    def view_page(self, url: str):
        dr = None
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--test-type")
            dr = webdriver.Chrome(options=options)
            dr.get(url)
        except Exception as e:
            se_list = ['[Inner - view_page] 使用 selenium 開啟網頁失敗', str(e)]
            self.sys_log.append(se_list)
            dr.close()
            return

        # 檢查 scroll bar
        try:
            self.check_scroll_bar(dr)
        except Exception as e:
            se_list = ['[stage] - check_scroll_bar 錯誤', str(e)]
            self.sys_log.append(se_list)

        # 儲存 screen shot
        try:
            self.save_screen_shot(dr)
        except Exception as e:
            se_list = ['[stage] - save_screen_shot 錯誤', str(e)]
            self.sys_log.append(se_list)

        dr.close()

    def check_scroll_bar(self, driver: webdriver):
        width = driver.execute_script("return document.body.scrollWidth")
        if width > 1280:
            self.reduc_score += -10
            error_info = '網頁出現橫向卷軸。 網頁寬度: ' + str(width)
            self.error_list.append({'code': 8, 'info': error_info, 'times': 1})

    def save_screen_shot(self, driver, scroll_delay=0.3):
        device_pixel_ratio = driver.execute_script('return window.devicePixelRatio')
        total_height = driver.execute_script('return document.body.parentNode.scrollHeight')
        viewport_height = driver.execute_script('return window.innerHeight')
        total_width = driver.execute_script('return document.body.offsetWidth')
        viewport_width = driver.execute_script("return document.body.clientWidth")

        try:
            assert (viewport_width == total_width)
        except AssertionError as e:
            se_list = ['[Inner - save_screen_shot] assert error', str(e)]
            self.sys_log.append(se_list)

        # scroll the page, take screenshots and save screenshots to slices
        offset = 0
        slices = {}
        while offset < total_height:
            if offset + viewport_height > total_height:
                offset = total_height - viewport_height

            driver.execute_script('window.scrollTo({0}, {1})'.format(0, offset))
            time.sleep(scroll_delay)

            img = Image.open(BytesIO(driver.get_screenshot_as_png()))
            slices[offset] = img

            offset = offset + viewport_height

        # combine image slices
        stitched_image = Image.new('RGB', (total_width * device_pixel_ratio, total_height * device_pixel_ratio))
        for offset, image in slices.items():
            stitched_image.paste(image, (0, offset * device_pixel_ratio))

        if not os.path.exists(os.path.dirname(self.ss_path)):
            try:
                os.makedirs(os.path.dirname(self.ss_path))
                stitched_image.save(self.ss_path)
            except Exception as e:
                se_list = ['[Inner - save_screen_shot] failed to write screen shot img to local. ', str(e)]
                self.sys_log.append(se_list)
        else:
            stitched_image.save(self.ss_path)
