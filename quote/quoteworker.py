#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import os
import argparse
import getopt
import types
import re
import types
import imp
import multiprocessing
import multiprocessing.forking

# third party module
import pytz
from configobj import ConfigObj


def main_is_frozen():
    return (hasattr(sys, "frozen") or  # new py2exe
            hasattr(sys, "importers")  # old py2exe
            or imp.is_frozen("__main__"))  # tools/freeze


def get_main_dir():
    if main_is_frozen():
        # executable at app/
        return os.path.dirname(sys.executable)
    # app/quote/quoteworker.py
    quote_realpath = os.path.realpath(sys.argv[0])
    app_dir = os.path.dirname(os.path.dirname(quote_realpath))
    return app_dir

# add parent folder to sys path
app_dir = get_main_dir()
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from csvloader import csvtolist

# our own function
#from utils import get_now, get_tz_hhmm


def get_now(timezone=''):
    #            self.tz = tz
    if timezone:
        tz = pytz.timezone(timezone)
        now = datetime.datetime.now(tz=tz)
    else:
        now = datetime.datetime.now()
    return now


def get_tz_hhmm(hour, minute, timezone=''):

    if timezone:
        # timezone
        tz = pytz.timezone(timezone)
        dt = datetime.datetime.now(
            tz=tz).replace(hour=hour, minute=minute, second=0, microsecond=0)
    else:
        dt = datetime.datetime.now().replace(second=0, microsecond=0)
        dt.replace(hour=hour, minute=minute)
    return dt

######################################################
# work around for pyinstaller


class _Popen(multiprocessing.forking.Popen):
    def __init__(self, *args, **kw):
        if hasattr(sys, 'frozen'):
            # We have to set original _MEIPASS2 value from sys._MEIPASS
            # to get --onefile mode working.
            # Last character is stripped in C-loader. We have to add
            # '/' or '\\' at the end.
            os.putenv('_MEIPASS2', sys._MEIPASS + os.sep)
        try:
            super(_Popen, self).__init__(*args, **kw)
        finally:
            if hasattr(sys, 'frozen'):
                # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                # available. In those cases we cannot delete the variable
                # but only set it to the empty string. The bootloader
                # can handle this case.
                if hasattr(os, 'unsetenv'):
                    os.unsetenv('_MEIPASS2')
                else:
                    os.putenv('_MEIPASS2', '')


class Process(multiprocessing.Process):
    _Popen = _Popen


def quote_update(source_file=""):
    """We have file quote support only, source_file format , python  list string [datetime.time,price,volume]
       [HH:MM:SS,price,totalvolume]
    """
    q_l = []
    try:
        return eval(open(source_file).read())
    except:
        return q_l


