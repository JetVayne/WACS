# coding: utf-8
import datetime
import pymysql
import requests
import bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import markpage_beta_v4

# db info
connecttion = 'localhost'
user = 'root'
password = 'edward261'
db_name = 'class'

# 手動設定時間
set_time = '2019-10-21'

# target_date
target_date = ''
target_date_m = ''

# hw id
hw_id = ''


def connect_db() -> pymysql.connections.Connection:
    return pymysql.connect(connecttion, user, password, db_name)


def get_student_url(cursor: pymysql.cursors) -> list:
    result = []
    sql = 'SELECT * FROM class.student_website;'
    try:
        cursor.execute(sql)
        result = list(cursor.fetchall())
    except:
        print('[Info] - failed to fetch data from db.')
        return result

    return result


def set_target_date():
    global target_date, target_date_m
    now = datetime.datetime.now()
    year = str(now.year)
    month = ''
    if len(str(now.month)) == 1:
        month = '0' + str(now.month)
    else:
        month = str(now.month)
    day = ''
    if len(str(now.day)) == 1:
        day = '0' + str(now.day)
    else:
        day = str(now.day)

    target_date = year + month + day
    target_date_m = year + '-' + month + '-' + day

    # 人工設定時間
    if set_time != '':
        time_sl = set_time.split('-')
        temp_time_m = ''
        for s in time_sl:
            temp_time_m += s
        target_date = temp_time_m
        target_date_m = set_time


def set_hw_id(cursor: pymysql.cursors):
    global hw_id
    data = []
    sql = 'SELECT * FROM class.student_score_item;'
    try:
        cursor.execute(sql)
        data = list(cursor.fetchall())
    except:
        print('[Info] - failed to fetch data from db.')
        return

    for d in data:
        date_str = str(d[4])
        if target_date_m == date_str:
            hw_id = d[0]


def marking(stid: str, home_url):
    html_save_path = 'D:/homework/' + target_date[0:4] + '/' + stid + '/' + target_date + '/index.html'
    screen_save_path = 'D:/homework/' + target_date[0:4] + '/' + stid + '/' + target_date + '/screen.jpg'
    gsjs_save_path = 'D:/homework/' + target_date[0:4] + '/' + stid + '/' + target_date + '/google_speed_result.json'
    res = None
    try:
        res = requests.get(home_url)
    except Exception as e:
        print('[error A] - 學號:', stid, 'home:', home_url)
        print(e)
        error_info = '無法存取首頁'
        return parse_homepage_error_record(error_info, stid)

    if res.status_code != 200:
        print('[error B] - 學號:', stid, 'home:', home_url)
        error_info = 'failed to access homepage status: ' + str(res.status_code)
        return parse_homepage_error_record(error_info, stid)

    doc = BeautifulSoup(res.text, 'html.parser')
    css_q = 'a[href*="' + target_date + '"]'
    element = doc.select(css_q)
    if len(element) == 0:
        print('[error C] - 學號:', stid, 'home:', home_url)
        error_info = '無法獲得該次作業網址 - ' + target_date_m
        return parse_homepage_error_record(error_info, stid)

    # normal case
    path = element[0].get('href')

    target_url = urljoin(home_url, path)

    web_page = markpage_beta_v4.WebPape(target_url,
                                        html_save_path=html_save_path,
                                        screen_save_path=screen_save_path,
                                        gsjs_save_path=gsjs_save_path)

    web_page.mark()

    output = parse_record(stid, web_page)

    return output


def parse_homepage_error_record(error_info: str, stid: str) -> list:
    output = []
    # result
    result_record = dict()
    result_record['type'] = 'r'
    result_record['student_code'] = stid
    result_record['score_item_id'] = hw_id
    result_record['reduction_item_id'] = 1
    result_record['info'] = error_info
    result_record['times'] = 1
    output.append(result_record)

    # score
    score_record = dict()
    score_record['type'] = 's'
    score_record['student_code'] = stid
    score_record['score_item_id'] = hw_id
    score_record['reduction_score'] = -100
    score_record['screen_path'] = ''
    score_record['page_path'] = ''
    score_record['google_pagespeed_path'] = ''
    output.append(score_record)
    return output


def parse_record(stid: str, web_page: markpage_beta_v4.WebPape) -> list:
    ouput = []

    error_list = web_page.error_list

    # create result record
    for error in error_list:
        result_record = dict()
        result_record['type'] = 'r'
        result_record['student_code'] = stid
        result_record['score_item_id'] = hw_id
        result_record['reduction_item_id'] = error.get('code')
        result_record['info'] = error.get('info')
        result_record['times'] = error.get('times')
        ouput.append(result_record)

    # create score record
    score_record = dict()
    score_record['type'] = 's'
    score_record['student_code'] = stid
    score_record['score_item_id'] = hw_id
    score_record['reduction_score'] = web_page.reduc_score
    score_record['screen_path'] = web_page.ss_path
    score_record['page_path'] = web_page.hs_path
    score_record['google_pagespeed_path'] = web_page.gs_path
    ouput.append(score_record)

    if len(web_page.sys_log) != 0:
        print('學號: ', stid, 'hw_url: ', web_page.url)
        for sys_error in web_page.sys_log:
            print(sys_error[0])
            print(sys_error[1])
            print('------------------------------------------')
        print()

    return ouput


def insert_db(cursor: pymysql.cursors, record_list: list):
    for record in record_list:
        table = record.get('type')
        if table == 'r':
            insert_result_table(cursor, record)

        elif table == 's':
            insert_score_table(cursor, record)


def insert_result_table(cursor: pymysql.cursors, record: dict):
    sql = 'INSERT INTO `student_reduction_result` (`student_code`,`score_item_id`,`reduction_item_id`,`info`,`times`) ' \
          'VALUES (%(student_code)s, %(score_item_id)s, %(reduction_item_id)s, %(info)s, %(times)s)'
    cursor.execute(sql, record)


def insert_score_table(cursor: pymysql.cursors, record: dict):
    sql = 'INSERT INTO `student_score` (`student_code`,`score_item_id`,`reduction_score`,`screen_path`,`page_path`,`google_pagespeed_path`) ' \
          'VALUES (%(student_code)s, %(score_item_id)s, %(reduction_score)s, %(screen_path)s, %(page_path)s, %(google_pagespeed_path)s)'
    cursor.execute(sql, record)


def main():
    set_target_date()
    conn = connect_db()
    cursor = conn.cursor()
    set_hw_id(cursor)
    if hw_id == '':
        return

    home_page_list = get_student_url(cursor)
    if len(home_page_list) == 0:
        conn.close()
        return

    for url_data in home_page_list:
        stid = url_data[0]
        home_url = url_data[2]
        record_list = marking(stid, home_url)
        insert_db(cursor, record_list)
        conn.commit()
        # break

    # conn.commit()
    conn.close()


if __name__ == '__main__':
    a = datetime.datetime.now()
    main()
    b = datetime.datetime.now()
    print(b - a)
