#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fast Moving Average
Author: TerryH, email: terryh.tp at gmail.com, 2009-12-25 19:42:18+08:00
License: BSD
"""
def AverageFC(price,length):
    """price must be a list 
       FIXME we use list just in beginning, if the speed is OK
    """
    s = 0     
    ll = []
    
    if len(price)>length:

        s = sum(price[:length-1])
        n = 0
        for i in price[length-1:]:
            s = s+i
            ll.append(s/length)
            s = s-price[n]
            n = n+1
    else:
        ll.append(sum(price)/len(price))

    num = len(ll)
    if num < length:
            ll += [0]*(length-num)
    return ll

MA = AverageFC
Average = AverageFC