#class QuoteWriter(Process): # for use under pyinstaller one execuable pack
#class QuoteWriter(multiprocessing.Process):
class QuoteWriter(object):
    """To update the quote data from quote source file"""
    #def __init__(self, **kwargs):
    def __init__(self, market_ini, commodity_ini, commodity, interval=0.3, app_dir=''):
        #multiprocessing.Process.__init__(self)

        # Done in def main
        if not app_dir:
            #app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            app_dir = get_main_dir()

        self.quote_type = {}    # a dict for quote config
        self.mtimezone = ''     # time zone info
        self.mclear = ''        # market clear time
        self.s1_start = ''      # session 1 start time
        self.s1_end = ''        # session 1 end time
        self.s2_start = ''      # session 2 start time
        self.s2_end = ''        # session 2 end time
        self.status = 0         # o stop, 1 running
        self.interval = interval
        self.output_file = ''
        self.quote_dir = ''
        self.data_dir = ''
        self.time_tickets = []
        self.time_tickets_length = 0
        self.ticket_index = 0
        self.quote_data = []
            # quote_data [[datatime, open, high, low, close, volume]...]
        self.quote_current = []  # quote_current store min1 current value [datatime, open, high, low, close, volume].
        self.quote_source_file = ''  # we hard code in quote interface always call `commodity`.now
        self.quote_file = {}
            # historty quote csv file open with append store file handler
        self.quote_file_current = {}    # for quote current value open with overwrite store file name not file handler
        self.tz = ''            # timezone obj
        self.base_duration = 60  # seconds

        if market_ini and commodity_ini:
            mobj = ConfigObj(market_ini, encoding='utf-8')
            cobj = ConfigObj(commodity_ini, encoding='utf-8')
            mcode = cobj[commodity]['mcode']
            ccode = commodity

            if cobj[commodity].get('cdir', False):
                self.quote_dir = os.path.join(
                    cobj[commodity].get('cdir'), 'data', mcode, ccode)
            else:
                self.quote_dir = os.path.join(app_dir, 'data', mcode, ccode)

            self.data_dir = os.path.join(app_dir, 'data', mcode, ccode)

            if self.quote_dir and not os.path.isdir(self.quote_dir):
                os.makedirs(self.quote_dir)
            if self.data_dir and not os.path.isdir(self.data_dir):
                os.makedirs(self.data_dir)

            print self.quote_dir
            print self.data_dir

            #self.output_file = get_ohlc_file( ccode , self.quote_dir)
            self.quote_source_file = os.path.join(
                self.quote_dir, ccode + ".now")

            #print "OutPut file", self.output_file

            for k, v in cobj[commodity]['quote'].items():
                if v == u'True':
                # FIXME , write file
                    minute = 0
                    if k.startswith('min'):
                        minute = int(k.split('min')[1])
                        self.quote_type[k] = int(k.split('min')[1])
                    if k.startswith('hour'):
                        minute = int(k.split('hour')[1]) * 60
                        self.quote_type[k] = int(k.split('hour')[1]) * 60
                    if k == u'day1':
                        minute = 60 * 24
                        self.quote_type[k] = 60 * 24

            # we base on 1 minute
            if 'min1' not in self.quote_type:
                self.quote_type['min1'] = 1

            self.mtimezone = mobj[mcode]['mtimezone']

            if self.mtimezone:  # timezone
                tz = pytz.timezone(self.mtimezone)
                self.tz = tz

            self.mclear = mobj[mcode]['mclear']
            self.s1_start = mobj[mcode]['s1_start']
            self.s1_end = mobj[mcode]['s1_end']
            self.s2_start = mobj[mcode]['s2_start']
            self.s2_end = mobj[mcode]['s2_end']

        #self.start()

    def cook_time_slice(self, session_start, session_end):
        """
        Prepare time slice date for session
        """
        result = []
        s_hour, s_minute = map(int, session_start.split(':')[:2])
        e_hour, e_minute = map(int, session_end.split(':')[:2])

        # TODO clean up
        if self.tz:
            # timezone
            #start_datetime = datetime.datetime.now(tzinfo=self.tz).replace(second=0, microsecond=0)
            start_datetime = get_tz_hhmm(s_hour, s_minute, self.mtimezone)
            print start_datetime
            if e_hour < s_hour:
                # end next day
                #end_datetime = (datetime.datetime.now(tzinfo=self.tz)+datetime.timedelta(days=1)).replace(second=0, microsecond=0)
                end_datetime = start_datetime + datetime.timedelta(days=1)
            else:
                #end_datetime = datetime.datetime.now(tzinfo=self.tz).replace(second=0, microsecond=0)
                end_datetime = start_datetime

            end_datetime = end_datetime.replace(hour=e_hour, minute=e_minute)
            print "COOK TIME", start_datetime, type(end_datetime), self.tz
        else:
            start_datetime = get_tz_hhmm(s_hour, s_minute)
            start_datetime.replace(hour=s_hour, minute=s_minute)

            if e_hour < s_hour:
                # end next day
                end_datetime = start_datetime + datetime.timedelta(days=1)
            else:
                end_datetime = start_datetime

            end_datetime.replace(hour=e_hour, minute=e_minute)

        dt = start_datetime
        delta = datetime.timedelta(seconds=self.base_duration)

        while dt < end_datetime:
            dt += delta
            result.append(dt)
        if result:
            return result

    def find_ticket(self):
        """find the right index for current ticket
        """
        now = get_now(self.mtimezone)
        i = 0
        market_open = 0
        delta = datetime.timedelta(
            seconds=self.base_duration)  # one minute time frame
        # load history from min1 quote file data
        min1_fn = self.quote_file['min1']
        print min1_fn
        self.quote_data = csvtolist(min1_fn)

        #if now < self.time_tickets[0]-delta:
        #    return i, market_open
        print self.time_tickets[0]
        print self.time_tickets[-1]
        for i in range(len(self.time_tickets)):
            print i, self.time_tickets[i]
            if now < self.time_tickets[i]:
                break
                print "Index ", i
        #return i,market_open
        print "Ticket Index", i, len(self.time_tickets)
        self.ticket_index = i

    def quote(self):
        """We have file quote support only, source_file format , python  list string [datetime.time,price,volume]
           [HH:MM:SS,price,totalvolume]
        """
        q_l = []
        try:
        #print self.quote_source_file
            return eval(open(self.quote_source_file).read())
        except:
            return q_l

    def pre_run(self):
        """
        Clean up data before run, count nessary ticket frame
        """
        if not self.quote_type:
            raise Exception('You need at least one quote_type')

        # session 1
        #print 'Session', self.s1_start, self.s1_end, self.s2_start, self.s2_end
        if self.s1_start != u"00:00" and self.s1_end:  # simple empty check
            tickets = self.cook_time_slice(self.s1_start, self.s1_end)
            if tickets:
                self.time_tickets += tickets
        # session 2
        if self.s2_start != u"00:00" and self.s2_end:  # simple empty check
            tickets = self.cook_time_slice(self.s2_start, self.s2_end)
            if tickets:
                self.time_tickets += tickets

        # open quote csv file and store quote_file_current list
        for k, v in self.quote_type.items():
            self.quote_file[k] = os.path.join(self.data_dir, k + '.csv')
            self.quote_file_current[k] = os.path.join(
                self.quote_dir, k + '.ohlc')

        # save total time_tickets length
        self.time_tickets_length = len(self.time_tickets)

    def write_quote(self):
        for k, v in self.quote_type.items():
            #print k,v, self.ticket_index
            if self.ticket_index % v == 0:  # 0..10.. start from zero, before call write_quote self.ticket_index had plus 1
                # time to write this bar
                # quote_data [[datatime, open, high, low, close, volume]...]
                process_ticket = zip(*self.quote_data[-v:])
                # process_ticket
                ticket_end = process_ticket[0][-1]
                dt = ticket_end.strftime("%Y/%m/%d,%H:%M")
                OO = process_ticket[1][0]
                HH = max(process_ticket[2])
                LL = min(process_ticket[3])
                CC = process_ticket[4][-1]
                VV = sum(process_ticket[5])
                val = "%s,%s,%s,%s,%s" % (
                    str(OO), str(HH), str(LL), str(CC), str(VV))
                line = "%s,%s\n" % (dt, val)
                fp = open(self.quote_file[k], 'a')  # append history file
                fp.write(line)
                fp.close()

    def write_current(self):
        print "write current..."
        for k, v in self.quote_type.items():
            #print k,v
            # min1 had wrote at def run
            #dt = self.quote_current[0].strftime("%Y/%m/%d,%H:%M")
            last_ticket = False
            if self.ticket_index < self.time_tickets_length:
                dt = self.time_tickets[
                    self.ticket_index].strftime("%Y/%m/%d,%H:%M")
            else:
                # last one ticket and had write the ticket
                # just use the last time_tickets
                dt = self.time_tickets[-1]
                last_ticket = True

            OO, HH, LL, CC, VV = self.quote_current[1:]
                # skip current ticket time

            if k == 'min1':
                # min1 base data
                if VV:
                    # dummy check at lease not None, no volumne no price
                    val = "%s,%s,%s,%s,%s" % (
                        str(OO), str(HH), str(LL), str(CC), str(VV))
                    line = "%s,%s" % (dt, val)
                    fp = open(self.quote_file_current[k], 'w')
                    fp.write(line)
                    fp.close()
            else:
                # longer than 1 minute
                # quote_data [[datatime, open, high, low, close, volume]...]
                # self.ticket_index 0 1 2 3 4 5 6 ....
                # self.quote_data[[0...], [1...], [2...], [3...], [4...], [5...]] + self.quote_current[6...] ...

                remainder = (self.ticket_index + 1) % v   # ticket_index 0..10...  (ticket_index + 1) % v ==0 on close bar minute
                print "remainer ", k, v, remainder

                if remainder == 0:
                    # closing time frame for this bar
                    process_data = self.quote_data[-(v - 1):]
                    process_data.append(self.quote_current)
                else:
                    # not closing time frame, and need to write current dt
                    if remainder > 1:
                        process_data = self.quote_data[-(remainder - 1):]
                    else:
                        process_data = []
                    process_data.append(self.quote_current)

                    if not last_ticket:
                        ticket_end = self.time_tickets[self.ticket_index]
                        seconds_delta = self.base_duration * (v - remainder)
                        ticket_end_current = ticket_end + \
                            datetime.timedelta(seconds=seconds_delta)
                        dt = ticket_end_current.strftime("%Y/%m/%d,%H:%M")

                    #dt = ticket_end_current.strftime("%Y/%m/%d,%H:%M")

                # TODO write correct dt
                process_ticket = zip(*process_data)
                # process_ticket
                OO = process_ticket[1][0]
                HH = max(process_ticket[2])
                LL = min(process_ticket[3])
                CC = process_ticket[4][-1]
                VV = sum(process_ticket[5])
                val = "%s,%s,%s,%s,%s" % (
                    str(OO), str(HH), str(LL), str(CC), str(VV))
                line = "%s,%s" % (dt, val)
                fp = open(self.quote_file_current[k], 'w')
                fp.write(line)
                fp.close()

    def run(self):
        """
        run this quote writer, to keep update quote files
        """
        # FIXME, use mmap to look up source file, time zone support
        self.status = 1
        self.pre_run()
        self.find_ticket()
        print "QT PRE", self.time_tickets[0]
        qt_pre = self.time_tickets[0] - datetime.timedelta(
            days=1)  # previous quotetime set an older default value

        ticket_index_pre = 0  # previous ticket index
        close_pre = 0  # previous close price
        volume_pre = 0  # previous bar total volume

        # in case our time is slow that market, plus 5 seconds
        safe_seconds = datetime.timedelta(seconds=5)
        lastticket_end = self.time_tickets[-1] + safe_seconds
        print 'RUN', self.status
        import pprint
        # init quote None value before market start
        OO = None
        HH = None
        LL = None
        CC = None
        VV = None
        print pprint.pprint(self.time_tickets[0])
        print pprint.pprint(self.time_tickets[-1])
        print self.ticket_index
        print lastticket_end
        while self.status:
            now = get_now(self.mtimezone)
            #try:
            #print  self.ticket_index < len(self.time_tickets) and now < lastticket_end
            if self.ticket_index < len(self.time_tickets) and now < lastticket_end:
                    # start ticket
                ticket_end = self.time_tickets[self.ticket_index]
                ticket_start = ticket_end - \
                    datetime.timedelta(seconds=self.base_duration)
                # if our time is slow or fast for few seconds, let's say 5 seonds
                if self.ticket_index == 0:
                    ticket_start = ticket_start - safe_seconds

                quote_list = self.quote()
                # print quote_list
                # start a ticket
                if quote_list:
                    ql = quote_list
                    # convert ticket time to datetime
                    #print "QL",ql
                    #qt = datetime.datetime.combine(now.date(),ql[0])
                    quote_time = ql[0]
                    #print ql.micro
                    # casting to timezone awareness
                    qt = now.replace(hour=quote_time.hour, minute=quote_time.minute, second=quote_time.second, microsecond=quote_time.microsecond)

                    #print "QT", qt, ticket_start, now
                    if (qt_pre < ticket_start and qt >= ticket_start) or ticket_index_pre != self.ticket_index:
                        # this bar first ticket
                        ticket_index_pre = self.ticket_index  # record the ticket index, until exit this ticket, we will enter again
                        OO = ql[1]
                        HH = ql[1]
                        LL = ql[1]
                        CC = ql[1]
                        VV = ql[2] - volume_pre

                    elif qt >= ticket_start and qt < ticket_end:
                        if not OO:
                            # first time, qmpty value just in case
                            OO = HH = LL = CC = ql[1]
                        # change HH, LL
                        if ql[1] > HH:
                            HH = ql[1]
                        if ql[1] < LL:
                            LL = ql[1]
                        CC = ql[1]
                        VV = ql[2] - volume_pre
                        print ql[0], OO, HH, LL, CC, VV,
                        print "\r",  # a trick to keep cursor at same line

                    dt = ticket_end.strftime("%Y/%m/%d,%H:%M")
                    val = "%s,%s,%s,%s,%s" % (
                        str(OO), str(HH), str(LL), str(CC), str(VV))
                    line = "%s,%s" % (dt, val)

                    if now >= ticket_end:
                        # close a ticket
                        print line

                        self.quote_data.append([ticket_end, OO, HH, LL, CC, VV])     # push values to quote_data
                        self.ticket_index += 1                                      # increse ti ticket index start from 0
                        volume_pre = ql[2]
                            # reset volume counter

                        # start write other quote_type, self.ticket_index start from , the min1 csv had wrote
                        # and ticket_index update to next example 0, 1, 2, 3, 4 ticket_index plus 1 = 5
                        print 'Write Quote----------'
                        self.write_quote()

                    qt_pre = qt  # remember as previous ticket time

                    # FIXME change to write every quote_file_current
                    self.quote_current = [qt, OO, HH, LL, CC, VV]
                    #print "write current"
                    self.write_current()

            #except:
            #    pass
            time.sleep(self.interval)

    def stop(self):
        """
        stop this quote writer
        """
        self.status = 0


