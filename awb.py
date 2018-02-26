import urllib
# coding:utf-8
import datamysql
import requests
import json
import re
import time

def search_key(key,page)    :
    headers = {'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive',
               'Content-Length': '189', 'Content-Type': 'application/json;charset=UTF-8',
               'Cookie': 'Hm_lvt_45cdb9a58c4dd401ed07126f3c04d3c4=1519570358; awbYHQXTK=hWXM8jexf8P1LNW3PFuVLIEI3ADpVqxfoAnzpfaFhMPsbTYMbioZky0UwPjn8M40wI7U8R4oE8T+MDMJQjGzGQ==; Hm_lpvt_45cdb9a58c4dd401ed07126f3c04d3c4=1519571392',
               'DNT': '1', 'Host': 'top.aiweibang.com', 'Origin': 'http://top.aiweibang.com', 'Pragma': 'no-cache',
               'Referer': 'http://top.aiweibang.com/user/search_advanced?kw=%E5%95%8A&kwtype=description&readmin=1000&readmax=100001&pageindex=9&pagesize=10',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest'}
    url='http://top.aiweibang.com/user/getsearch_advanced'
    payload = {"kw":key,"kwtype":"description","provinceid":None,"cityId":None,"kindid":None,"kindclassid":None,"readmin":"1000","readmax":100001,"original":None,"video":None,"pageindex":page,"pagesize":10}
    r = requests.post(url,headers=headers,json=payload)
    try:

        wx_list = json.loads(r.text)['data']['data']
        for i in wx_list:
            wxname = i['Name']
            wxid = i['Alias']
            try:
                wxhost = i['Reg']['RegName']
            except:wxhost=''
            month_count=''
            avg_read=i['TopReadNumAvg']
            about=i['Description']
            key_page=''
            cookie_id=''
            bad_words = 0
            if laji_check(wxname, wxhost) == 1:
                bad_words = 1
            datamysql.inmysql_moth_read(fix_wxname(wxname), wxid, wxhost, month_count, avg_read, bad_words,fix_wxname(about),key_page, cookie_id)
def fix_wxname(wxname):
    p=re.compile('<.*?>|\'|\n|\r')
    s=p.sub('',wxname).replace('【','')
    return s
def laji_check(wxname,zhuti):
    p1 = re.compile('股票|娱乐|周公|股市|财|保险|金融|理财|互联网|文摘|经济|企业|李嘉|总裁|管理|励志|真相|骚|星座|说话术|说话技巧|心理学|经典|语录|官方|变漂亮|睡前|陈安之|小知识|小助手|百科|窍门|运势|算命|养身|养生|美丽|创业|精英|女|美人|八卦|搞笑|内涵|密|风水|大师|法师|每天|人民法院|^教|瘦|肤|生活助手|百米生活|公安|脸红|爆笑|短片|胸|潮流|两性|妞|穿衣|搭配|美文|男|化妆|相册|姐夫|佳人|开心|学点|.*人那些事|世界.*乐部|头发|18|禅|妈|段子|银行|电商|今曰关注|大学$|二货村|中国梦|发布|风流|小.*片|心语|分公司|陈大|腾讯|糗|小姨子|.*姿势|有话说|小说|集团|老婆|我爱你|团.*委|政.*府|教育厅$|^中央|共.*团|公司|医院|中学|小学|局$|协会$|委员会$|.*一中|警|幼儿园|检察|电视台|国税|联通|开发区|人才市场|血站|中心卫生院|驾校|购物中心|万达')
    p2 = re.compile('政府|中央|中共|中国移动|^中国平安|共产党|局$|院$|公安|青年|委员会|集团|税务|工会|旅游局|小学|中学|医院|深圳市腾讯|该帐号服务由')
    laji_wxname = p1.search(str(wxname))
    laji_zhuti = p2.search(str(zhuti))

    if str(laji_wxname) == 'None' and str(laji_zhuti) == 'None':
        laji=888
    else:
        #print('laji=1',wxname,zhuti)
        laji=1
    return laji

if __name__ == '__main__':
    inFile = open('keywords', 'r')
    keys0 = inFile.readlines()
    inFile.close()
    for page in range(1,11):
        for key in keys0:
            print(key.strip(),page)
            search_key(key.strip(),page)
            time.sleep(2)