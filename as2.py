import random
import threading
import re
import fix
import iplist
import datamysql
import time
import datetime

def get_keywords(key_page,i,iplsit,Cookies_list):
    lock = threading.Lock()
    lock.acquire()
    proxy_random = random.choice(iplsit)
    proxy = {
        'http': 'http://' + proxy_random,
        'https': 'https://' + proxy_random,
    }
    lock.release()
    if key_page[i]=='':
        pass
    else:
        p = re.compile('(.*?)#(\d+)')
        dd = p.findall(key_page[i])
        key = dd[0][0]
        page = dd[0][1]
        url = 'http://weixin.sogou.com/weixin?usip=&query=' + str(
            key) + '&ft=&tsn=1&et=&interation=&type=2&wxid=&page=' + str(page) + '&ie=utf8'
        cookie_value = random.choice(Cookies_list)
        cookie = {'Cookie':'SUID=' + str(cookie_value['SUID']) + '; SUV=009F178CB4A8FD4159B5F4F5A7CF1860; CXID=BB13F9E4BB0AC972488C27042B8AD0B2; pgv_pvi=1013663744; wuid=AAFcjOzfGwAAAAqZOEeIUwcAAAA=; FREQUENCY=1508226538938_1; usid=eQFnTprT02cYYSjR; SUID=41FDA8B42320940A0000000059B5F4F2; GOTO=; weixinIndexVisited=1; ABTEST=8|1516028512|v1; IPLOC=CN3100; SUIR=' + str(cookie_value['SUIR']) + '; SNUID=' + str(cookie_value['SNUID']) + '; sct=265; JSESSIONID=aaa-lePdWTAyfgls39Bew; ppinf=5|1517244528|1518454128|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo1NDolRTUlOEQlQTElRTUlOEQlQTElRTUlOEQlQTElRTklODclOEMlRTYlOUMlODklRTglOEElQjF8Y3J0OjEwOjE1MTcyNDQ1Mjh8cmVmbmljazo1NDolRTUlOEQlQTElRTUlOEQlQTElRTUlOEQlQTElRTklODclOEMlRTYlOUMlODklRTglOEElQjF8dXNlcmlkOjQ0Om85dDJsdUFZYWJkdU1WVkZCNkMtMlREOVA4Mk1Ad2VpeGluLnNvaHUuY29tfA; pprdig=oZBcHK7eqYigBqkLaUSNmbCpooCN0Y0ZxZuRW3P2ahB8cRbL2aMbPSAgR6dPumDErKAKcYknF_IZE91lIdKb6UIChWjWr3yC2Q0Q-ESWDx59I88UR6J3or0yr2mGmwznP-KgDJQU-hk_JWMXhp_51RgFP1qYJ1bhq0Ffz__VV1Y; sgid=06-30822981-AVpvUHBGzrcuNblAAkf0v10; ' \
        'ppmdig=' + str(cookie_value['ppmdig'])}
        ss = fix.search_key(url, proxy,cookie,key_page[i])
        pages=ss[2]

        if ss[0] == 1:
            datamysql.up_search_key_to_mongodb(key_page[i])
            for p in pages:#还有省下几页关键词待搜索
                datamysql.insert_search_key_to_mongodb(str(key) + '#' + str(p))
            #print('关键词累加', key)

def wx_keywords_proxy(key_page,concurrency,concurrency_max,iplsit,suids):
    # 一个线程处理一条ip
    all_thread = []
    long = len(key_page)
    chongzhi=0
    while long > 100:
            for i in range(0, concurrency):
                t = threading.Thread(target=get_keywords, args=(key_page, i,iplsit,suids))
                all_thread.append(t)
                t.setDaemon(True)
                t.start()
            for t in all_thread:
                try:
                    t.join(60)
                except:
                    continue
            time.sleep(10)

            chongzhi += 1
            if chongzhi > 10:
                key_page = datamysql.get_search_key_to_mongodb()
                #suids = iplist.get_suid()
                chongzhi = 0
            if chongzhi > 1110:
                print(chongzhi, "重新getiplist")
                chongzhi = 0
                iplsit = iplist.get_iplist()
            long = len(key_page)

            concurrency = long
            if concurrency > concurrency_max:
                concurrency = concurrency_max
            print('concurrency=', concurrency,'ips=', len(iplsit), '    剩余关键词=', long, '       ', datetime.datetime.now())
    print('long=', long, 'breakout')

def cc(concurrency_max):
    iplsit = iplist.get_iplist2()
    suids = iplist.get_suid()
    key_page = datamysql.get_search_key_to_mongodb()
    print('ips=', len(iplsit), 'keys=', len(key_page), '个单字关键词需要查[[[')
    concurrency = 200
    wx_keywords_proxy(key_page, concurrency, concurrency_max, iplsit, suids)

if __name__ == '__main__':
    cc(2000)