def main(market_ini, commodity_ini, commodity, interval=0.3):

    app_dir = get_main_dir()

    try:
        w = QuoteWriter(
            market_ini, commodity_ini, commodity, interval, app_dir)
        w.start()
    finally:
        w.stop()
        w.terminate()
        # wait for close process
        isalive = 1
        while isalive:
            isalive = 0
            isalive = w.is_alive()


if __name__ == '__main__':
    # command line tool wrapper
    app_dir = get_main_dir()
    parser = argparse.ArgumentParser("""
    A worker process to collect price merge to history file.
    """)

    parser.add_argument('-i', '--interval', type=float, default=0.3,
                        help="The interval in second to check current quote. (default is 0.3 second )")

    parser.add_argument(
        '-c', '--cini', help="The path to commodity configure file.")

    parser.add_argument(
        '-m', '--mini', help="The path to market configure file.")

    parser.add_argument(
        '-com', '--commodity', help="The unique commodity name code.")

    args = parser.parse_args()

    if (args.cini and args.mini and args.commodity and
            os.path.isfile(args.cini) and os.path.isfile(args.mini)):
        p = QuoteWriter(
            args.mini, args.cini, args.commodity, args.interval, app_dir)
        #p.start()
        p.run()
    else:
        print parser.print_help()

#if __name__ == '__main__':
    ## command line tool wrapper
    #opts, args = getopt.getopt(sys.argv[1:], "i:", ["cini=", "mini=","commodity=" ] )
    #app_dir = get_main_dir()
    #if len(opts) > 0:
        #interval      = 1
        #commodity_ini = ''
        #market_ini    = ''
        #commodity     = ''
        #for o, v in opts:
            #if o in ("-i"):
            #interval = float(v)
            #elif o in ("--commodity"):
            #commodity = v
            #elif o in ("--cini"):
            #commodity_ini = v
            #elif o in ("--mini"):
            #market_ini = v
    #if os.path.isfile(commodity_ini) and os.path.isfile(market_ini) and commodity:
        #p = QuoteWriter(market_ini, commodity_ini, commodity, interval, app_dir)
        ##p.start()
        #p.run()
    #else:
        #print __doc__
