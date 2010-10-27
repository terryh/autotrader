#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a strategy file for you to refer, 
this example is taking from TradeStation 程式交易全攻略,page 293, ISBN 978-957-0477-99-3
Author: TerryH, email: terryh.tp at gmail.com, 
License: BSD
"""

PARAS={
"ran":82,
}

VARS = {
"longentry":99999,
"shortentry":0,
"longex":0,
"shortex":99999,
"count":0,    
}


#MA2 = map(round,AverageFC(C,5))
if DATE[0] != DATE[1]:
    #print "NEW DATE", DATE[0],TIME[0]
    longentry = OPEN[0]+ran
    shortentry = OPEN[0]-ran


if MARKETPOSITION == 0 and count == 0 and HH >= longentry:
    BUY("BUY",HH) 

if MARKETPOSITION == 0 and count == 0 and LL <= shortentry:
    SELL("SELL",LL) 


if MARKETPOSITION > 0 and HIGH[0]-ran > longentry:
    longex = HIGH[0]-ran
    count = 1

if MARKETPOSITION < 0 and LOW[0]+ran < shortentry:
    shortex = LOW[0]+ran
    count = 1

if MARKETPOSITION > 0 and count == 1 and LL <= longex:
    EXITLONG("LONG EXIT",LL)


if MARKETPOSITION < 0 and count == 1 and HH >= shortex:
    EXITSHORT("SHORT EXIT",HH)

if MARKETPOSITION == 0 and count == 1:
    longentry = CLOSE[1]+ran
    shortentry = CLOSE[0]-ran
    longex = 0
    shortex = 99999
    count = 0

if TIME[0] >= 133000 and MARKETPOSITION != 0:
#   print "Clear Market Position"
    EXITLONG("GYXL",C[0])
    EXITSHORT("GYXS",C[0])


print DATE[0],TIME[0],O[0],C[0],MKS



