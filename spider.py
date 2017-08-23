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
import jieba
import jieba.analyse
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class TouTiao(object):
    def __init__(self,uid,hot):
        self.headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        self.uid = str(uid)         #头条号id
        self.hot = int(hot)         #阅读量>hot表示热点文章
        self.article_list = []      #该头条号下的所有文章列表
        self.article_contents =[]   #该头条号下所有文章内容
    #初始化操作,获取cookies:tt_webid
    def init(self):
        r = requests.get("http://www.toutiao.com",headers=self.headers)
        if r.status_code != 200:
            print("spider init failed")
            return ;
        webid = r.cookies['tt_webid']
        self.cookies = dict(tt_webid=webid)
    #根据用户uid,获取其所有文章信息(文章id,文章标题,阅读量,隐藏阅读量)
    def get_article_list(self):
        article_count = 0
        last_time = "0"
        ret = []
        while True:
            url = "https://www.toutiao.com/c/user/article/?page_type=1&user_id="+self.uid+"&max_behot_time="+str(last_time)+"&count=100"
            r = requests.get(url,headers=self.headers,cookies=self.cookies,timeout=3)
            if r.status_code != 200:
                #访问错误,说明没有文章了
                break;
            article_infos = r.json()
            if article_infos is None:
                #文章信息为空,说明没有文章了
                break;
            for info in article_infos['data']:
                title = info['title']
                count = info['go_detail_count']
                hidden_count = info['detail_play_effective_count']
                item_id = info['item_id']
                last_time = info['behot_time']
                #文章访问量大于hot时,加入文章列表中
                if count > self.hot:
                    self.article_list.append({"id":item_id,'title':title,'count':count,'hidden_count':hidden_count})
                    article_count += 1
            print("已获取%d条信息"%(article_count))
            time.sleep(1)   #每隔3秒,获取100条信息
        print("获取%s文章列表完成,共有%d篇文章"%(self.uid,article_count))
    #根据文章id,返回文章内容
    def get_single_article_info(self,item_id):
        url = "http://www.toutiao.com/i" + str(item_id) + "/"
        r = requests.get(url,headers=self.headers,cookies=self.cookies,timeout=3)
        if r.status_code != 200:
            return None
        html = r.text
        #获取script中文章内容部分文本
        start = html.find("content: '") + 10
        end = html.find("'.replace(",start)
        content = html[start:end]
        #将html标签全部删除
        regex = re.compile(r'&lt;.*?&gt;')
        #返回干净的文本
        return regex.sub('',content)
    #获取该头条号下所有文章内容
    def get_all_article(self):
        success_count = 0;
        failed_count = 0;
        for each in self.article_list:
            content = get_single_article_info(each['id'])
            if content is None:
                print ("%s 内容获取失败"%echo['id'])
                failed_count += 1
            else:
                print ("%s 内容获取成功!"%echo['id'])
                success_count += 1
                self.article_contents.append({"id":each['id'],'content':content})
            time.sleep(3)
        print("获取%s所有文章完成,成功%d个,失败%d个"%(self.uid,success_count,failed_count))
    def print_article_list(self):
        index = 1
        for info in self.article_list:
            print("%d-%s-%s-%s-%s"%(index,info['id'],info['title'],info['count'],info['hidden_count']))
            index += 1

def get_wordcloud(text):
    tags = jieba.analyse.extract_tags(text,topK=50)
    for tag in tags:
        print(tag.encode('utf-8'))

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

#get_hot_article_info(6351943396,999,0)
#get_hot_article_info(62257280632,999,0)
#get_hot_article_info(sys.argv[1],0)
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
#html = get_article_content(sys.argv[1])
#print(html)
#get_wordcloud(html)
User1 = TouTiao(6707232556,0)
User1.init()
User1.get_article_list()
User1.print_article_list()
