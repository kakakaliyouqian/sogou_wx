import requests
import re
from datamysql import Mogodb_name
import datamysql
import time
from lxml import etree

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

def fix_wxname(wxname):
    p=re.compile('<.*?>|\'|\n|\r')
    s=p.sub('',wxname).replace('【','')
    return s
def fix_wxid(wxid):
    p=re.compile('em_weixinhao">(.*?)</label>')
    s=p.findall(wxid)[0]
    return s

def search_key(url,proxy,cookie,key_page)    :
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'DNT': '1', 'Host': 'weixin.sogou.com', 'Pragma': 'no-cache', 'Referer': 'http://weixin.sogou.com/weixin?type=2&s_from=input&query=%E9%98%BF&ie=utf8&_sug_=n&_sug_type_=', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}

    title_keys=[]
    pages=[]
    try:
        r = requests.get(url, proxies=proxy, headers=headers,cookies=cookie, timeout=8)
        r.encoding = 'utf-8'
        s = etree.HTML(r.text)
        list = s.xpath('//li[@id]//div[2]/div/a/text()')
        if list==[]:
            #print('status=', r.status_code)
            ss=0
        else:
            listkey=[]
            for i in list:
                if laji_check(i,'')==1:
                    continue

                tokey=str(i) + '#1'
                if tokey in str(listkey):
                    continue
                else:
                    listkey.append(tokey)
                    datamysql.insert_name_to_mongodb(tokey)
                time.sleep(0.5)

                tokey2 = str(i)[0:2] + '#1'
                if tokey2 in str(listkey):
                    continue
                listkey.append(tokey2)
                datamysql.insert_name_to_mongodb(str(i)[0:2]+ '#1')
            ss = 1
            print('        ',key_page,'---->>>',listkey)
            pages=s.xpath("//a[contains(@id,'sogou_page')]/text()")
    except:
        ss = 0
    return ss,title_keys,pages

def list_moth_read(url,proxy,key_page,key,page,cookie,cookie_id):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'weixin.sogou.com',
        'Referer': 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=%E8%BD%BB%E8%89%B2%E5%BF%97&ie=utf8&_sug_=n&_sug_type_=&w=01019900&sut=1517&sst0=1502674902649&lkt=0%2C0%2C0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    try:
        r = requests.get(url, proxies=proxy, headers=headers,cookies=cookie, timeout=10)
        s = etree.HTML(r.text)
        errors=s.xpath('//*[@id="noresult_part1_container"]/div/p[2]/text()')
        if '暂无与' in str(errors):
            print(errors)
            isok = 1
        else:
            list = s.xpath('//li[@id]')
            account_anti_url='http://weixin.sogou.com'+s.xpath('//*[@id="wrapper"]/script/text()')[0].split('"')[1]
            req = requests.get(account_anti_url, headers=headers).json()
            json_reads = req['msg']
            for i in list:
                wxopenid=i.xpath('./@d')[0]
                if wxopenid in str(json_reads):
                    avg_read = json_reads[wxopenid].split(',')[1]
                    if int(avg_read) > 500:
                        month_count = json_reads[wxopenid].split(',')[0]
                        wxname=i.xpath('string(./div/div[2]/p[1]/a)')
                        wxid=i.xpath('./div/div[2]/p[2]/label/text()')[0]
                        about = i.xpath('string(./dl[1]/dd)')
                        if len(i.xpath('.//dl')) == 3:
                            wxhost = i.xpath('string(./dl[2]/dd)')
                        else:
                            wxhost = ''
                        bad_words = 0
                        if laji_check(wxname, wxhost) == 1:
                            bad_words = 1
                        #print(wxname, wxid, wxhost, month_count, avg_read,bad_words,about)
                        datamysql.inmysql_moth_read(wxname, wxid, wxhost, month_count, avg_read,bad_words,about,key_page,cookie_id)

            if len(json_reads)==0:#如果没有数据获取到，那么page不要累加，太多没数据的页面，浪费搜索时间
                print('>>都没有阅读数据,不进入累加page  ',key_page)
            else:
                if len(list)>5:
                    pages = s.xpath("//a[contains(@id,'sogou_page')]/text()")
                    if str(int(page)+1) in str(pages):
                        Mogodb_name().insert_name_to_mongodb(str(key) + '#' + str(int(page)+1))
                        print(key_page, '  有数据=', len(json_reads),len(list),'个号',pages)
                else:
                    print(key_page, '结束，page不累加',len(list),'个号')
            isok = 1
    except:
        isok = 0
    return isok


if __name__ == '__main__':
    list_moth_read('1', '2', '3')
