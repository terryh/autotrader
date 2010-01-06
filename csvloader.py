#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A tool load stock history data from csv file 
Author: TerryH, email: terryh.tp@gmail.com, 
Thu, 31 Dec 2009 16:10:01 +0800
License: BSD
"""

__version__ = '0.0.1'
__author__ = 'TerryH'

import datetime
import sys
import getopt
import decimal
import string

def csvtolist(filename="",backbars=300,maxbars=False,start="",end=""):
    """ csvtolist(filename="",backbars=300,maxbars=False,start="",end="")
        
        A tool load stock history data from csv file 
        
        filename
            the filename you want to process
        backbars
            how many back bars you take to caculate
        
        you also can test the result from command line 
        
        csvtolist.py --back=number csvfile.csv
        
        -h --help       read the help
        
        -b --backbars   the number back bars you want to caculate

        read thhe csv file last few lines to process look back data
        the format we prefer
        YYYY/MM/DD,HH:MM,OPEN,HIGH,LOW,CLOSE,VOLUMN 
        YYYY/MM/DD,OPEN,HIGH,LOW,CLOSE,VOLUMN 
        or 
        YYYY-MM-DD,OPEN,HIGH,LOW,CLOSE,VOLUMN
    """


    if filename:
        fp = open(filename,"r+")
        lines = fp.readlines()
        sdate = ""
        edate = ""
        si = -1
        ei = -1
        maxloop = 0
        date_split = "/"
        # skip the first line for safe
        if lines[1].split(",")>=6:
            # prepare the return list
            dl = []
            if maxbars == True:
                # do nothing
                pass

            elif start or end:
                if len(lines)>2:
                    # a simple test for this file more than two row
                    oneline = lines[1] # take second line for process
                    if "/" in oneline:
                        date_split="/"
                    elif "-" in ll[0]:
                        date_split="-"
                content = "".join(lines) # the file splitlines include \r or \n
                if start:
                    sdate = start.split("-") 
                    sdate = map(int,sdate)
                    sdate = datetime.datetime(sdate[0],sdate[1],sdate[2])
                    while si<0 and maxloop<10:
                        sds = sdate.strftime("%Y-%m-%d")
                        sds = sds.replace("-",date_split)
                        si = content.find(sds)
                        sdate = sdate + datetime.timedelta(days=1)
                        maxloop +=1

                if end:
                    edate = end.split("-") 
                    edate = map(int,edate)
                    edate = datetime.datetime(edate[0],edate[1],edate[2])+ datetime.timedelta(days=1)# delay one day
                    print edate
                    while ei<00 and maxloop<10:
                        eds = edate.strftime("%Y-%m-%d")
                        eds = eds.replace("-",date_split)
                        ei = content.find(eds)
                        edate = edate + datetime.timedelta(days=1)
                        maxloop +=1
                
                if si >0 and ei>0:
                    lines = content[si:ei].splitlines() # this will strip \r or \n
                elif si>0:
                    lines = content[si:].splitlines()
                elif ei>0:
                    lines = content[:ei].splitlines()

            else:
                lines = lines[-backbars:]
            print si,ei
            for line in lines:
                ll = line.split(",")  
                ll = map(string.strip,ll)
                # blanket first value
                date = []
                o = 0
                h = 0
                l = 0
                c = 0
                v = 0
                hh = 0
                mm = 0
                ss = 0

                if "/" in ll[0]:
                    date = ll[0].split("/") 
                    date = map(int,date)
                elif "-" in ll[0]:
                    date = ll[0].split("-") 
                    date = map(int,date)
            
                if len(ll)==6:
                    # have no HH:MM:SS
                    #o,h,l,c,v = map(decimal.Decimal,ll[1:])
                    o,h,l,c,v = map(float,ll[1:])
                
                elif len(ll)>6:
                    # having time 
                    t = ll[1].split(':')
                    t = map(int,t)
                    hh = t[0]
                    mm = t[1]
                    if len(t)==3:
                        ss = t[2]
                    else:
                        ss = 0
                    
                    #o,h,l,c,v = map(decimal.Decimal,ll[2:7])
                    o,h,l,c,v = map(float,ll[2:7])
                
                if hh:
                    dt = datetime.datetime(date[0],date[1],date[2],hh,mm,ss)
                else:
                    dt = datetime.datetime(date[0],date[1],date[2])
                
                dl.append([dt,o,h,l,c,v])

        return dl

if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], "ahb:", ["all","help", "backbars=","start=","end="])
    if len(args) > 0:
        start=0
        end=0
        for o, a in opts:
            if o in ("-h", "--help"):
                print csvtolist.__doc__
                sys.exit()
            elif o in ("-b", "--backbars"):
                import pprint
                pprint.pprint(csvtolist(args[0],int(a)))
                #print csvtolist(args[0],int(a))
                #import timeit
                #tt = timeit.Timer("csvtolist(%s,%d)"%(args[0],int(a)),"from __main__ import csvtolist")
                #print "Run csvtolist once take ",tt.timeit(100)/100
            elif o in ("-a", "--all"):
                print csvtolist(args[0],maxbars=True)
            elif o in ("--start"):
                start = a
            elif o in ("--end"):
                end = a
        
        if start or end:
            print csvtolist(args[0],start=start,end=end)
            
    else:
        print csvtolist.__doc__
        sys.exit()
