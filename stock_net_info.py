import urllib
from urllib import request
import csv
from bs4 import BeautifulSoup
from urllib.request import *
import os.path
import re
from datetime import date
import datetime as dt
import time

class stock_info:
    name = ""
    stock_number = ""
    info_list = []
    year_eps_list = []
    season_eps_list = []
    interest_list = []
    history_data = []
    stock_ma = []
    stock_distribute = []
    close = 0.0
    net_worth = 0.0
    debt = ""
    year = 0
    season = 0
    director_holding = 0.0
    
    def __init__(self, number, directory_path="history_data", year = 5, season = 4, stock_distribute = None):
        self.year = year
        self.season = season
        self.stock_number = number
        self.name = get_stock_name(number)
        # print(self.name)
        self.year_eps_list = get_stock_year_eps(number,year)[1:]
        # print(self.year_eps_list)
        self.season_eps_list = get_stock_season_eps(number,season)[1:]
        # print(self.season_eps_list)
        self.info_list = get_stock_info(number,["收盤價", "每股淨值(元)","負債比例"])[1:]
        try:
            self.close = float(self.info_list[0])
        except:
            self.close = float(0)
        try:
            self.net_worth = float(self.info_list[1])
        except:
            self.net_worth = float(0)
        self.debt = self.info_list[2]
        # print(self.info_list)
        self.interest_list = get_stock_interest_info(number,year)[1:]
        for item in self.interest_list:
            item = float("%.2f"%(item))
        self.history_data = get_stock_day_data(number, directory_path)
        self.stock_ma_list = get_stock_ma(number)
        if stock_distribute == None:
            try:
                self.stock_distribute = get_stock_distribute(number)
            except ConnectionResetError as e:
                self.stock_distribute = None
        else:
            self.stock_distribute = stock_distribute
        self.director_holding = float(get_stock_holding_info(number,["董監持股"])[1])

# name at first
def get_stock_type_old_list(stock_type="EB028000E"):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/ze/zeg/zeg_'+stock_type+'_I.djhtm'
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zh/zhc/zhc_' + stock_type + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read().decode('big5','ignore'),"html.parser")
    all_tr = soup.find_all('tr')

    p = re.compile(r'.*([0-9][0-9][0-9][0-9]).*')
    
    result_list = []
    # stock_info
    for tr in all_tr:
        all_td = tr.find_all('td')
        # print("============================")
        # print(all_td[0].text.encode('big5','ignore').decode('big5'))
        # print("============================")
        m = p.match(all_td[0].text.replace('\n','').replace('\t','').replace('\r',''))
        if m:
            if m.group(1) != None:
                print(m.group(1))
                result_list.append(m.group(1))
                
    return result_list
    
# name at first
# [ name, eps1, eps2, eps_last_seasons, eps ]
def get_stock_interest_info(stock_number,last_seasons):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zc/zcc/zcc_' + stock_number + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read(),"html.parser")
    all_td = soup.find_all('td')
    
    first_td = soup.find('td', {'class':'t10'})
    
    # stock name
    interest_list = []
    stock_name = ""
    if first_td:
        p = re.compile(r'(.*)\([0-9]*\).*')
        m = p.match(first_td.text)
        if m:
            stock_name = m.group(1)
            interest_list.append(stock_name)
            
    # stock_eps
    p = re.compile(r'2[0-9][0-9][0-9]')
    i = 0
    while(i < len(all_td)):
        if p.match(all_td[i].text):
            interest_list.append(float(all_td[i+7].text))
            i = i+7
        if len(interest_list) > last_seasons:
            break
        i = i+1
                
    sum = 0.0
    for value in interest_list[1:last_seasons+1]:
        sum = sum+value
    interest_list.append(sum/last_seasons)
    return interest_list


