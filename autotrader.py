#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A set of script for you to trade any financial product in market
Author: TerryH, email: terryh.tp at gmail.com,
License: BSD
"""

import datetime
import time
import sys
import getopt
import types
import pprint
import re
import types
import threading

try:
    import cPickle as pickle
except:
    import pickle


# our own function
from csvloader import csvtolist 
from order import Order
from function import *

# parameters
re_paras = re.compile("PARAS.?=.?{.*?}",re.DOTALL)
# variables must have default value
re_vars = re.compile("VARS.?=.?{.*?}",re.DOTALL)


def checktimeframe(dataset=[],backbars=300):
    """look for more  than two day, find the time frame for trade, 
       at lease have more thant 2 day item in dataset
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

def find_ticket(timeframe_list=[],delta="", now=""):
    """find the right index for current ticket
    """
    # FIXME leter, we should think about different time zone for trading
    if not now:
        now = datetime.datetime.now()
    
    if timeframe_list and delta:
        tt = now.time()
        i = 0
        market_open = 0
        for i in range(len(timeframe_list)):
            #print i,timeframe_list[i]
            if tt<=timeframe_list[i]:
                market_open = 1
                
                break
        return i,market_open
        

        
            
def autotrader(strategy_file="", market_file="",backbars=300, interval=1, 
               quote=False,maxbars=False, start="",end="",pov=0,tax=0):
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

        --start=YYYY-MM-DD tell where to start


        --end=YYYY-MM-DD tell where to end
        
        the following is market file format
        read thhe csv file last few lines to process look back data
        
        marrket file format 
        
        YYYY/MM/DD,HH:MM,OPEN,HIGH,LOW,CLOSE,VOLUMN 
        YYYY/MM/DD,OPEN,HIGH,LOW,CLOSE,VOLUMN 
        
        or 
        
        YYYY-MM-DD,OPEN,HIGH,LOW,CLOSE,VOLUMN
    """
    global RUN,dataset,OO,HH,LL,CC,VV,dl,tl,ol,hl,ll,cl,vl
    if strategy_file:
        
        print "Exec Strategy File-> ", strategy_file
        
        strategy_source = open(strategy_file).read()
        
        # bind order function
        ORDER = Order()
        BUY = Buy = buy = ORDER.BUY
        SELL = Sell = sell = ORDER.SELL
        EXITLONG = ExitLong = exitlong = ORDER.EXITLONG
        EXITSHORT = ExitShort = exitshort = ORDER.EXITSHORT
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
        
        dl,tl,ol,hl,ll,cl,vl = [],[],[],[],[],[],[]
        
        num = len(dataset)
        for i in range(num):
            # bind order variable
            ORDER.dt = dataset[i][0]
            MARKETPOSITION=MarketPosition=marketposition=MKS = ORDER.market_position
            ENTRYPRICE=EntryPrice=entryprice = ORDER.entry_price
            # load record
            dl,tl,ol,hl,ll,cl,vl = General_Row(dl,tl,ol,hl,ll,cl,vl,dataset[i],length=backbars)
            DATE = Date=dl
            TIME = Time=tl
            OPEN = Open = O =ol
            HIGH = High = H =hl
            LOW  = Low  = L =ll
            CLOSE= Close= C =cl
            VOLUME=Volume=V = vl
            OO = ol[0] 
            HH = hl[0] 
            LL = ll[0] 
            CC = cl[0] 
            VV = vl[0] 
            # not exception catch, any error in strategy file we stop
            exec(strategy_source)
       
        # after looping all history we taken, 
        if start or end:  
            ORDER.REPORT()
            
        while RUN and quote:
            #print datetime.datetime.now(),ORDER,ORDER.market_position, ORDER.dt
            ORDER.dt = dataset[-1][0]
            MARKETPOSITION=MarketPosition=marketposition=MKS = ORDER.market_position
            ENTRYPRICE=EntryPrice=entryprice = ORDER.entry_price
            DATE = Date=dl
            TIME = Time=tl
            OPEN = Open = O =ol
            HIGH = High = H =hl
            LOW  = Low  = L =ll
            CLOSE= Close= C =cl
            VOLUME=Volume=V = vl
            exec(strategy_source)

            time.sleep(interval)

def quote_update(market="",quote=""):
    """We have file quote support only, quote_file format , python pickled list,[datetime.time,price,volume]
       HH:MM:SS,price,totalvolume
    """
    q_l = []
    try:
        return pickle.load(open(quote))
    except:
        return q_l



            
def main(strategies=[],market="",backbars=300,interval=1, \
         quote="",maxbars=False,start="",end="",pov=0,tax=0):
    """If we are going to keep update the market file, and scanning for buy or sell signal
       could have many strategy for one market file
    """
    # share data, only read 
    global RUN, dataset,OO,HH,LL,CC,VV,dl,tl,ol,hl,ll,cl,vl
    RUN = True
    thread_list = []
    # load dataset
    if market:
        if start or end:
            dataset = csvtolist(market,start=start,end=end)
        else:
            dataset = csvtolist(market,backbars=backbars)
        tl = [] # threading list
        if type(strategies) == types.ListType and len(strategies)>0:
            if quote:
                # only have quote input, we use threading
                for s in strategies:
                    t = threading.Thread(target=autotrader,args=(s,market,backbars,interval,True))
                    t.start()
                    thread_list.append(t)
            elif start or end:
                # only parse first strategy , quote = False
                autotrader(strategies[0],market,backbars,interval,False,maxbars,start,end,pov,tax)
            else:
                autotrader(strategies[0],market,backbars,interval,False,maxbars)
        
        if quote:
            # if have quote let's start our MAIN LOOOP

            #print quote
            timeframe_list,delta = checktimeframe(dataset)
            now = datetime.datetime.now()
            ti,market_open = find_ticket(timeframe_list,delta, now)
            if not market_open and ti==len(timeframe_list)-1:
                # market not start yet, start from ti = 0, else condition just use the found ti (ticket index)
                ti = 0
            
            ww = 0 # for test
            pc = 0 # previous close price
            pt = datetime.datetime(1900,1,1) # previous time
            pv = 0 # previous bar total volume
            tip = 0 # previous ticket index
            # in case our time is slow that market, plus 5 seconds
            lastticket_end = datetime.datetime.combine(now.date(),timeframe_list[-1]) + datetime.timedelta(seconds=5)
            #print ti,market_open
            #print timeframe_list,delta 
            try:
 
                while ti<len(timeframe_list) and now <lastticket_end:
                    now = datetime.datetime.now()
                    # start ticket 
                    ticket_time = timeframe_list[ti]
                    ticket_end = datetime.datetime.combine(now.date(),ticket_time)
                    ticket_start = ticket_end-delta
                    quote_list = quote_update(quote=quote)
                    
                    # start a ticket
                    if quote_list:
                        ql = quote_list
                        # convert ticket time to datetime
                        qt = datetime.datetime.combine(now.date(),ql[0])
                        if (pt<ticket_start and qt>=ticket_start) or tip !=ti:
                            # this bar first ticket
                            tip = ti # record the ticket index, until exit this ticket, we will enter again
                            OO = ql[1]
                            HH = ql[1]
                            LL = ql[1]
                            CC = ql[1]
                            VV = ql[2]-pv

                        elif qt>=ticket_start and qt< ticket_end:
                            # change HH, LL
                            if ql[1]>HH: HH = ql[1]
                            if ql[1]<LL: LL = ql[1]
                            CC = ql[1]
                            VV = ql[2]-pv
                            print ql[0],OO,HH,LL,CC,VV,
                            print "\r",# a trick to keep cursor at same line

                        if now>=ticket_end:
                            # close a ticket
                            line = ticket_end.strftime("%Y/%m/%d,%H:%M")
                            pv = ql[2]
                            qline= "%s,%s,%s,%s,%s" % (str(OO),str(HH),str(LL),str(CC),str(VV))
                            fp = file(market,"a")
                            fp.write(line+','+qline+"\n")
                            fp.close()
                            print line+','+qline
                            # increse ti ticket index
                            ti = ti+1
                            # after new ticket, read it again
                            dataset = csvtolist(market,backbars=backbars)
                            dl,tl,ol,hl,ll,cl,vl = General(dataset,length=backbars)
                        
                        pt = qt #remember as previous ticket time 
                    time.sleep(interval)
            
            except KeyboardInterrupt:
        
                RUN = False
                for t in thread_list:
                    t.join()
                print "Finishing all job"
        
        # join all thread, if we have
        if thread_list:
            RUN = False # stop all thread
            for t in thread_list:
                t.join()
            print "Finishing all job"

if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], "ahq:ti:m:b:", 
                 ["all","help","quote=","market=","back=","start=","end=","pov=","tax="])
    
    if len(args) > 0:
        strategy = args[0:]
        market = ""
        backbars = 300
        maxbars=False
        interval = 1
        start = 0
        end = 0
        pov = 0
        tax = 0
        quote = 0
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
            elif o in ("--start"):
                start = a
            elif o in ("--end"):
                end =a
            elif o in ("--pov"):
                pov = float(a)
            elif o in ("--tax"):
                tax =float(a)
            elif o in ("-q","--quote"):
                quote = a

        if (start or end) and strategy and market:  
            # have start or end, will generate report
            main(strategy,market,backbars,interval,quote,maxbars,start,end,pov,tax)
        
        elif strategy and market and quote:
            main(strategy,market,backbars,interval,quote,maxbars)
        elif strategy and market:
            main(strategy,market,backbars,interval,quote,maxbars)
            
    else:
        print autotrader.__doc__
        sys.exit()
