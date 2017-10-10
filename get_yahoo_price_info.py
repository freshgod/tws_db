import re
import urllib
import calendar
import datetime
import getopt
import sys
import time

try:
    # for Python 2.x
    from StringIO import StringIO
except ImportError:
    # for Python 3.x
    from io import StringIO
import csv

crumble_link = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
cookie_regex = r'set-cookie: (.*?); '
quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&crumb={}'

def get_crumble_and_cookie(symbol):
    link = crumble_link.format(symbol)
    response = urllib.request.urlopen(link)
    match = re.search(cookie_regex, str(response.info()))
    cookie_str = match.group(1)
    text = response.read().decode('utf-8')
    match = re.search(crumble_regex, text)
    crumble_str = match.group(1)
    return crumble_str, cookie_str

def download_quote(symbol, date_from, date_to):
    time_stamp_from = calendar.timegm(datetime.datetime.strptime(date_from, "%Y-%m-%d").timetuple())
    time_stamp_to = calendar.timegm(datetime.datetime.strptime(date_to, "%Y-%m-%d").timetuple())

    attempts = 0
    while attempts < 5:
        crumble_str, cookie_str = get_crumble_and_cookie(symbol)
        link = quote_link.format(symbol, time_stamp_from, time_stamp_to, crumble_str)
        #print link
        r = urllib.request.Request(link, headers={'Cookie': cookie_str})

        try:
            response = urllib.request.urlopen(r)
            text = response.read().decode('utf-8')
            print("%s downloaded"%(symbol))
            return text
        except urllib.error.URLError:
            print("%s failed at attempt %d"%(symbol, attempts))
            attempts += 1
            time.sleep(2*attempts)
    return ""

def get_yahoo_price_info(symbol, from_date, to_date):
    symbol = symbol+".TW"
    text = download_quote(symbol, from_date, to_date)
    if "" == text :
        return
    f = StringIO(text)
    reader = csv.DictReader(f, delimiter=',')
    rows=[]
    for row in reader:
        if "null" in row.values():
            continue
        rows.append(row)
    return rows
