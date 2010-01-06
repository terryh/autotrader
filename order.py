#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
tracking on our order and state
Author: TerryH, email: terryh.tp@gmail.com, 
Thu, 31 Dec 2009 16:11:03 +0800
License: BSD
"""

__version__ = '0.0.1'
__author__ = 'TerryH'

import datetime

class Order(object):
    
    def __init__(self):
        # orders[0] contain [datetime,condition_name,action,market_position,price]
        self.orders = []
        self.order_time = []

        self.market_position = 0
        self.entry_price = 0
        self.bars_since_entry = 0
        self.bars_since_exit = 0
        self.dt = 0
        self.pov = 0 # point value 
        self.tax = 0 # if have point and tax, accounting it



    def BUY(self,condition_name="",price=0,datetime="",position=1):
        if not datetime and self.dt:
            datetime = self.dt
        if self.market_position==0 and price and datetime not in self.order_time:
            #print "BUY"
            self.market_position = position
            self.orders.append([datetime,condition_name,self.market_position,price])
            self.order_time.append(datetime)
            self.entry_price = price
        
        

    def SELL(self,condition_name="",price=0,datetime="",position=-1):
        if not datetime and self.dt:
            datetime = self.dt
        #print self.market_position==0 and price and datetime not in self.order_time
        if self.market_position==0 and price and datetime not in self.order_time:
            #print "SELL"
            self.market_position = position
            self.orders.append([datetime,condition_name,self.market_position,price])
            self.order_time.append(datetime)
            self.entry_price = price

    def EXITLONG(self,condition_name="",price=0,datetime=""):
        if not datetime and self.dt:
            datetime = self.dt
        if self.market_position>0 and datetime not in self.order_time:
            self.orders.append([datetime,condition_name,-self.market_position,price])
            self.order_time.append(datetime)
            self.market_position = 0
        

    def EXITSHORT(self,condition_name="",price=0,datetime=""):
        if not datetime and self.dt:
            datetime = self.dt
        if self.market_position<0 and datetime not in self.order_time:
            self.orders.append([datetime,condition_name,-self.market_position,price])
            self.order_time.append(datetime)
            self.market_position = 0

    def REPORT(self):
        if self.orders:
            net = 0
            # FIXME: a lot accounting result must be implement
            t_net = 0
            t_mk = 0
            t_max_draw_down=0
            t_win_count=0
            t_loss_count=0
            for i in range(len(self.orders)):
                #[datetime,condition_name,self.market_position,price]
                # 
                
                dt = self.orders[i][0]
                cn = self.orders[i][1]
                mk = self.orders[i][2]
                price = self.orders[i][3]

                print dt.strftime("%Y/%m/%d,  %H:%M:%S,")+"  %10.5f"%(price)+"%15s,"%(cn)+"%5d,    "%(mk)
                
                if mk<0:
                    net = net-mk*price
                elif mk>0:
                    net = net-mk*price
                
                

            if self.pov and self.tax:
                net =  self.pov*net - len(self.orders)*self.tax
            
            print "Total: %20f in  %d trades" % (net,len(self.orders)/2)
