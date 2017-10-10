# -*- coding: utf-8 -*-
import datetime
import time

import urllib
from urllib import request
from bs4 import BeautifulSoup

from influxdb import InfluxDBClient
from get_yahoo_price_info import get_yahoo_price_info

HOST='localhost'
PORT=8086
USER = 'root'
PASSWORD = ''
START_DATE='2001-01-01'

def add_price_info_to_db(stuck_number,price_info_list):    
    stock_price_info_list = []
    for item in price_info_list:
    
        date = datetime.datetime.strptime(item['Date'],"%Y-%m-%d")
        
        for key in item.keys():
            if key == "Date":
                continue
            item[key]=float(item[key])
        
        stock_price_info = {
            "measurement": "price_info",
            "time": int(date.strftime('%s')),
            "fields": item
        }   
        stock_price_info_list.append(stock_price_info)
    
    write_influx_data(stuck_number,stock_price_info_list)
    
def chunkify(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

def write_influx_data(stock_number, data_points):
    client = InfluxDBClient(HOST, PORT, USER, PASSWORD, stock_number)
    DBNAME = "stock_"+stock_number+".TW"

    # create db
    client.create_database(DBNAME)
    client.switch_database(DBNAME)

    # Write points by parts
    if len(data_points) > 100:
        data_points_parts = chunkify(data_points, 10)
        for data_part in data_points_parts:
            client.write_points(data_part,time_precision='s')
    else:
        client.write_points(data_points,time_precision='s')

def get_newest_data_date(stock_number):
    client = InfluxDBClient(HOST, PORT, USER, PASSWORD, stock_number)
    DBNAME = "stock_"+stock_number+".TW"

    # create db
    client.create_database(DBNAME)
    client.switch_database(DBNAME)
    
    # get the last Date
    query = 'select last(Date) from price_info'
    result = list(client.query(query, database=DBNAME))
    
    if [] == result:
        return ""
    else:
        return result[0][0]['last']

def read_list_from_file(file="stock.csv"):
    with open(file) as f:
        stock_list = f.read().splitlines()
    return stock_list
    
def remove_stock_in_file(stock_number, file="stock.csv"):
    f = open(file)
    lines = f.readlines()
    f.close()
    with open(file,"w") as f:
        for line in lines:
            if stock_number in line:
                continue
            f.write(line)

if __name__ == '__main__':
    stock_list = read_list_from_file()
    todat_date = datetime.datetime.today().strftime("%Y-%m-%d")
    for stock_number in stock_list:
        print("get %s history data"%(stock_number))
        last_date = get_newest_data_date(stock_number)
        if "" == last_date:
            last_date = START_DATE
        
        print("get %s from %s to %s"%(stock_number, last_date, todat_date))
        price_info_list = get_yahoo_price_info(stock_number,last_date,todat_date)
        if price_info_list:
            add_price_info_to_db(stock_number,price_info_list)
        else:
            print("%s has no history data"%(stock_number))