# name at first
def get_stock_info(stock_number,info_list):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zc/zca/zca_' + stock_number + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read().decode('big5','ignore'),"html.parser")
    all_tr = soup.find_all('tr')
    
    first_td = soup.find('td', {'class':'t10'})
    
    # stock name
    result_info_list = [None]*(len(info_list) + 1)
    stock_name = ""
    if first_td:
        p = re.compile(r'[\r\n ]*(.*)[\t\r\n ]*\([0-9]*\)')
        m = p.match(first_td.text)
        if m:
            stock_name = m.group(1).replace('\t','').replace(' ','')
            result_info_list[0] = stock_name
    else:
        print("stock %s not found"%(stock_number))
            
    # stock_info
    for tr in all_tr:
        all_td = tr.find_all('td')
        for td_index in range(len(all_td)):
            if all_td[td_index]:
                text = all_td[td_index].text.encode('big5','ignore').decode('big5')
                for info_index in range(len(info_list)):
                    if info_list[info_index] == text:
                        result_info_list[info_index+1]=all_td[td_index+1].text
    return result_info_list
    
    
def get_stock_total(stock_number,info_list):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zc/zcj/zcj_' + stock_number + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read(),"html.parser")
    all_tr = soup.find_all('tr')
            
    # stock_info
    result_info_list = [None]*(len(info_list))
    for tr in all_tr:
        all_td = tr.find_all('td')
        for td_index in range(len(all_td)):
            if all_td[td_index]:
                text = all_td[td_index].text.encode('big5','ignore').decode('big5')
                for info_index in range(len(info_list)):
                    if info_list[info_index] == text:
                        result_info_list[info_index]=all_td[td_index+1].text.replace(",","")
    return result_info_list
    
# name at first
# [ name, eps1, eps2, eps_last_seasons, eps ]
def get_stock_season_eps(stock_number,last_seasons):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zc/zcq/zcq_' + stock_number + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read(),"html.parser")
    all_tr = soup.find_all('tr')
    
    first_td = soup.find('td', {'class':'t10'})
    
    # stock name
    eps_list = []
    stock_name = ""
    if first_td:
        p = re.compile(r'(.*)\([0-9]*\)')
        m = p.match(first_td.text)
        if m:
            stock_name = m.group(1)
            eps_list.append(stock_name)
            
    # stock_eps
    for tr in all_tr:
        all_td = tr.find_all('td')
        p_eps = re.compile(r'[ ]*每股盈餘[^-－]*$')
        m_eps = p_eps.match(all_td[0].text)
        if all_td[0] and m_eps:
            for td in all_td[1:last_seasons+1]:
                # print(td)
                try:
                    eps_list.append(float(td.text))
                except:
                    print(stock_number)
                    print(all_td)
                    eps_list.append(0.0)
                
    sum = 0
    for value in eps_list[1:last_seasons+1]:
        sum = sum+value
    eps_list.append(sum)
    return eps_list
    
# name at first
# [ name, eps1, eps2, eps_last_years, eps/year ]
def get_stock_year_eps(stock_number,last_years=5):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zc/zcq/zcqa/zcqa_' + stock_number + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read(),"html.parser")
    all_tr = soup.find_all('tr')
    
    first_td = soup.find('td', {'class':'t10'})
    
    # stock name
    eps_list = []
    stock_name = ""
    if first_td:
        p = re.compile(r'(.*)\([0-9]*\)')
        m = p.match(first_td.text)
        if m:
            stock_name = m.group(1)
            eps_list.append(stock_name)
            
    # stock_eps
    for tr in all_tr:
        all_td = tr.find_all('td')
        p_eps = re.compile(r'[ ]*每股盈餘[^-]*$')
        m_eps = p_eps.match(all_td[0].text)
        if all_td[0] and m_eps:
            leave_flag = 0
            for td in all_td[1:last_years+1]:
                try:
                    eps_list.append(float(td.text))
                except:
                    print(stock_number)
                    print(all_td)
                    eps_list.append(0.0)

    sum = 0
    actual_year = 0
    for value in eps_list[1:last_years+1]:
        sum = sum+value
        actual_year = actual_year + 1
    if(actual_year):
        eps_list.append(sum/actual_year)
        
    return eps_list

