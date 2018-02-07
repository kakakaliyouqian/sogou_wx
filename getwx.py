#coding=utf-8
import fix
import threading
import re
import iplist
import datetime
import random
import sentemail
import time
from datamysql import Mogodb_name

def get_keywords(key_page,i,iplsit,Cookies_list):
    lock = threading.Lock()
    lock.acquire()
    proxy_random = random.choice(iplsit)
    proxy = {
        'http': 'http://'+ proxy_random[1],
        'https': 'https://'+ proxy_random[1],
    }
    lock.release()
    p = re.compile('(.*?)#(\d+)')
    dd = p.findall(key_page[i])
    key = dd[0][0]
    page = dd[0][1]
    url = 'http://weixin.sogou.com/weixin?type=1&query=' + str(
        key) + '&_sug_type_=&_sug_=n&type=1&page=' + str(page) + '&ie=utf8'

    cookie_value = random.choice(Cookies_list)


    cookie={'Cookie':'SUID='+str(cookie_value['SUID'])+'; '
           'SUV='+str(cookie_value['SUV'])+';'
           ' CXID=BB13F9E4BB0AC972488C27042B8AD0B2;'
           ' pgv_pvi=1013663744; '
           'wuid=AAFcjOzfGwAAAAqZOEeIUwcAAAA; '
           'FREQUENCY=1508226538938_1; '
           'usid=eQFnTprT02cYYSjR;'
           ' SUID='+str(cookie_value['SUID'])+'; GOTO=; weixinIndexVisited=1; '
           'SUIR='+str(cookie_value['SUIR'])+'; '
           'ppinf=5|1516014693|1517224293|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo1NDolRTUlOEQlQTElRTUlOEQlQTElRTUlOEQlQTElRTklODclOEMlRTYlOUMlODklRTglOEElQjF8Y3J0OjEwOjE1MTYwMTQ2OTN8cmVmbmljazo1NDolRTUlOEQlQTElRTUlOEQlQTElRTUlOEQlQTElRTklODclOEMlRTYlOUMlODklRTglOEElQjF8dXNlcmlkOjQ0Om85dDJsdUFZYWJkdU1WVkZCNkMtMlREOVA4Mk1Ad2VpeGluLnNvaHUuY29tfA; '
           'pprdig=YZMDc-8j5KmcaB7EMp7xPizEr4s3z4yOoj3Et3L16C1Ix2UFeHks6pXkv9ai_YFwyZqTjKx-qTZ5Qg_BcqrM0oHsrsUFgFTjzLqc3bAhu99dJy-hvknT9K8EWSgcasavvdXo10o5G1h5dceyjRN-hrG8O6KrWybTqZu-Sfa0amw; sgid=06-30822981-AVpcjGUumQribrsg6cuiaCibSo;'
           ' ABTEST='+str(cookie_value['ABTEST'])+'; '
            'ppmdig='+str(cookie_value['ppmdig'])+'; IPLOC=CN3100; sct=263; JSESSIONID=aaaxd-G0pP9Wi4x2EGKdw; '
           'PHPSESSID='+str(cookie_value['PHPSESSID'])+'; '
            'SNUID='+str(cookie_value['SNUID'])}

    isok = fix.list_moth_read(url, proxy,key_page[i],key,page,cookie,cookie_value['id'])

    if isok==1:
        Mogodb_name().up_name_to_mongodb(key_page[i])
        #q.put(key_page[i])#返回子线程的数据，down=1


def wx_keywords_proxy(key_page,concurrency,concurrency_max,iplsit,suids):
    # 一个线程处理一条ip
    all_thread = []
    long = len(key_page)
    chongzhi=0
    k=0
    while long > concurrency:
        for i in range(0, concurrency):
            t = threading.Thread(target=get_keywords, args=(key_page,i,iplsit,suids))
            all_thread.append(t)
            t.setDaemon(True)
            t.start()
        for t in all_thread:
            try:
                t.join(60)
            except:continue
        time.sleep(1)


        k+=1
        if k>3:
            k=0
            key_page = Mogodb_name().get_name_to_mongodb()
        long = len(key_page)
        concurrency = int(long / 2)
        chongzhi+=1

        if chongzhi>1110:
            print(chongzhi,"重新getiplist")
            chongzhi=0
            iplsit = iplist.get_iplist()
        if concurrency>concurrency_max:
            concurrency=concurrency_max
        print(len(suids),'个cookies   ',len(iplsit),'个代理   ','concurrency=',concurrency,'    剩余关键词=', long,'       ',datetime.datetime.now())

        if long<10:
            print('long=',long,'breakout')
            sentemail.a(str(datetime.datetime.now()))
            break


def cc(concurrency_max):
    iplsit = iplist.get_iplist()
    suids = iplist.get_suid()

    key_page = Mogodb_name().get_name_to_mongodb()
    print(len(iplsit), '个代理   ', len(key_page), '个key', '\n', key_page)
    concurrency = 210
    wx_keywords_proxy(key_page, concurrency, concurrency_max, iplsit, suids)

if __name__ == '__main__':

    cc(2000)
