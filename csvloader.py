#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A tool load stock history data from csv file 
Author: TerryH, email: terryh.tp at gmail.com, 
License: BSD
"""

import datetime
import sys
import getopt
import string
import os
#import mmap

def csvtolist(filename="",backbars=300,maxbars=False,start="",end=""):
    """ csvtolist(filename="",backbars=300,maxbars=False,start="",end="")
        
        A tool load stock history data from csv file 
        
        filename
            the filename you want to process
        backbars
            how many back bars you take to caculate
        
        you also can test the result from command line 
        
        csvtolist.py --backbars=number csvfile.csv
        
        -h --help       read the help
        
        -b --backbars   the number back bars you want to caculate

        read thhe csv file last few lines to process look back data
        the format we prefer
        YYYY/MM/DD,HH:MM,OPEN,HIGH,LOW,CLOSE,VOLUMN 
        YYYY/MM/DD,OPEN,HIGH,LOW,CLOSE,VOLUMN 
        or 
        YYYY-MM-DD,OPEN,HIGH,LOW,CLOSE,VOLUMN
    """

    dl = []
    if filename and os.path.isfile(filename):
        fp           = open(filename,"rb")
        #fsize       = os.path.getsize(filename)
        content      = fp.read()
        lines        = []
        si           = -1 # start point index
        ei           = -1
        date_split   = "?"
        dt_samefield = False # datetime
        
        # identify date text
        if content.find('/') >= 4 : # AC year 2011/01/01
            date_split="/"
        elif content.find('-') >= 4:
            date_split="-"
        
        # check for start or end
        if start:
            si = content.find(start)

        if end:
            ei = content.rfind(end) # look up from end of file

        # prepare the return list
            
        if si >0 and ei>0:
            lines = content[si:ei].splitlines() # this will strip \r or \n
        elif si>0:
            lines = content[si:].splitlines()
        elif ei>0:
            lines = content[:ei].splitlines()

        else:
            lines = content.splitlines()[-backbars:]
        
        # empty file
        if not lines: return dl
        
        # check datetime combination in last line
        lastline = lines[-1]
        ll= lastline.split(',')
        if ll[0].split(" ") > 1 and len(ll) == 6:
            # datetime field YYYY/MM/DD HH:MM,OPEN,HIGH,LOW,CLOSE,VOLUMN 
            dt_samefield = True
            
        for line in lines:
            line = line.strip()
            if line.startswith(","): 
                line=line[1:]
            if line.endswith(","): 
                line=line[:-1]

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

            # in case we have date time combine field
            datel = ll[0].split(" ")[0]
            date = datel.split(date_split)[:3]
            date = map(int,date)
        
            if dt_samefield:
                # have no HH:MM:SS
                #o,h,l,c,v = map(decimal.Decimal,ll[1:])
                o,h,l,c,v = map(float,ll[1:])
                
                # may date time at first field
                if ll[0].find(":")>2:
                    # find a mark like time
                    dtl = ll[0]
                    m1 = dtl.find(":")
                    hh = int(dtl[m1-2:m1])
                    mm = int(dtl[m1+1:m1+3])
                    ss = 0
            
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
                #pprint.pprint(csvtolist(args[0],int(a)))
                #print csvtolist(args[0],int(a))
                import timeit
                tt = timeit.Timer("csvtolist('%s',%d)"%(args[0],int(a)),"from __main__ import csvtolist")
                print "Run csvtolist once take ",tt.timeit(500)/500
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