# http://jsjustweb.jihsun.com.tw/z/zc/zco/zco.djhtm?a=2454&e=2017-9-19&f=2017-9-20
def get_buy_sell(stock_number, days=60, brokers=3, total_volume=0, total_max_volume=0):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zc/zco/zco.djhtm'
    
    # get today
    today = dt.datetime.today().strftime("%Y-%m-%d").replace("-0","-")
    days_before_today = (dt.datetime.today() - dt.timedelta(days=days)).strftime("%Y-%m-%d").replace("-0","-")
    
    urladdr = urladdress + "?a=" + str(stock_number) + "&e=" + days_before_today + "&f=" + today

    # print(urladdr)

    response = urlopen(urladdr)

    # get charset is good
    # print(response.info().get_content_charset())

    soup = BeautifulSoup(response.read(),"html.parser")

    # dates = soup.findAll("div", {"id" : re.compile('date.*')})

    all_tr = soup.find_all('tr')

    count = 0
    buy_sum = 0
    sell_sum = 0
    total_buy_sum = 0
    total_sell_sum = 0
    for tr in all_tr:
        all_td = tr.find_all('td',{'class' : re.compile('t[34][tn]1')})
        if all_td and len(all_td) > 8 and count < brokers:
            if all_td[0].find('a'):
                buy_sum += int(all_td[3].text.replace(',',''))
            if all_td[5].find('a'):
                sell_sum += int(all_td[8].text.replace(',',''))
            count = count+1
            
        if all_td and len(all_td) > 8:
            if all_td[0].find('a'):
                total_buy_sum += int(all_td[3].text.replace(',',''))
            if all_td[5].find('a'):
                total_sell_sum += int(all_td[8].text.replace(',',''))
            
    if buy_sum > total_volume and sell_sum > total_volume:
        if total_max_volume == 0 or (buy_sum < total_max_volume and sell_sum < total_max_volume):
            return [float(float(buy_sum)/float(sell_sum)),total_buy_sum,total_sell_sum]
        else:
            return [-1,buy_sum,sell_sum]
    elif total_volume == 0:
        if sell_sum:
            return [float(float(buy_sum)/float(sell_sum)),total_buy_sum,total_sell_sum]
        else:
            return [0,total_buy_sum,total_sell_sum]
    else:
        return [-1,total_buy_sum,total_sell_sum]

