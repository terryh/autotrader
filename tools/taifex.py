#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get history from http://www.taifex.com.tw/chinese/3/3_1_3.asp
merge to K bar csv data
http://www.taifex.com.tw/DailyDownload/Daily_`date +%Y_%m_%d`.zip
"""
import urllib2
import datetime
import zipfile
import csv
import string
import sys
import shutil
import os
import calendar
import imp
from collections import defaultdict

# try python2.7 argparse
import argparse

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


# hack for execable or python script
def main_is_frozen():
    return (hasattr(sys, "frozen") or  # new py2exe
            hasattr(sys, "importers")  # old py2exe
            or imp.is_frozen("__main__"))  # tools/freeze


def get_main_dir():
    if main_is_frozen():
        # executable at app/
        return os.path.dirname(sys.executable)
    # app/tool/taifex.py
    script_realpath = os.path.realpath(sys.argv[0])
    app_dir = os.path.dirname(os.path.dirname(script_realpath))
    return app_dir


app_dir = get_main_dir()
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)


taifex_dir = os.path.join(app_dir, 'taifex')
history_dir = os.path.join(app_dir, 'history')

# parse commodity code
#TX：臺股期貨
#MTX：小型臺指期貨
#TE：電子期貨
#TF：金融期貨

commodity_codes = ['TX', 'MTX', 'TE', 'TF']
START_HOUR = 8
START_MINUTE = 45
history_files = {
    'min1': 1,
    'min3': 3,
    'min5': 5,
    'min15': 15,
    'min30': 30
}

if not os.path.isdir(taifex_dir):
    os.makedirs(taifex_dir)
if not os.path.isdir(history_dir):
    os.makedirs(history_dir)

url_file = "http://www.taifex.com.tw/DailyDownload/Daily_%d_%02d_%02d.zip"
data_file = "Daily_%d_%02d_%02d.zip"


def get_auto_yyyymm(getday=None):
    if not getday:
        getday = datetime.date.today()

    cd = calendar.Calendar()
    contractdate = 0
    cdate = ""
    cal = cd.monthdayscalendar(getday.year, getday.month)

    ########################################
    #[[0,0,1,2,3,4,5]
    #[6,7,8,9,10,11,12]
    #......]
    # contractdate third wednesday every month
    ########################################
    if cal[0][2]:
        # check first week have wednesday, not zero
        contractdate = datetime.date(getday.year, getday.month, cal[2][2])
    else:
        # first week have no wednesday
        contractdate = datetime.date(getday.year, getday.month, cal[3][2])

    if getday <= contractdate:
        cdate = contractdate.strftime("%Y%m")
    else:
        # make sure to cross one month
        cdate = datetime.date(contractdate.year, contractdate.month,
                              1) + datetime.timedelta(days=40)
        cdate = cdate.strftime("%Y%m")
    return cdate


def main(start_date, ym='', download=None, auto=None, final_code=None, directory=None):
    html_end = "</html>"
    today = datetime.date.today()

    global commodity_codes  # assign again in main()

    if start_date:
        try:
            start_date = datetime.datetime.strptime(
                start_date, '%Y%m%d').date()
        except ValueError:
            print 'Sorry, your datetime format is wrong, please use format like YYYYMMDD'
            sys.exit()

    if auto:
        # overwrite
        start_date = (
            datetime.datetime.now() - datetime.timedelta(days=5)).date()
        ym = get_auto_yyyymm(start_date)

    if final_code and final_code in commodity_codes:
        commodity_codes = [final_code]

    #-------------------------------------------------------------------------------
    # generate file names
    # clean old history file, except download FIXME maybe it's not a good decision
    if not download:
        for code in commodity_codes:
            commodity_folder = os.path.join(history_dir, code)
            if not os.path.isdir(commodity_folder):
                os.makedirs(commodity_folder)
            for k, v in history_files.items():
                fn = k + '.csv'
                fn_fullpath = os.path.join(commodity_folder, fn)
                if os.path.isfile(fn_fullpath):
                    print 'Remove File', fn_fullpath
                    os.unlink(fn_fullpath)
    #-------------------------------------------------------------------------------

    # main loop
    #while start_date < today:
    while start_date <= today:
        filename = data_file % (
            start_date.year, start_date.month, start_date.day)
        filename_path = os.path.join(taifex_dir, filename)
        filename_path_holder = filename_path[:-3] + \
            'html'  # replace .zip to .html
        remote_filename = url_file % (
            start_date.year, start_date.month, start_date.day)

        # if auto overwrite
        if auto:
            ym = get_auto_yyyymm(start_date)

        # local check
        if not os.path.isfile(filename_path):
            today_after_market = (start_date == today and datetime.datetime.now().hour > 15)  # market close at 13:45
            not_file_holder_exist = (not os.path.isfile(
                filename_path_holder) and start_date < today)

            if today_after_market or not_file_holder_exist:
                print 'Try Get file', remote_filename
                contents = urllib2.urlopen(remote_filename).read().strip()
                is_html = contents[-len(html_end):] == html_end
                if not is_html:
                    # this is not html page, should be real data
                    print 'Save to', filename_path
                    fp = open(filename_path, 'wb')  # "b" binary mode is a must
                    fp.write(contents)
                    fp.close()  # flush

                # for not today empty data holder
                if start_date != today and is_html:
                    print 'Save to', filename_path_holder
                    fp = open(filename_path_holder, 'wb')
                    fp.write(contents)
                    fp.close()  # flush

        # test locale archive file, start to parse
        if os.path.isfile(filename_path) and not download:
            zfile = zipfile.ZipFile(filename_path, 'r')
            # buffer in Memory
            for fn in zfile.namelist():
                if fn.endswith(".rpt"):
                    reader = csv.reader(StringIO(zfile.read(fn)))
                    # skip header row
                    reader.next()
                    db = defaultdict(list)
                    # 交易日期,商品代號,交割年月,成交時間,成交價格,成交數量(B+S),近月價格,遠月價格,開盤集合競價
                    for row in reader:
                        row = map(string.strip, row)
                        #print row
                        if len(row) < 5:
                            continue

                        try:
                            price = float(row[4])
                            Date = row[0]
                            Code = row[1]
                            Ym = row[2]
                            Time = row[3]
                            Price = price
                            Volume = int(row[5]) / 2  # buy plus sell
                            if Ym == ym and Code in commodity_codes:
                                line = "%s %s,%s,%s" % (
                                    Date, Time, Price, Volume)
                                #sys.exit()
                                db[Code].append(line)

                        except ValueError:
                            print "Some thing wrong with your data !!"
                            sys.exit()

                    for code in commodity_codes:
                    #for code in ['MTX']:
                    #for code in ['TX']:
                    #for code in ['TF']:
                        start_time = datetime.time(START_HOUR, START_MINUTE)
                        start_date_time = datetime.datetime.combine(
                            start_date, start_time)
                        next_close_time = start_date_time + \
                            datetime.timedelta(seconds=60)
                        next_next_time = start_date_time + \
                            datetime.timedelta(seconds=120)
                        min1 = []
                        #print start_date_time
                        #print next_close_time
                        pre_dt = None
                        vv = 0
                        if db[code]:
                            for line in db[code]:
                                dt, price, volume = line.split(',')
                                price = float(price)
                                volume = int(volume)
                                dt = datetime.datetime.strptime(
                                    dt, '%Y%m%d %H%M%S')
                                if not pre_dt:
                                    # very fist ticket
                                    oo = hh = ll = cc = price

                                # this bar
                                if dt >= start_date_time and dt < next_close_time:
                                    if price > hh:
                                        hh = price
                                    if price < ll:
                                        ll = price
                                    cc = price
                                    vv += volume

                                # close this bar, first ticket in next bar
                                if dt >= next_close_time and pre_dt < next_close_time:
                                    # in case dt > next_next_time
                                    if dt >= next_next_time:
                                        while dt >= next_next_time:
                                            line_list = [next_close_time,
                                                         oo, hh, ll, cc, vv]
                                            #print line_list
                                            min1.append(line_list)
                                            start_date_time = next_close_time
                                            next_close_time = start_date_time + \
                                                datetime.timedelta(seconds=60)
                                            next_next_time = start_date_time + datetime.timedelta(seconds=120)
                                            oo = hh = ll = cc = price
                                            vv = 0

                                    # push data line
                                    line_list = [
                                        next_close_time, oo, hh, ll, cc, vv]
                                    #print line_list
                                    min1.append(line_list)
                                    # reset variables
                                    start_date_time = next_close_time
                                    next_close_time = start_date_time + \
                                        datetime.timedelta(seconds=60)
                                    next_next_time = start_date_time + \
                                        datetime.timedelta(seconds=120)
                                    oo = hh = ll = cc = price
                                    vv = volume

                                pre_dt = dt
                            # this last bar never close,
                            if dt == start_date_time:  # last ticket equal the last close time
                                # merge with last_bar
                                last_line = min1[-1]
                                if price > last_line[2]:
                                    last_line[2] = price
                                if price < last_line[3]:
                                    last_line[3] = price
                                last_line[4] = price
                                last_line[5] += volume
                                min1[-1] = last_line
                            else:
                                line_list = [
                                    next_close_time, oo, hh, ll, cc, vv]
                                #print line_list
                                min1.append(line_list)

                        # we had this date's min1 data
                        print code, len(min1)
                        files = {}
                        for k, v in history_files.items():
                            fn = os.path.join(history_dir, code, k + '.csv')
                            files[fn] = v

                        # min1 [[datatime, open, high, low, close, volume]...]
                        for idx, line_list in enumerate(min1):
                            kbar = idx + 1  # K bae index
                            for fn, v in files.items():
                                if v == 1:
                                    dt = line_list[
                                        0].strftime("%Y/%m/%d,%H:%M")
                                    OO, HH, LL, CC, VV = line_list[1:]
                                    line = "%s,%s,%s,%s,%s,%s\n" % (
                                        dt, OO, HH, LL, CC, VV)
                                    fp = open(fn, 'a')  # append history file
                                    fp.write(line)
                                    fp.close()
                                elif kbar % v == 0:
                                    # time to write this bar
                                    process_ticket = min1[kbar - v:kbar]
                                    vstack_ticket = zip(*process_ticket)
                                    ticket_end = vstack_ticket[0][-1]
                                    dt = ticket_end.strftime("%Y/%m/%d,%H:%M")
                                    OO = vstack_ticket[1][0]
                                    HH = max(vstack_ticket[2])
                                    LL = min(vstack_ticket[3])
                                    CC = vstack_ticket[4][-1]
                                    VV = sum(vstack_ticket[5])
                                    line = "%s,%s,%s,%s,%s,%s\n" % (
                                        dt, OO, HH, LL, CC, VV)
                                    fp = open(fn, 'a')  # append history file
                                    fp.write(line)
                                    fp.close()

                        # in case the last ticket not close k bar
                        # maybe last ticket is 13:30 but min30.csv close at ??:15 ??:45
                        for fn, v in files.items():
                            if kbar % v != 0:
                                remain = kbar % v
                                process_ticket = min1[kbar - remain:kbar]
                                vstack_ticket = zip(*process_ticket)
                                ticket_end = vstack_ticket[0][-1]
                                dt = ticket_end.strftime("%Y/%m/%d,%H:%M")
                                OO = vstack_ticket[1][0]
                                HH = max(vstack_ticket[2])
                                LL = min(vstack_ticket[3])
                                CC = vstack_ticket[4][-1]
                                VV = sum(vstack_ticket[5])
                                line = "%s,%s,%s,%s,%s,%s\n" % (
                                    dt, OO, HH, LL, CC, VV)
                                fp = open(fn, 'a')  # append history file
                                fp.write(line)
                                fp.close()

        start_date += datetime.timedelta(days=1)

        # take care copy filem having code and dir
        if directory and final_code in commodity_codes:
            if os.path.isdir(directory):
                for k, v in history_files.items():
                    fn = os.path.join(history_dir, code, k + '.csv')
                    if os.path.isfile(fn):
                        print "Copy file %s to %s" % (fn, directory)
                        shutil.copy(fn, directory)
            else:
                print 'This directory not exist %s' % directory


if __name__ == '__main__':
    # command line tool wrapper
    parser = argparse.ArgumentParser("""
    Get history from http://www.taifex.com.tw/ to cook the 1, 3, 5, 15, 30 minute/s K bar,
    taifex only allow latest 30 days.

    TX  TAIFEX Futures
    MTX Mini-TAIFEX Futures
    TE  Electronic Sector Index Futures
    TF  Finance Sector Index Futures
    """)
    parser.add_argument('-s', '--start', help="Collect data from START date YYYYMMDD to today.")

    parser.add_argument('-ym', '--ym', help="Target trade Year && Month YYYYMM for collect data.")

    parser.add_argument('-d', '--download', action="store_true",
                        help="""Only try to download zip file from taifex.
                            """)

    parser.add_argument('-a', '--auto', action="store_true",
                        help="""Automaticly put the 5 day earlier as --start value, and use date to guest -ym value,
                        this will ignore --start and --ym
                        the last trading day of contract is third wednesday each month in general.
                            """)

    parser.add_argument('-code', '--code',
                        help="""Specific Code the avaliable code are TX, MTX, TE, TF, if you want only pick one.""")

    parser.add_argument('-dir', '--dir',
                        help="""This option must use with -code, the avaliable code are TX, MTX, TE, TF,
                        copy all result of -code Code to the DIR, the filename are
                        min1.csv min3.csv, min5.csv, min15.csv, min30.csv .""")

    args = parser.parse_args()
    if args.start and args.ym or args.auto or (args.download and args.start):
        main(args.start, args.ym, args.download, args.auto,
             args.code, args.dir)
