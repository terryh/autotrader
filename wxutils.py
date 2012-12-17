#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: terryh.tp at gmail.com

import wx
import datetime

# TODO, only keep one version
def _p2w(date): 
    assert isinstance(date, (datetime.datetime, datetime.date)) 
    tt = date.timetuple() 
    dmy = (tt[2], tt[1]-1, tt[0]) 
    return wx.DateTimeFromDMY(*dmy) 

def _w2p(date): 
    assert isinstance(date, wx.DateTime) 
    if date.IsValid(): 
        ymd = map(int, date.FormatISODate().split('-')) 
        return datetime.date(*ymd) 
    else: 
        return None

def wxd_to_python(value):
    # parse wx.DateTime to python datetime.date
    year = value.GetYear()
    month = value.GetMonth() + 1
    day = value.GetDay()
    return datetime.date(year,month,day)     

def python_to_wxd(value):
    # parse python datetime.date to wx.DateTime
    wxd = wx.DateTime()
    wxd.ParseDate(str(value))
    return wxd 

def showMsg(self, msg):
    try:
        dlg = wx.MessageDialog( self, msg,'', wx.OK | wx.ICON_INFORMATION )
        dlg.ShowModal()
    finally:
        dlg.Destroy()

def ShowBusyCursor(f):
    def func(*args, **kwargs):
        wx.BeginBusyCursor()
        ret = f(*args, **kwargs)
        wx.EndBusyCursor()
        return ret
    return func