def get_page_request(url):
    req = urllib.request.Request(
        url,
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    return urllib.request.urlopen(req)


def get_select_stock(append_str="",out_dir="../static/stock_select/"):
    today = date.today()
    if os.path.exists(out_dir + str(today) + append_str + '.csv'):
       return 

    f = get_page_request('http://justdata.yuanta.com.tw/z/zk/zkf/zkResult.asp?A=x@490,a@7,b@-0.3;x@510,a@7,b@1;x@920,a@15;x@590,a@13;x@980,a@10;x@990,a@50;x@500,a@7,b@7&B=&C=LA,SO@1&D=1&E=0&G=1&site=')
    soup = BeautifulSoup(f.read().decode('big5','ignore'),"html.parser")

    table = soup.find('table',{"class":"zkt1"})
    if table:
        all_tr = table.find_all('tr',{'class':re.compile('zkt2R*')})
        
    # header
    header_row = []
    header_td = table.find('td',{'class':"zkt1L"})
    if header_td:
       header_row = []
       all_td = header_td.find_all('td',{'class':'zkt1HC'})
       for td in all_td:
           header_row.append(td.text.replace('\n','').replace('\r','').replace('\t',''))
    
    #header_row.append("stock_number")
    #header_row.append("open")
    #header_row.append("quote_change")
    #header_row.append("quote_change_percent")
    #header_row.append("min_eps_7")
    #header_row.append("avg_eps_7")
    #header_row.append("net_worth")
    #header_row.append("PER")

    # header_row.append("buy_sell")

    p = re.compile(r'([^0-9]*[0-9\.]*).*')
    rows = []
    for tr in all_tr:
        all_td = tr.find_all('td')
        if all_td and all_td[0].find("a"):
            temp_row = []
            for td in all_td:
                m = p.match(td.text.replace('\n',''))
                if m :
                    temp_row.append(m.group(1))
            rows.append(temp_row)

    with open(out_dir + str(today) + append_str + '.csv', 'w', newline='\n') as f:
        writer = csv.writer(f)
        writer.writerow(header_row)
        writer.writerows(row for row in rows if row)
        
def get_stock_list(market_list):
    stock_list = []
    
    if (market_list):
        f = get_page_request('http://isin.twse.com.tw/isin/C_public.jsp?strMode=2')
    else:
        f = get_page_request('http://isin.twse.com.tw/isin/C_public.jsp?strMode=4')
    if not f:
        return stock_list
    
    soup = BeautifulSoup(f.read(),"lxml")
    if not soup:
        return stock_list
    
    table = soup.find('table',attrs={'class':'h4'})
    
    rows=[]
    for row in table.find_all('tr'):
        # rows.append([val.text for val in row.find_all('td')])
        all_td = row.find('td')
        if all_td:
            p = re.compile(r'(^[\d][\d][\d][\d])[ ][ ]*')
            m = p.match(all_td.text)
            if m:
                rows.append(m.group(1))

    #with open('output_file.csv', 'w', newline='\n') as f:
    #    writer = csv.writer(f)
    #    writer.writerow(headers)
    #    writer.writerows(row for row in rows if row)
        
    return rows

def get_all_stock_type_list():
    return get_stock_classified_list("EB011000E", "上市")+get_stock_classified_list("EB141000B", "上櫃")
    # return get_stock_classified_list("EB141000B", "上櫃")

def get_stock_type_list(stock_type="EB011000E"):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/ze/zeg/zeg_'+stock_type+'_I.djhtm'
    # urladdress = 'http://jsjustweb.jihsun.com.tw/z/zh/zhc/zhc_' + stock_type + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read().decode('big5','ignore'),"html.parser")
    all_script = soup.find_all('script',{"language":"javascript"})

    p = re.compile(r'.*\'([0-9]{4})\'.*\'(.*)\'.*')
    
    result_list = []
    # stock_info
    for sc in all_script:
        text = sc.text.replace('\n','').replace('\r','').replace('\t','')
        # print(text)
        m = p.match(text)
        if m :
            # result_list.append([m.group(1),m.group(2)])
            result_list.append(m.group(1))
                
    return result_list
    
def get_stock_classified_list(stock_type="EB011000E", title=""):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/ze/zeg/zeg_'+stock_type+'_I.djhtm'
    # urladdress = 'http://jsjustweb.jihsun.com.tw/z/zh/zhc/zhc_' + stock_type + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read().decode('big5','ignore'),"html.parser")
    all_option = soup.find_all('option')

    result_list = []
    # stock_info
    for opt in all_option:
        if (re.compile(r'EB.*').match(opt['value'])):
            if opt.text != "上市" and opt.text != "上櫃":
                result_list.append([opt['value'],title + " " + opt.text])
                
    return result_list
    
def get_stock_net_reduce_info(stock_number):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zc/zcx/zcxD6.djjs?A='+stock_number
    # urladdress = "file:///D:/cygwin_home/fresh.lee/python_test/stock_viewer/stock_viewer/other_program/test.html"
    response = urlopen(urladdress)
    res_text = response.read().decode('big5').replace("document.writeln('",'').replace("\\n');","")
    # res_text = res_text.replace("</tr>","</tr>\r\n").replace("</td>","</td>\r\n")
    soup = BeautifulSoup(res_text,"html.parser")
    # print(soup.decode('big5'))
    
    all_tr = soup.find_all('tr')
    
    result_list = []
    for tr in all_tr:
        all_td = tr.find_all('td')
        if len(all_td) == 6 and all_td[0]['class'] == ["t4t1"]:
            result_list.append(all_td[5].text)
    return result_list
    
def get_stock_name(stock_number):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zc/zcc/zcc_' + stock_number + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read(),"html.parser")
    first_td = soup.find('td', {'class':'t10'})
    
    # stock name
    stock_name = ""
    if first_td:
        p = re.compile(r'(.*)\([0-9]*\).*')
        m = p.match(first_td.text)
        if m:
            stock_name = m.group(1)
            
    return stock_name
        
def make_url_tw(ticker_symbol):
    base_url = "http://chart.finance.yahoo.com/table.csv?s="
    urladdress = base_url + ticker_symbol + ".TW"
    return urladdress

def make_file_path(ticker_symbol,directory):
    # file_name = directory + "/" + str(date.today()) + "_" + ticker_symbol + ".csv"
    file_name = directory + "/" + ticker_symbol + ".csv"
    return file_name
    
def pull_historical_data(ticker_symbol, file_path, make_url=make_url_tw):
    try:
        urlretrieve(make_url(ticker_symbol), file_path)
    except:
        print("stock %s not found"%(ticker_symbol))
        pass
    
def get_stock_day_data(stock_number,directory_path="history_data"):
    file_path = make_file_path(stock_number, directory_path)
    pull_historical_data(stock_number, file_path)
    try:
        data = list(csv.reader(open(file_path)))
    except:
        return []
    return data

def makelist(table):
    result = []
    allrows = table.findAll('tr')
    for row in allrows:
        result.append([])
        allcols = row.findAll('td')
        for col in allcols:
            thestrings = [s for s in col.findAll(text=True)]
            thetext = ''.join(thestrings)
            result[-1].append(thetext)
    return result
    
def get_stock_ma(stock_number):
    urladdress = 'http://www.cnyes.com/twstock/Technical/'+stock_number+'.htm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read().decode('big5','ignore'),"html.parser")
    all_table = soup.find_all('table')
    
    ma_array = makelist(all_table[1])
    
    if(len(ma_array) < 4): return []
    
    stock_ma_list = [[1,3,5,10,20,60,120,240]]
    stock_ma_list.append(ma_array[2][1:])
    return stock_ma_list
    
def find_top_distribute(distribute,people):
    # distribute = stock_info.stock_distribute
    sum = 0
    people_sum = 0
    
    if people < distribute[-1]['people']:
        sum = distribute[-1]['percent']
    else:
        for item in reversed(distribute):
            if people_sum + item['people'] >= people:
                sum = sum + (item['percent']*(people-people_sum)/item['people'])
                break
            sum = sum + item['percent']
            people_sum = people_sum + item['people']
    return float("%.2f"%(sum))
    
def find_below_distribute(distribute,stocks):
    # distribute = stock_info.stock_distribute
    sum = 0
    for item in distribute:
        if stocks >= item['stock']:
            sum = sum + item['percent']
        else:
            break
    return float("%.2f"%(sum))
    
def get_stock_distribute(stock_number):
    urladdress = 'http://histock.tw/stock/large.aspx?no='+stock_number
    response = urlopen(urladdress)

    if None == response:
        return None
    soup = BeautifulSoup(response.read().decode('big5','ignore'),"html.parser")
    table = soup.find('table',{'class':'tb-stock'})
    
    if None == table:
        return None
    
    all_tr = table.find_all('tr')
    
    result = []
    flag = 0
    for tr in all_tr:
        all_td = tr.find_all('td')
        if all_td == []: continue
        # all_td[0] : index
        # all_td[1] : stock
        # all_td[2] : people
        # all_td[3] : total stock
        # all_td[4] : percent
        p = re.compile(r'[^-]*[-]([0-9]*)')
        
        stock_distribute = {}
        # stock_distribute['stock'] 
        match = p.match(all_td[1].text.replace(',',''))
        if match:
            stock_distribute['stock'] = int((int(match.group(1)) + 1)/1000)
        elif flag == 0:
            flag = 1
            stock_distribute['stock'] = 1001
        else:
            continue
        stock_distribute['people'] = int(all_td[2].text.replace(',',''))
        stock_distribute['total_stock'] = int(all_td[3].text.replace(',',''))
        stock_distribute['percent'] = float(all_td[4].text)
        
        result.append(stock_distribute)
        
    return result
        
# name at first
def get_stock_holding_info(stock_number,info_list):
    urladdress = 'http://jsjustweb.jihsun.com.tw/z/zc/zcj/zcj_' + stock_number + '.djhtm'
    response = urlopen(urladdress)
    soup = BeautifulSoup(response.read().decode('big5','ignore'),"html.parser")
    all_tr = soup.find_all('tr')
    
    first_td = soup.find('td', {'class':'t10'})
    
    # stock name
    result_info_list = [None]*(len(info_list) + 1)
    stock_name = ""
    if first_td:
        p = re.compile(r'[\r\n ]*(.*)[\t\r\n ]*\([0-9]*\)')
        m = p.match(first_td.text)
        if m:
            stock_name = m.group(1).replace('\t','').replace(' ','')
            result_info_list[0] = stock_name
    else:
        print("stock %s not found"%(stock_number))
            
    # stock_info
    for tr in all_tr:
        all_td = tr.find_all('td')
        for td_index in range(len(all_td)):
            if all_td[td_index]:
                text = all_td[td_index].text.encode('big5','ignore').decode('big5')
                for info_index in range(len(info_list)):
                    if info_list[info_index] == text:
                        result_info_list[info_index+1]=all_td[td_index+2].text.replace('%','')
    return result_info_list
        
    