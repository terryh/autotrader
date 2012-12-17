#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General include OPEN, HIGH, LOW, CLOSE, VLOUMN
Author: TerryH, email: terryh.tp at gmail.com, 
License: BSD
"""
import datetime
from math import sqrt
from AverageFC import Average

def General(dataset,length=300):
    """dateset is a item list in datetime order, and 
       dateset structure [dt,o,h,l,c,v] last is latest data
       FIXME we use list just in beginning, if the speed is OK
    """
    s = 0     
    dl = []
    tl = []
    ol = []
    hl = []
    ll = []
    cl = []
    vl = []
    if dataset:
        for i in dataset[-length:]:
            dl.append(int(i[0].strftime("%Y%m%d")))
            tl.append(int(i[0].strftime("%H%M%S")))
            ol.append(i[1])
            hl.append(i[2])
            ll.append(i[3])
            cl.append(i[4])
            vl.append(i[5])
        
        # reverse the list, CLOSE[0] become the latest 

        dl.reverse()
        tl.reverse()
        ol.reverse()
        hl.reverse()
        ll.reverse()
        cl.reverse()
        vl.reverse()
        num = len(dl)
        if num < length:
            dl += [0]*(length-num)
            tl += [0]*(length-num)
            ol += [0]*(length-num)
            ll += [0]*(length-num)
            cl += [0]*(length-num)
            vl += [0]*(length-num)
            
    
    return dl,tl,ol,hl,ll,cl,vl

def General_Row(dl=[],tl=[],ol=[],hl=[],ll=[],cl=[],vl=[],one_dataset_item=[],length=300):
    """dateset is a item list in datetime order, and 
       dateset structure [dt,o,h,l,c,v] last is latest data
       FIXME we use list just in beginning, if the speed is OK
       it's very UGLY hack
    """
    i = one_dataset_item
    if i and len(i)>=6 :
            dl.insert(0,(int(i[0].strftime("%Y%m%d"))))
            tl.insert(0,int(i[0].strftime("%H%M%S")))
            ol.insert(0,i[1])
            hl.insert(0,i[2])
            ll.insert(0,i[3])
            cl.insert(0,i[4])
            vl.insert(0,i[5])
        
    while len(dl)>length:
        dl.pop()
    while len(tl)>length:
        tl.pop()
    while len(ol)>length:
        ol.pop()
    while len(hl)>length:
        hl.pop()
    while len(ll)>length:
        ll.pop()
    while len(cl)>length:
        cl.pop()
    while len(vl)>length:
        vl.pop()
    
    if len(dl)<length:
        dl += [0]*(length-len(dl))
    if len(tl)<length:
        tl += [0]*(length-len(tl))
    if len(ol)<length:
        ol += [0]*(length-len(ol))
    if len(hl)<length:
        hl += [0]*(length-len(hl))
    if len(ll)<length:
        ll += [0]*(length-len(ll))
    if len(cl)<length:
        cl += [0]*(length-len(cl))
    if len(vl)<length:
        vl += [0]*(length-len(vl))
        


    
    return dl,tl,ol,hl,ll,cl,vl

def Highest(price=0,length=10):
    """price is a list
    """
    return max(price[:length])

def Lowest(price=0,length=10):
    """price is a list
    """
    return min(price[:length])

def HighD(dataset=[]):
    """Find High of Day
    """
    tempd = datetime.date(1900,1,1)
    tempV = 0
    vl = []
    if dataset:
        for ll  in dataset:
            dt,o,h,l,c,v = ll 
            if dt.date() == tempd:
                if h > tempV:
                    tempV = h
            else:
                vl.append(tempV)    
                tempV = h
            
            tempd = dt.date()
        
        # don't forget the last one
        vl.append(tempV)    


    vl.reverse()

    return vl

def LowD(dataset=[]):
    """Find Low of Day
    """
    tempd = datetime.date(1900,1,1)
    tempV = 0
    vl = []
    if dataset:
        for ll  in dataset:
            dt,o,h,l,c,v = ll 
            if dt.date() == tempd:
                if l < tempV:
                    tempV = l
            else:
                vl.append(tempV)    
                tempV = l
            
            tempd = dt.date()
        
        # don't forget the last one
        vl.append(tempV)    


    vl.reverse()

    return vl

def StdDev(price=0,length=10):
    """Stardard Deviation
    """
    SumSqrt = 0
    if price and len(price) >= length and length>0:
        # Average return a list, just take first one
        av = Average(price,length)[0]

        for i in range(length):
            SumSqrt = SumSqrt + (price[i]-av)*(price[i]-av)

        return sqrt(SumSqrt/length)
    else:
        return 0

def BollingerBand(price=0,length=10,stdev=2):
    """BollingerBand
    """
    if price and len(price) >= length and length>0:
        # Average return a list, just take first one
        av = Average(price,length)[0]
        return av + stddev*StdDev(price,length)
    else:
        return 0
