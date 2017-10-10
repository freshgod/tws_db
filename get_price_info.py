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
    DBNAME = stock_number

    # create db
    client.drop_database(DBNAME)
    client.create_database(DBNAME)
    client.switch_database(DBNAME)

    # Write points by parts
    data_points_parts = chunkify(data_points, 10)
    for data_part in data_points_parts:
        client.write_points(data_part,time_precision='s')
    
if __name__ == '__main__':
    stock_number = '2454'
    price_info_list = get_yahoo_price_info(stock_number,START_DATE,datetime.datetime.today().strftime("%Y-%m-%d"))
    
    add_price_info_to_db(stock_number,price_info_list)