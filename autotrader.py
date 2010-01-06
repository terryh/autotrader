#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A set of script for you to trade any financial product in market
Author: TerryH, email: terryh.tp@gmail.com,
Thu, 31 Dec 2009 16:09:34 +0800
License: BSD
"""

__version__ = '0.0.1'
__author__ = 'TerryH'

import datetime
import time
import sys
import getopt
import types
import pprint
import re

# our own function
from csvloader import csvtolist 
from order import Order
from function import *


# parameters
re_paras = re.compile("PARAS.?=.?{.*?}",re.DOTALL)
# variables must have default value
re_vars = re.compile("VARS.?=.?{.*?}",re.DOTALL)


def checktimeframe(dataset=[],backbars=300):
    """look for more  than two day, find the time frame for trade, at lease have more thant 2 day item in dataset
    """
    timeframe_list = []
    tl = timeframe_list
    timedelta = 0 # seconds
    initday = 0
    
    for i in range(len(dataset[-backbars:])):
        dt = dataset[i][0]
        if i<2:
            initday = dt.date()
        elif initday and dt.date()>initday:
            if dt.time() not in tl:
                tl.append(dt.time())

    if tl:
        tl.sort()
        day = datetime.date.today()
        t1 = tl[0]
        t2 = tl[1]

        timedelta = datetime.datetime.combine(day,t2)-datetime.datetime.combine(day,t1)

    return tl,timedelta
            
def autotrader(strategy_file="", market_file="",backbars=300, interval=1, maxbars=False,start="",end="",pov=0,tax=0):
    """ autotrader(strategy_file,market_data,backbars)
        A set of script for you to trade any financial product in market
        this is the main script

        autotrader [options] your_strategy_file.py

        OPTIONS:
        
        -m, -market=your_market_file
            the incoming market data stream, now we only work on text file,
            you have to implement this by yourself

        -b, -backbars
            how many back bars you take to caculate, the small the better depend on your strategy
            , impact on performance
        
        -h --help       read the help
        
        -i interval the timer for check the strategy, default 1 second

        --start YYYY-MM-DD tell where to start


        --end YYYY-MM-DD tell where to end
        
        the following is market file format
        read thhe csv file last few lines to process look back data
        
        marrket file format 
        
        YYYY/MM/DD,HH:MM,OPEN,HIGH,LOW,CLOSE,VOLUMN 
        YYYY/MM/DD,OPEN,HIGH,LOW,CLOSE,VOLUMN 
        
        or 
        
        YYYY-MM-DD,OPEN,HIGH,LOW,CLOSE,VOLUMN
    """


    if strategy_file and market_file:
        
        print "Exec Strategy File-> ", strategy_file
        # load dataset
        if start or end:
            dataset = csvtolist(market_file,start=start,end=end)
        else:
            dataset = csvtolist(market_file,backbars=backbars)
        
        strategy_source = open(strategy_file).read()
        
        # bind order function
        ORDER = Order()
        BUY=Buy=buy = ORDER.BUY
        SELL=Sell=sell = ORDER.SELL
        EXITLONG=ExitLong=exitlong = ORDER.EXITLONG
        EXITSHORT=ExitShort=exitshort = ORDER.EXITSHORT
        if pov:
            ORDER.pov=pov
        if tax:
            ORDER.tax=tax
        
        if re_paras.search(strategy_source):
            dd = re_paras.search(strategy_source).group()
            exec(dd)
            for k,v in PARAS.items():
                # FIXME it's not secure, but we exec strategy file anyway
                vars()[k]=v

         
        if re_vars.search(strategy_source):
            dd = re_vars.search(strategy_source).group()
            exec(dd)
            for k,v in VARS.items():
                vars()[k]=v
        
        # set time frame
        tl,delta = checktimeframe(dataset)
        
        dl,tl,ol,hl,ll,cl,vl = [],[],[],[],[],[],[]
        
        num = len(dataset)
        for i in range(num):
            # bind order variable
            ORDER.dt = dataset[i][0]
            MARKETPOSITION=MarketPosition=marketposition=MKS = ORDER.market_position
            ENTRYPRICE=EntryPrice=entryprice = ORDER.entry_price
            
            # load record
            dl,tl,ol,hl,ll,cl,vl = General_Row(dl,tl,ol,hl,ll,cl,vl,dataset[i],length=backbars)
            # 
            DATE = Date=dl
            TIME = Time=tl
            OPEN = Open = O =ol
            HIGH = High = H =hl
            LOW  = Low  = L =ll
            CLOSE= Close= C =cl
            VOLUME=Volume=V = vl
            # not exception catch, any error in strategy file we stop
            exec(strategy_source)

       
        # after looping all history we taken, 
        if start or end:  
            ORDER.REPORT()
        
        # FIXME implement scanning to ticket changing and fire strategy
        #while True:
            #execfile(strategy_file)
            #exec(open(strategy_file).read())
            
            #exec(strategy_source)
            #time.sleep(interval)

    
            

if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], "ahti:m:b:", 
                 ["all","help","test","market=","back=","start=","end=","pov=","tax="])
    
    if len(args) > 0:
        strategy = args[0]
        market = ""
        backbars = 300
        maxbars=False
        test= False
        interval = 1
        start = 0
        end = 0
        pov = 0
        tax = 0
        for o, a in opts:
            if o in ("-h", "--help"):
                print autotrader.__doc__
                sys.exit()
            elif o in ("-b", "--backbars"):
                backbars=int(a)
            elif o in ("-a", "--all"):
                maxbars= True
            elif o in ("-m", "--market"):
                market = a
            elif o in ("-i"):
                interval = int(a)
            elif o in ("-t","--test"):
                test=True
            elif o in ("--start"):
                start = a
            elif o in ("--end"):
                end =a
            elif o in ("--pov"):
                print a
                pov =float(a)
            elif o in ("--tax"):
                tax =float(a)

        if (start or end) and strategy and market:  
            # have start or end, will generate report
            print pov,tax
            autotrader(strategy,market,backbars,interval,maxbars,start,end,pov,tax)
        
        elif strategy and market:
            autotrader(strategy,market,backbars,interval,maxbars)
            
    else:
        print autotrader.__doc__
        sys.exit()
