# WACS - Webpage Automatic Checking System
### An automatic checking, scoring system for web-page.

<br>

## Introduction
Latest-Version: Beta.V4

WACS is Teaching Assistant - Developement Project, for the course - INTRODUCTION OF NETWORK in Soochow University.

<br>

## Check Item
- Check if the page file is not existed or is empty or status-code: 404 --- 1 --- `static`
- Check if \<!DOCTYPE\> is HTML --- 2 --- `check_doc_type`
- Check if charset is UTF-8 --- 3 --- `check_charset`
- Check if lang is zh_TW --- 4 --- `check_lang`
- Check if title is empty --- 5 --- `check_title`
- Check if content is all in \<body- --- 7 --- `check_head`
- Check if page has horizontal scroll-bar --- 8 --- `check_scroll_bar`
- Check if the speed of page-loading is too slow --- 9 --- `check_page_speed`
- Check if the image is failed to display --- 10 --- `check_img_display`
- Check if file name of the page HTML file contains bad character --- 11 --- `check_file_path_name`
- Check if file name of the image contains bad character --- 12 --- `check_img_path_name`
- Check if file name of the folder contains bad character --- 13 --- `check_all_folder_name`  
- Check if a new window will open when accessing external-domain page --- 14 --- `check_new_window`
- Check if image is in the correct folder --- 15 --- `check_img_path_name`
- Check if css is in the correct folder --- 16 --- `check_css`
- Check if JavaScript is in the correct folder --- 17 --- `check_js`
- Check if image is deformed --- 18 --- `check_img_setting`
- Check if the setting of image is wrong --- 19 --- `check_img_setting`
- Check if the beging or ending of tag is wrong --- 20 --- `check_tags`
- Check if the usage of \<, \> - is wrong --- 21 --- `check_gls`
- Check if the blank space of attribute is wrong --- 22 --- `check_attr_space`
- Check if the usage of quotation of attribute is wrong --- 23 --- `check_attr_quote`
- Check if the usage of \<ul\> is wrong --- 24 --- `check_list_tag / self.check_ul`
- Check if the usage of \<ol\> is wrong --- 25 --- `check_list_tag / self.check_ol`
- Check if the usage of \<li\> is wrong --- 26 --- `check_list_tag / self.check_li` 


