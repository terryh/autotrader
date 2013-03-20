#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Trader to run you trading strategy
"""
import wx
import datetime
import time
import sys
import os
import re
import threading
import argparse
import traceback
import random
#import getopt
#import multiprocessing

from cStringIO import StringIO

#import types

import pytz
import pandas

app_realpath = os.path.realpath(sys.argv[0])
app_dir = os.path.dirname(app_realpath)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from order import Order

#--------------------------------------------------------------------------------
# parameters && variables
re_paras = re.compile("PARAS.?=.?{.*?}", re.DOTALL)
# variables must have default value
re_vars = re.compile("VARS.?=.?{.*?}", re.DOTALL)
#--------------------------------------------------------------------------------

# FIXME, try different way to solve same problem
# chose the best one
# myown, multiprocessing.Process, threading.Thread

#class Trader(object):
#class Trader(multiprocessing.Process):


class Trader(threading.Thread):
    """To update the quote data from quote source file"""

    _csv_fields = ['date', 'time', 'open', 'high', 'low', 'close', 'volumn']

    def __init__(self, quote_now_file, quote_history_file, strategy_file,
                 backtest_history_file="",
                 timezone="",
                 backbars=300,
                 interval=0.3,
                 start_date="",
                 end_date="",
                 pov=0,
                 tax=0,
                 app_dir='../'):

        #------- threading need this ------------
        threading.Thread.__init__(self)
        self.setDaemon(1)       # die while parent killed
        #----------------------------------------

        self.mtimezone = ''     # market time zone info

        self.strategy_file = strategy_file
        self.strategy_source = ""
        self.compiled_code = ""  # store compiled code

        self.start_date = start_date
        self.end_date = end_date

        self.pov = pov            # Point of value
        self.tax = tax

        self.status = 0         # o stop, 1 running

        self.backbars = backbars
        self.interval = interval

        self.quote_now_file = quote_now_file
        self.quote_history_file = quote_history_file

        self.tz = ''            # timezone obj

        self.date_spliter = '/'  # default date string spliter

        self.base_duration = 60  # seconds

        self.mapping_fields = []  # for pandas.io.parsers.read_csv

        if timezone:  # timezone  FIXME seems don't need
            self.mtimezone = timezone
            self.tz = pytz.timezone(self.mtimezone)
        #----------------------------------------------------------------------
        # share object with main process
        # use pandas DataFrame as base structure https://github.com/pydata/pandas
        # csv file 'date','time', 'open','high','low','close','volumn'
        # DateFrame 'date_time', 'open','high','low','close','volumn'
        self.dataframe = None
        self.ORDER = None
        # maybe don't need
        self.dtl = None
        self.dl = None
        self.tl = None
        self.ol = None
        self.hl = None
        self.ll = None
        self.cl = None
        self.vl = None
        #----------------------------------------------------------------------

    def check_strategy(self):
        """check strategy_source, try to compile to python byte code
        """
        source = ""
        message = ""
        code = ""
        if self.strategy_file and os.path.isfile(self.strategy_file):
            source = open(self.strategy_file).read()
        else:
            message += "file `%s` not found" % (self.strategy_file)

        if source:
            try:
                code = compile(source, '<string>', 'exec')
            except:
                # compile error
                # TODO
                message = traceback.format_exc()
                message = message.strip()

            if message:
                # TODO echo this and log this
                return message
            else:
                self.compiled_code = code
                self.strategy_source = source
        return message

    def update_data(self):
        """
        update history file data after run, use during trading
        """

        #t1 = time.time()
        if self.quote_history_file and os.path.isfile(self.quote_history_file):
            fp = open(self.quote_history_file, "rb")

            content = fp.read()
            if self.quote_now_file and os.path.isfile(self.quote_now_file):
                line = open(self.quote_now_file, "rb").read()
                content += line

            if self.mapping_fields:
                backbars_content = content = '\n'.join(content.splitlines(
                )[-self.backbars:])  # alwayse take same line data

                dataframe = pandas.io.parsers.read_csv(StringIO(backbars_content), names=self.mapping_fields, parse_dates=[[0, 1]])
                # assign the value to self.dataframe
                dl = dataframe.date_time.tolist()
                for idx, v in enumerate(dl):
                    self.dataframe.date_time.set_value(idx, v)

                dl = dataframe.open.tolist()
                for idx, v in enumerate(dl):
                    self.dataframe.open.set_value(idx, v)

                dl = dataframe.high.tolist()
                for idx, v in enumerate(dl):
                    self.dataframe.high.set_value(idx, v)

                dl = dataframe.low.tolist()
                for idx, v in enumerate(dl):
                    self.dataframe.low.set_value(idx, v)

                dl = dataframe.close.tolist()
                for idx, v in enumerate(dl):
                    self.dataframe.close.set_value(idx, v)

                dl = dataframe.volumn.tolist()
                for idx, v in enumerate(dl):
                    self.dataframe.volumn.set_value(idx, v)

                del dataframe

            fp.close()
            del(fp)
            del(content)
        #print "time fro update date",time.time() - t1

    # TODO remove the following block, replace by self.update_data
    def reload_read_data(self):
        """
        request history file data after run, use during trading
        """
        if self.quote_history_file and os.path.isfile(self.quote_history_file):
            fp = open(self.quote_history_file, "rb")

            content = fp.read()
            if os.path.isfile(self.quote_now_file):
                line = open(self.quote_now_file, "rb").read()
                content += line

            if self.mapping_fields:
                backbars_content = content = '\n'.join(content.splitlines(
                )[-self.backbars:])  # alwayse take same line data
                self.dataframe = pandas.io.parsers.read_csv(StringIO(backbars_content), names=self.mapping_fields, parse_dates=[[0, 1]])

            fp.close()
            del(fp)
            del(content)

    def normalize_date(self):

        if self.date_spliter == '-':
            if self.start_date:
                self.start_date = self.start_date.replace('/', '-')
            if self.end_date:
                self.end_date = self.end_date.replace('/', '-')
        elif self.date_spliter == '/':
            if self.start_date:
                self.start_date = self.start_date.replace('-', '/')
            if self.end_date:
                self.end_date = self.end_date.replace('-', '/')

    def clean_date_with_zero(self, date_string):
        return self.date_spliter.join(map(lambda x: "%02d" % int(x), date_string.split(self.date_spliter)))

    def clean_date_without_zero(self, date_string):
        return self.date_spliter.join(map(lambda x: "%d" % int(x), date_string.split(self.date_spliter)))

    def read_data(self):
        """
        prepare data before run
        """
        if self.quote_history_file and os.path.isfile(self.quote_history_file):
            fp = open(self.quote_history_file, "rb")
            content = fp.read()
            si = -1  # start point index
            ei = -1

            # setup date spliter, default is '/'
            prefix = content[:10]
            if '-' in prefix:
                self.date_spliter = '-'

            # get start end date string normalize
            self.normalize_date()

            # check for start or end
            if self.start_date:
                date_string = self.clean_date_with_zero(self.start_date)
                si = content.find(date_string)
                if si < 0:
                    #not founf, let's try without zero date
                    date_string = self.clean_date_without_zero(self.start_date)
                    si = content.find(date_string)

            if self.end_date:
                date_string = self.clean_date_with_zero(self.end_date)
                ei = content.rfind(date_string)
                if ei < 0:
                    #not founf, let's try without zero date
                    date_string = self.clean_date_without_zero(self.end_date)
                    ei = content.rfind(date_string)

            # prepare the buffer
            if si > 0 and ei > 0:
                # have both start and end date
                content = content[si:ei]
            elif si > 0:
                # have start date
                content = content[si:]
            elif ei > 0:
                # have end date
                content = content[:ei]
            elif self.quote_now_file:
                # have current quote file, should go to running strategy
                # only take needed lines
                #content = content.splitlines()[-self.backbars:].join('\n')
                content = '\n'.join(content.splitlines()[-self.backbars:])

            if content:
                mapping_fields = self._csv_fields
                # safe format check
                # format should like this 'date','time', 'open','high','low','close','volumn'
                line = content[:content.find('\n')]
                fields = line.strip().split(',')
                if len(fields) > len(self._csv_fields):
                    # FIXME csv have more field than we want, not handle short columns yet
                    fill_length = len(fields) - len(self._csv_fields)
                    mapping_fields = self._csv_fields + \
                        ['nan%s' % i for i in range(fill_length)]

                self.mapping_fields = mapping_fields
                self.dataframe = pandas.io.parsers.read_csv(StringIO(
                    content), names=mapping_fields, parse_dates=[[0, 1]])

            fp.close()
            del(fp)
            del(content)

    def run(self):
        """
        execute the strategy main loop
        """
        #print 'RUN' , self.status
        self.check_strategy()
        self.read_data()
        minute = datetime.datetime.now(
        ).strftime('%M')  # one minute poor man timmer

        # populate locals for variables
        # bind order function

        self.ORDER = ORDER = Order()
        BUY = Buy = buy = ORDER.BUY
        SELL = Sell = sell = ORDER.SELL
        EXITLONG = ExitLong = exitlong = ORDER.EXITLONG
        EXITSHORT = ExitShort = exitshort = ORDER.EXITSHORT

        if self.pov:
            ORDER.pov = self.pov
        if self.tax:
            ORDER.tax = self.tax

        if re_paras.search(self.strategy_source):
            dd = re_paras.search(self.strategy_source).group()
            PARAS = {}
            # run PARAS
            exec(dd)
            for k, v in PARAS.items():
                locals()[k] = v

        if re_vars.search(self.strategy_source):
            dd = re_vars.search(self.strategy_source).group()
            VARS = {}
            # run VARS
            exec(dd)
            for k, v in VARS.items():
                locals()[k] = v

        # loop back history
        #dl,tl,ol,hl,ll,cl,vl = [],[],[],[],[],[],[]
        rows_number = len(self.dataframe)
        backbars = self.backbars  # save typing
        #t1 = time.time()
        if rows_number > backbars:
            for i in range(backbars, rows_number):
                # bind order variable
                ORDER.dt = self.dataframe.date_time[i]
                MARKETPOSITION = MarketPosition = marketposition = MKS = ORDER.market_position
                ENTRYPRICE = EntryPrice = entryprice = ORDER.entry_price

                dtl = self.dataframe.date_time.values[i - backbars:i]

                # TODO speed killer if we do datetime convert
                #dl = []
                #tl = []
                #for item in dtl:
                    ##dl.append(int(item.date().strftime("%Y%m%d")))
                    ##tl.append(int(item.time().strftime("%H%M%S")))
                    #dl.append(item.date())
                    #tl.append(item.time())

                ol = self.dataframe.open.values[i - backbars:i]
                hl = self.dataframe.high.values[i - backbars:i]
                ll = self.dataframe.low.values[i - backbars:i]
                cl = self.dataframe.close.values[i - backbars:i]
                vl = self.dataframe.volumn.values[i - backbars:i]
                #print i, type(vl)
                # pupulate locals()
                #DATE = Date = dl
                #TIME = Time = tl
                DATETIME = DateTime = DT = dtl
                OPEN = Open = O = ol
                HIGH = High = H = hl
                LOW = Low = L = ll
                CLOSE = Close = C = cl
                VOLUME = Volume = V = vl
                if i >= self.backbars:
                    exec(self.compiled_code)

            #print time.time() - t1
            if self.start_date or self.end_date or not self.quote_now_file:
                # reurn string for output
                return ORDER.REPORT()

        ## clear now data
        #self.reload_read_data() # load data
        self.update_data()  # load data
        self.status = 1

        if self.quote_now_file:

            while self.status:

                t1 = time.time()

                MARKETPOSITION = MarketPosition = marketposition = MKS = ORDER.market_position
                ENTRYPRICE = EntryPrice = entryprice = ORDER.entry_price

                CURRENT_BAR, OO, HH, LL, CC, VV = self.quote()
                if CURRENT_BAR:
                    ORDER.current_dt = CURRENT_BAR
                    # update last ticket
                    last_valid_index = self.dataframe.last_valid_index()
                    self.dataframe.open[last_valid_index] = OO
                    self.dataframe.high[last_valid_index] = HH
                    self.dataframe.low[last_valid_index] = LL
                    self.dataframe.close[last_valid_index] = CC
                    self.dataframe.volumn[last_valid_index] = VV

                    #self.dataframe.volumn[last_valid_index] = random.randrange(300,3000)
                    #print "Latest V ",VV, type(VV), last_valid_index, random.randrange(300,5000)

                    # pull triggrt to update date
                    #print CURRENT_BAR, self.dataframe.date_time[last_valid_index], last_valid_index
                    if CURRENT_BAR != self.dataframe.date_time[last_valid_index]:
                        self.update_data()

                ## populate locals(), datetime python value should nerver change by trading program
                ## share data via numpy array mapping
                self.dtl = DATETIME = DateTime = DT = dtl = self.dataframe.date_time.values[-backbars:]
                #self.dl = DATE = Date = dl = map(lambda d: int(d.date().strftime("%Y%m%d")), dtl)
                #self.tl = TIME = Time = tl = map(lambda d: int(d.time().strftime("%H%M%S")), dtl)
                self.ol = OPEN = Open = O = ol = self.dataframe.open.values[
                    -backbars:]
                self.hl = HIGH = High = H = hl = self.dataframe.high.values[
                    -backbars:]
                self.ll = LOW = Low = L = ll = self.dataframe.low.values[
                    -backbars:]
                self.cl = CLOSE = Close = C = cl = self.dataframe.close.values[
                    -backbars:]
                self.vl = VOLUME = Volume = V = vl = self.dataframe.volumn.values[-backbars:]
                exec(self.compiled_code)
                #print time.time() - t1
                #print self.dataframe.date_time.values[-1]
                #print self.dataframe.volumn.values[-1]
                #print CURRENT_BAR, VV
                time.sleep(self.interval)

    def quote(self):
        """ Read current bar %Y/%m/%d,%H:%M,Open,High,Low,Close,Volume
        """
        CURRENT_BAR = ''
        Open = 0
        High = 0
        Low = 0
        Close = 0
        Volume = 0
        cast = lambda s: '.' in s and float(s) or int(s)

        try:
            line = open(self.quote_now_file).read()
            l = line.split(',')[:7]
            price = l[2:]
            price = map(cast, price)
            dt_string = "%s %s" % (l[0], l[1])
            dt = datetime.datetime.strptime(
                dt_string, '%Y/%m/%d %H:%M')  # FIXME able to support %Y-%m-%d
            Open = price[0]
            High = price[1]
            Low = price[2]
            Close = price[3]
            Volume = price[4]
            return dt, Open, High, Low, Close, Volume
        except:
            return CURRENT_BAR, Open, High, Low, Close, Volume

    def stop(self):
        """
        stop this quote writer
        """
        self.status = 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser("""
    Start to running the trading strategy with some configuration.
    """)
    parser.add_argument('-f', '--file',
                        help="The strategy file gona to run.")

    parser.add_argument('-q', '--quote',
                        help="The quote file to get latest price update.")

    parser.add_argument('-his', '--history',
                        help="The history file to get history OHLC value.")

    parser.add_argument('-test', '--backtest',
                        help="The back test history file.")

    parser.add_argument('-s', '--start',
                        help="Do back testing from date `start` to last day or `end`")

    parser.add_argument('-e', '--end',
                        help="Do back testing from first date or `start` to `end`.")

    parser.add_argument('-b', '--backbars', type=int, default=200,
                        help="How many backbars your strategy need. (  default is 200 )")

    parser.add_argument('-pv', '--pov', type=float, default=0,
                        help="Point of value.")

    parser.add_argument('-tx', '--tax', type=float, default=0,
                        help="Tax or comission for each order.")

    parser.add_argument('-i', '--interval', type=float, default=1,
                        help="The interval in second to check and run this strategy file. (default is 0.3 second )")

    parser.add_argument('-g', '--gui', action="store_true",
                        help="Show the graphi interface")

    args = parser.parse_args()
    #def __init__(self, quote_now_file, quote_history_file, strategy_file,
                    #timezone="",
                    #backbars=300,
                    #interval=0.3,
                    #start="",
                    #end="",
                    #pov=0,
                    #tax=0,
                    #app_dir= '../'):
    timezone = ''
    if args.file:
        t = Trader(args.quote,
                   args.history,
                   args.file,
                   args.backtest,
                   timezone,
                   args.backbars,
                   args.interval,
                   args.start,
                   args.end,
                   args.pov,
                   args.tax,
                   app_dir)
        #t.run()
        if args.gui and args.quote:
            # show gui in main process as main loop only having current quote file
            # wait the thread to prepare data
            t.start()
            while t.status == 0:
                time.sleep(3)
            #print t.__dict__.keys()
            #print t.dataframe
            from pricechart import Trait
            gui = Trait(t.dataframe)
            gui.configure_traits()
            #gui.title = u"阿賢"
        elif args.quote:
            # only stay in terminal
            t.start()
            while t.is_alive():
                # dummy main loop, take break
                time.sleep(2)
        elif args.start or args.end:
            # back testing
            results = t.run()
            print results
        elif args.file:
            # at least have strategy file, let's validate it
            print t.check_strategy()
            #print t.strategy_source()
            #print  ""
