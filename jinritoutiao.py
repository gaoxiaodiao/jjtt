#!/usr/bin/python
#coding=utf-8
"""
*文件说明:tmp.py
*作者:高小调
*创建时间:2017年08月22日 星期二 23时56分17秒
*开发环境:Kali Linux/Python v2.7.13
"""
import requests
import time
from os import path
from wordcloud import WordCloud
from bs4 import BeautifulSoup
import jieba
import jieba.analyse
import re
import sys
def get_wordcloud(text):
    tags = jieba.analyse.extract_tags(text,topK=50)
    for tag in tags:
        print(tag.encode('utf-8'))

#根据用户uid获取其发布所有文章信息
def get_hot_article_info(uid,hot_count):
    r = requests.get("http://www.toutiao.com")
    webid = r.cookies['tt_webid']
    print(webid)
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    cookies = dict(tt_webid=webid)
    time = "0";
    index = 1
    while(True):
        url = "https://www.toutiao.com/c/user/article/?page_type=1&user_id="+str(uid)+"&max_behot_time="+str(time)+"&count=100"
        r = requests.get(url,headers=headers,cookies=cookies)
        if r.status_code != 200:
            break
        infos = r.json()
        if infos is None:
            break
        new_info = {}
        ret = []
        for info in infos['data']:
            title = info['title']
            count = info['go_detail_count']
            item_id = info['item_id']
            time = info['behot_time']
            if count >= hot_count :
                ret.append({'id':item_id,'title':title,'count':count})
                print("%d-%s-%s-%s-%s"%(index,item_id,title,count,info['detail_play_effective_count']))
                index = index+1
    return ret

#根据关键字查找用户名及用户id
def search_user_from_keyword(keyword):
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Cookie':'tt_webid=6457127978488366605;'}
    offset = 0
    index = 1
    ret = []
    while(1):
        url = "http://www.toutiao.com/search_content/?offset="+str(offset)+"&format=json&keyword="+str(keyword)+"&count=20&cur_tab=4"
        r = requests.get(url,headers=headers)
        infos = r.json()
        for info in infos['data']:
            name = info['name']
            uid = info['id']
            ret.append({'id':uid,'name':name})
            #print("%d-%s-%s"%(index,name,uid))
            index = index+1
        if infos['return_count'] < 20:
            break;
        else:
            offset = offset + 20
    return ret

def get_article_content(item_id):
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Cookie':'tt_webid=6457127978488366605;'}
    url = "http://www.toutiao.com/i"+str(item_id)+"/"
    r = requests.get(url,headers=headers)
    if r.status_code == 200:
        html = r.text
        start1 = html.find("content: '") + 10
        end1 = html.find("'.replace(",start1)
        ret = html[start1:end1]
        regex = re.compile(r'&lt;.*?&gt;') 
        tmp = regex.sub('',ret)
        return tmp
    else:
        return None
#get_hot_article_info(6351943396,999,0)
#get_hot_article_info(62257280632,999,0)
get_hot_article_info(sys.argv[1],0)
#search_user_from_keyword("把妹")
'''
#根据用户名中的关键字,找出其所有文章
user_infos = search_user_from_keyword("把妹")
for each in user_infos:
    print("----%s-%s----------"%(each['id'],each['name']))
    get_hot_article_info(each['id'],999,10000)
    time.sleep(1)
    print("---------------------")
'''
#html = get_article_content(6456978028344902157)
#print(html)
#get_wordcloud(html)
