#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: terryh.tp at gmail.com

# wxPython
import wx
from wx.lib.wordwrap import wordwrap
from wxobject import MyFrame, M, C, D, S

import os
import sys
import logging
import re
import datetime
import subprocess
import shlex
import tempfile
import multiprocessing
import multiprocessing.forking

# help pyinstaller, cx_Freeze to include
from ctypes import POINTER, WINFUNCTYPE, c_char_p, c_void_p, c_int, c_ulong
from ctypes.wintypes import BOOL, DWORD, BYTE, INT, LPCWSTR, UINT, ULONG

#import calendar
#from shutil import copyfile

# locale
#import gettext
#_ = gettext.ugettext

# third party module
from configobj import ConfigObj

#help pyinstaller to find
import pytz

#------------------------------------------
from tz import timezones
from wxutils import wxd_to_python, python_to_wxd, showMsg, ShowBusyCursor
from quote.utils import get_now, get_tz_hhmm

# Process
from quote.quoteworker import QuoteWriter

__version__ = u'0.2.1'
__appname__ = u'AutoTrader'
__author__ = u'TerryH'

app_realpath = os.path.realpath(sys.argv[0])
app_dir = os.path.dirname(app_realpath)

market_ini = os.path.join(app_dir, 'config', 'market.ini')
commodity_ini = os.path.join(app_dir, 'config', 'commodity.ini')
strategy_ini = os.path.join(app_dir, 'config', 'strategy.ini')
data_dir = os.path.join(app_dir, 'data')

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

re_alphanumeric = re.compile(r'^\w+$')
re_date = re.compile(r'^\d{4}-\d{2}-\d{2}$')

quote_module_dir = 'quote'

QUOTE_SOURCE = [u"", u'DDE']

# fixed name for quoteworker
QUOTE_WRITER_EXE = 'quoteworker.exe'
TRADER_EXE = 'trader.exe'

# support tracking trade time
SUPPORT_TIME = ['min1', 'min2', 'min3', 'min5', 'min15', 'min30', 'hour1',
                'day1']
SUPPORT_TIME_NAME = ['1 Min', '2 Min', '3 Min', '5 Min', '15 Min',
                     '30 Min', '1 Hour', '1 Day']
#SUPPORT_TIME_NAME = ['1 Min':'min1',
#                     '2 Min':'min2',
#                     '3 Min':'min3',
#                     '5 Min':'min5',
#                     '15 Min':'min15',
#                     '30 Min':'min30',
#                     '1 Hour':'hour1',
#                     '1 Day':'day1'
#                    }

######################################################
# work around for pyinstaller one file execuable pack
# but now we use cx_Freeze


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

################################################################################
# start multiprocessing.Process outside wxApp main loop
# now in favor to subprocess.Popen via the following code block


def start_quote_process(quote_method, commodity='', commodity_ini=''):
    quote_module = __import__(
        "quote.%s" % quote_method, fromlist=[quote_method])
    p = multiprocessing.Process(
        target=quote_module.main, args=(commodity, commodity_ini))
    p.start()
    return p


def start_quote_workers(market_ini, commodity_ini, ccode):
    p = QuoteWriter(market_ini, commodity_ini, ccode)
    p.start()
    return p
################################################################################

################################################################################
# start subprocess.Popen outside wxApp main loop


def sub_process_stdout(final_command):
    #print final_command
    p = subprocess.Popen(shlex.split(final_command), stdout=subprocess.PIPE)
    return p


def sub_process(final_command):
    #print final_command
    p = subprocess.Popen(shlex.split(final_command))
    return p
################################################################################

#------------------------------------------


class Mixin(object):
    def collect_data(self):
        raw_dict = {}
        for k in self.field_keys:
            if getattr(self.__dict__[k], 'GetValue', False):
                raw_dict[k] = self.__dict__[k].GetValue()
            elif getattr(self.__dict__[k], 'GetStringSelection', False):
                raw_dict[k] = self.__dict__[k].GetStringSelection()
            elif getattr(self.__dict__[k], 'GetPath', False):
                raw_dict[k] = self.__dict__[k].GetPath()
        return raw_dict

    def loaditem(self, code=''):
        if self.configobj and code in self.configobj:
            for k in self.field_keys:
                #print k
                if self.configobj[code].get(k):
                    setvalue = self.configobj[code].get(k)
                    # casting
                    if setvalue == u'True':
                        setvalue = True
                    if setvalue == u'False':
                        setvalue = False

                    # datetime date to wx.DateTime
                    if (isinstance(setvalue, str) or isinstance(setvalue, unicode)) and re_date.search(setvalue):
                        setvalue = python_to_wxd(setvalue)

                    if getattr(self.__dict__[k], 'SetValue', False):
                        self.__dict__[k].SetValue(setvalue)
                    elif getattr(self.__dict__[k], 'SetStringSelection', False):
                        self.__dict__[k].SetStringSelection(setvalue)
                    elif getattr(self.__dict__[k], 'SetPath', False):
                        self.__dict__[k].SetPath(setvalue)

#------------------------------------------


class Strategy(S, Mixin):
    def __init__(self, *args, **kwds):
        S.__init__(self, *args, **kwds)
        wx.EVT_CHAR_HOOK(self, self.onKey)
        self.configobj = {}
        self.inifile = strategy_ini
        self.configobj = {}
        self.c_obj = ConfigObj(commodity_ini, encoding='utf-8')
        self.field_keys = ['strategyfile', 'historyfile', 'ccode',
                           'period', 'num', 'cost',
                           'start', 'end', 'sid', 'run'
                           ]
        self.require_fields = ['strategyfile', 'ccode', 'period', 'num']
        self.ccode.SetItems([v.get('ccode') for k, v in self.c_obj.items()])
        self.period.SetItems(SUPPORT_TIME_NAME)
        self.loaddata()

    def validate(self, raw_dict={}):
        for key in self.require_fields:
            if not raw_dict.get(key, False):
                return False
        # extra validate
        if not raw_dict.get('num').isdigit():
            return False
        if raw_dict.get('cost', False) and not raw_dict.get('cost').isdigit():
            return False
        return True

    def get_data_dir(self):
        if self.ccode.GetValue():
            ccode = self.ccode.GetValue()
            dir_name = "%s_%s" % (self.c_obj[ccode].get(
                'mcode'), self.c_obj[ccode].get('ccode'))
            history_dir = os.path.join(data_dir, dir_name)
            if history_dir and not os.path.exists(history_dir):
                os.makedirs(history_dir)
            return history_dir
        return ''

    def onSubmit(self, event):
        raw_dict = self.collect_data()

        if not self.validate(raw_dict):
            dlg = wx.MessageDialog(self,
                                   _("You must at least have strategy file, commodity code, trading time period and max number of bars will use in strategy."),
                                   _("Strategy"),
                                   wx.OK | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self,
                                   _("Are you sure want to update?"),
                                   _("Strategy"),
                                   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
            if val == wx.ID_YES:
                sid = self.sid.GetValue()

                if not sid:
                    # let's find a new sid, forget about race, lock, and looping
                    start_id = 1
                    if not sid:
                        sid = self.get_new_id()
                        raw_dict['sid'] = sid
                # wx.DateTime
                if raw_dict.get('start'):
                    raw_dict['start'] = wxd_to_python(
                        raw_dict.get('start')).strftime('%Y-%m-%d')
                if raw_dict.get('end'):
                    raw_dict['end'] = wxd_to_python(
                        raw_dict.get('end')).strftime('%Y-%m-%d')

                if sid not in self.configobj:
                    # insert
                    self.configobj[sid] = {}

                for key in self.field_keys:
                    self.configobj[sid][key] = raw_dict.get(key, '')

                self.configobj.write()  # write ini file
                self.Destroy()

    def onValidate(self, event):
        raw_dict = self.collect_data()
        if 'strategyfile' in raw_dict:
            final_command = r'%s --file "%s"' % (
                TRADER_EXE, raw_dict['strategyfile'])
            p = sub_process_stdout(final_command)
            message = p.stdout.read().strip()
            if message:
                print "Go , haha ,cauch U", str(message), len(message), len(message.strip())
                showMsg(self, message)
            else:
                showMsg(self, _("No error found"))

    def onDelete(self, event):
        if self.configobj and self.sid.GetValue():
            sid = self.sid.GetValue()
            dlg = wx.MessageDialog(self,
                                   _('Are you sure?'),
                                   _('Delete'),
                                   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
            if val == wx.ID_YES:

                del self.configobj[sid]  # delete & write back
                self.configobj.write()
                self.Destroy()

        self.Destroy()

    def onKey(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Close()
        event.Skip()

    def onBackTest(self, event):
        print "BackTest"

        # you must specify the start date, end date or both
        self.onSubmit(event)

        self.loaddata()

        sid = self.sid.GetValue()
        raw_dict = self.configobj[sid]
        # condition to run back test
        _goBackTest = ((raw_dict.get('start') or raw_dict.get('end')) and
                       raw_dict.get('strategyfile') and raw_dict.get('historyfile'))
        if _goBackTest:
            # example command
            #  python trader.py -his FITX.txt --end 2010/10/13 -b 10 -f stest.py
            command_list = [TRADER_EXE, '--file', r'"%s"' %
                            raw_dict['strategyfile']]

            if raw_dict.get('start'):
                command_list.append("--start")
                command_list.append(raw_dict['start'])

            if raw_dict.get('end'):
                command_list.append("--end")
                command_list.append(raw_dict['end'])

            # must have
            command_list.append("--history")
            command_list.append(r'"%s"' % raw_dict['historyfile'])

            final_command = " ".join(command_list)
            p = sub_process_stdout(final_command)
            message = p.stdout.read().strip()
            #message =  p.stdout.read()
            if message:
                # clean windows stdout line break
                message = message.replace('\r', "")
                fname = os.path.join(tempfile.gettempdir(), "autotrader.csv")
                fp = open(fname, "w")
                fp.write(message)
                os.startfile(fname)
        else:
            dlg = wx.MessageDialog(self,
                                   _("You must at least, config start date, end date or both, with history file"),
                                   _("Back Test"),
                                   wx.OK | wx.ICON_INFORMATION
                                   )
            dlg.ShowModal()
            dlg.Destroy()

    def get_new_id(self):
        start_id = 1
        sid = 0
        while not sid:
            if not str(start_id) in self.configobj:
                sid = str(start_id)
                return sid
            start_id += 1

    def loaddata(self):
        self.configobj = ConfigObj(self.inifile, encoding='utf-8')

#------------------------------------------


class DDEWIN(D, Mixin):
    def __init__(self, *args, **kwds):
        D.__init__(self, *args, **kwds)
        wx.EVT_CHAR_HOOK(self, self.onKey)
        self.configobj = {}
        self.field_keys = ['mcode', 'ccode',
                           'dde1_server', 'dde1_topic', 'dde1_time', 'dde1_price', 'dde1_volume',
                           'dde2_server', 'dde2_topic', 'dde2_time', 'dde2_price', 'dde2_volume'
                           ] + SUPPORT_TIME
        self.require_fields = ['dde1_server', 'dde1_topic',
                               'dde1_time', 'dde1_price', 'dde1_volume']

    def validate(self, raw_dict={}):
        for key in self.require_fields:
            if not raw_dict.get(key, False):
                return False
        return True

    def onSubmit(self, event):
        raw_dict = self.collect_data()

        if not self.validate(raw_dict):
            dlg = wx.MessageDialog(self,
                                   _("You must at least input DD1, time, price and volume, can refer from Excel."),
                                   _("DDE"),
                                   wx.OK | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self,
                                   _("Are you sure want to update?"),
                                   _("DDE"),
                                   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
            if val == wx.ID_YES:
                # TODO
                self.GetParent().update_quote(raw_dict, self.field_keys)
                self.Destroy()

    def onCancel(self, event):
        self.Close()

    def onDelete(self, event):
        if self.configobj:
            dlg = wx.MessageDialog(self,
                                   _('Are you sure?'),
                                   _('Delete'),
                                   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
            if val == wx.ID_YES:
                self.GetParent().delete_quote()
                self.Destroy()

        self.Destroy()

    def onKey(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Close()
        event.Skip()

#------------------------------------------


class Commodity(C, Mixin):
    def __init__(self, *args, **kwds):
        C.__init__(self, *args, **kwds)
        wx.EVT_CHAR_HOOK(self, self.onKey)
        self.field_keys = ['cname', 'ccode', 'mcode', 'cpov',
                           'csource', 'cdir']
        self.require_fields = ['cname', 'ccode', 'mcode']
        self.inifile = commodity_ini
        self.configobj = {}
        self.m_obj = ConfigObj(market_ini, encoding='utf-8')
        self.markets = [(v.get('mname'), v.get('mcode')) for k,
                        v in self.m_obj.items()]
        self.loaddata()
        self.csource.SetItems(QUOTE_SOURCE)
        self.mcode.SetItems([mcode for mname, mcode in self.markets])

    def validate(self, raw_dict={}):
        for key in self.require_fields:
            if not raw_dict.get(key, False):
                return False
        if not re_alphanumeric.search(raw_dict.get('ccode')):
            return False
        return True

    def onSubmit(self, event):
        raw_dict = self.collect_data()
        if not self.validate(raw_dict):
            dlg = wx.MessageDialog(self,
                                   _("You must at least input Commodity Name, Commodity Code (alphanumeric), and Quote Folder for real time data processing, better at a ram disk folder."),
                                   _("Market"),
                                   wx.OK | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self,
                                   _("Are you sure want to update?") +
                                   ' ' + _("Remember to restart to ative changes."),
                                   _("Market"),
                                   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
            if val == wx.ID_YES:
                ccode = raw_dict['ccode'].upper()
                raw_dict['ccode'] = ccode

                if ccode not in self.configobj:
                    self.configobj[ccode] = {}
                #print raw_dict

                for key in self.field_keys:
                    self.configobj[ccode][key] = raw_dict.get(key, '')
                self.configobj.write()  # write ini file
                self.Close()

    def onSource(self, event):
        if self.csource.GetStringSelection():
            self.config.Enable()
        else:
            self.config.Enable(False)

    def onConfig(self, event):
        raw_dict = self.collect_data()
        source = raw_dict.get('csource')
        mcode = raw_dict.get('mcode')
        ccode = raw_dict.get('ccode')

        if source and source in QUOTE_SOURCE:
            support_time = SUPPORT_TIME  # FIXME, check this value
            try:
                exec('support_time = %s_SUPPORT_TIME' % source)
            except:
                pass  # FIXME, better chance to load support field

            try:
                __import__("quote.%s" % (source), fromlist=[source])

                dlg = DDEWIN(self)  # FIXME, add more config
                dlg.mcode.SetValue(mcode)
                dlg.ccode.SetValue(ccode)
                self.loaddata()  # reload data again to make sure
                if self.configobj.get(ccode):
                    dlg.configobj = self.configobj.get(ccode)
                    dlg.loaditem('quote')

                dlg.ShowModal()
                dlg.Destroy()
            except ImportError:
                self.GetParent().loginfo(_('No support quote module found.'))

    def onHistory(self, event):
        history_dir = self.check_history()
        if history_dir:
            if os.name == 'nt':
                os.startfile(history_dir)
            elif os.name == 'posix':
                try:
                    os.system('xdg-open %s' % history_dir)
                              # try open histtory folder on linux
                except:
                    pass  # TODO

    def check_history(self):
        dir_name = ''
        history_dir = ''
        if self.ccode.GetValue() and self.mcode.GetStringSelection():
            self.history.Enable()
            dir_name = "%s_%s" % (self.mcode.GetStringSelection(
            ), self.ccode.GetValue().upper())
            history_dir = os.path.join(data_dir, dir_name)
            if history_dir and not os.path.exists(history_dir):
                os.makedirs(history_dir)
            return history_dir
        else:
            self.history.Enable(False)

        return

    def onMcode(self, event):
        self.check_history()

    def onDelete(self, event):
        ccode = self.ccode.GetValue().upper()
        if ccode and ccode in self.configobj:
            dlg = wx.MessageDialog(self,
                                   _('Are you sure?'),
                                   _('Delete'),
                                   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
            if val == wx.ID_YES:
                del self.configobj[ccode]
                self.configobj.write()
        self.Destroy()

    def onKey(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Close()
        event.Skip()

    def loaddata(self, m_obj={}):
        self.configobj = ConfigObj(self.inifile, encoding='utf-8')
        if m_obj:
            self.m_obj = m_obj

    def set_market_obj(self, m_obj={}):
        if m_obj:
            self.m_obj = m_obj

    def update_quote(self, quote_obj={}, field_keys=[]):
        if self.configobj and self.ccode.GetValue() and self.configobj.get(self.ccode.GetValue()):
            cid = self.ccode.GetValue()
            if not self.configobj[cid].get('quote', False):
                self.configobj[cid]['quote'] = {}

            for k in field_keys:
                self.configobj[cid]['quote'][k] = quote_obj.get(k, '')
            self.configobj.write()

    def delete_quote(self):
        if self.configobj and self.ccode.GetValue() and self.configobj.get(self.ccode.GetValue()):
            del self.configobj[self.ccode.GetValue()]['quote']
            self.configobj.write()

    def loaditem(self, ccode=''):
        super(Commodity, self).loaditem(ccode)
        if self.csource.GetStringSelection():
            self.config.Enable()
        if self.ccode.GetValue() and self.mcode.GetStringSelection():
            self.history.Enable()

#------------------------------------------


class Market(M, Mixin):
    def __init__(self, *args, **kwds):
        M.__init__(self, *args, **kwds)
        wx.EVT_CHAR_HOOK(self, self.onKey)
        self.field_keys = ['mname', 'mcode', 'mtimezone', 'mclear',
                           's1_start', 's1_end', 's2_start', 's2_end',
                           'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6'
                           ]
        self.require_fields = ['mname', 'mcode', 'mtimezone',
                               'mclear', 's1_start', 's1_end']
        self.inifile = market_ini
        self.configobj = {}
        self.loaddata()
        self.mtimezone.SetItems(timezones)

    def validate(self, raw_dict={}):
        for key in self.require_fields:
            if not raw_dict.get(key, False):
                return False
        if not re_alphanumeric.search(raw_dict.get('mcode')):
            return False
        # special check for time 24HHMM
        if raw_dict['mclear'] == u'00:00' or raw_dict['s1_end'] == u'00:00':
            return False

        return True

    def onSubmit(self, event):
        raw_dict = self.collect_data()
        if not self.validate(raw_dict):
            dlg = wx.MessageDialog(self,
                                   _("You must at least input Market Name, Market Code (alphanumeric), Session Clear Time and Session 1 Time"),
                                   _("Market"),
                                   wx.OK | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self,
                                   _("Are you sure want to update?"),
                                   _("Market"),
                                   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
            if val == wx.ID_YES:
                mcode = raw_dict['mcode'].upper()
                raw_dict['mcode'] = mcode
                if raw_dict['mcode'] not in self.configobj:
                    self.configobj[mcode] = {}
                for key in self.field_keys:
                    self.configobj[mcode][key] = raw_dict.get(key, '')
                self.configobj.write()  # write ini file
                self.Close()

    def onCancel(self, event):
        self.Close()

    def onDelete(self, event):
        mcode = self.mcode.GetValue().upper()
        if mcode and mcode in self.configobj:
            dlg = wx.MessageDialog(self,
                                   _('Are you sure?'),
                                   _('Delete'),
                                   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
                                   )
            val = dlg.ShowModal()
            dlg.Destroy()
            if val == wx.ID_YES:
                del self.configobj[mcode]
                self.configobj.write()
        self.Destroy()

    def onKey(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Close()
        event.Skip()

    def loaddata(self):
        self.configobj = ConfigObj(self.inifile, encoding='utf-8')

#------------------------------------------


class FF(MyFrame):
    def __init__(self, *args, **kwds):
        MyFrame.__init__(self, *args, **kwds)

        self.quote_process = {}
        self.quote_workers = {}
        self.trader = {}
        self.strategy_process = {}

        # main application timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        self.timer.Start(1000 * 10)

        self.m_obj = {}  # market
        self.c_obj = {}  # commodity
        self.s_obj = {}  # strategy

        self.market_ini = market_ini
        self.commodity_ini = commodity_ini
        self.strategy_ini = strategy_ini

        self.data_ids = ['username', 'password', 'cert',
                         'certpass', 'autostart', ]  # 'sctrl','actrl']

        self.logfilename = os.path.join(app_dir, "autotrader.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=self.logfilename,
        )
        self.logger = logging.getLogger('')

        # Market
        self.mctrl.InsertColumn(0, _("Market Name"))
        self.mctrl.InsertColumn(1, _("Market Code"))
        self.mctrl.InsertColumn(2, _("Market Time Zone"))

        # Commodity
        self.cctrl.InsertColumn(0, _("Commodity Name"))
        self.cctrl.InsertColumn(1, _("Commodity Code"))
        self.cctrl.InsertColumn(2, _("Market Code"))
        self.cctrl.InsertColumn(3, _("Quote Source"))
        self.cctrl.InsertColumn(4, _("Quote Folder"))

        # Strategy
        self.sctrl.InsertColumn(0, _("Id"))
        self.sctrl.InsertColumn(1, _("Commodity Code"))
        self.sctrl.InsertColumn(2, _("Program File"))
        self.sctrl.InsertColumn(3, _("Time Period"))

        self.loaddata()
        self.render_all()

        # test
        self.test = None

    def onMarket(self, event):
        dlg = Market(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.load_market()
        self.render_market()

    def onMarketActive(self, event):
        item_index = event.m_itemIndex
        mcode = self.mctrl.GetItem(item_index, 1).GetText()
        dlg = Market(self)
        dlg.loaditem(mcode)
        dlg.ShowModal()
        dlg.Destroy()
        self.load_market()
        self.render_market()

    def onCommodity(self, event):
        dlg = Commodity(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.loaddata()
        self.render_commodity()

    def onCommodityActive(self, event):
        item_index = event.m_itemIndex
        ccode = self.cctrl.GetItem(item_index, 1).GetText()
        dlg = Commodity(self)
        dlg.loaditem(ccode)
        dlg.ShowModal()
        dlg.Destroy()
        self.load_commodity()
        self.render_commodity()

    def onStrategy(self, event):
        dlg = Strategy(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.load_strategy()
        self.render_strategy()

    def onStrategyActive(self, event):
        item_index = event.m_itemIndex
        sid = self.sctrl.GetItem(item_index, 0).GetText()
        dlg = Strategy(self)
        dlg.loaditem(sid)
        dlg.ShowModal()
        dlg.Destroy()
        self.load_strategy()
        self.render_strategy()

    def OnCheckItem(self, index, flag):
        sid = self.sctrl.GetItem(index, 0).GetText()
        #print index, flag, sid
        if self.s_obj.get(sid, False):
            # toggle run key value
            if flag:
                self.s_obj[sid]['run'] = True
            else:
                self.s_obj[sid]['run'] = ""
            self.s_obj.write()

    def onSave(self, event):
        dd = {}
        for k in self.data_ids:
            item = getattr(self, k)
            if hasattr(item, 'GetValue'):
                if k == 'username':
                    dd[k] = item.GetValue().upper()
                else:
                    dd[k] = item.GetValue()
            elif hasattr(item, 'GetPath'):
                dd[k] = item.GetPath()

        self.data = dd

    def onAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = __appname__
        info.Version = __version__
        info.Copyright = __author__
        info.Description = wordwrap(
            _("An easy tool for you to trade any commodity you like.\nLicense: MIT for individual, GPL for none individual.\n Author: TerryH"),
            350, wx.ClientDC(self))
        info.WebSite = (u"http://terryh.tp.blogspot.com/", u"TerryH's Blog")
        wx.AboutBox(info)

    def onQuit(self, event):
        dlg = wx.MessageDialog(self,
                               _('Are you sure?'),
                               _('Close'),
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION
                               )
        val = dlg.ShowModal()
        dlg.Destroy()
        if val == wx.ID_YES:
            # close all process
            self.stop_process()
            self.Destroy()

    def onTimer(self, event):
        """
        create process for quote service, strategy  start or stop
        """

        #self.loginfo('onTimer')
        for k, v in self.c_obj.items():
            if v.get('csource'):
                ccode = v['ccode']  # commodity code
                mcode = v['mcode']  # market code
                source = v['csource']
                mtimezone = self.m_obj[mcode]['mtimezone']

                session_start = ''
                session_end = ''

                mclear = self.m_obj[mcode]['mclear']
                s1_start = self.m_obj[mcode]['s1_start']
                s1_end = self.m_obj[mcode]['s1_end']
                s2_end = self.m_obj[mcode]['s2_end']

                if mclear and mclear != '00:00':
                    session_start = mclear
                elif s1_start and s1_start != '00:00':
                    session_start = mclear

                if s2_end and s2_end != '00:00':
                    session_end = s2_end
                elif s1_end and s1_end != '00:00':
                    session_end = s1_end

                key = "%s_%s" % (mcode, ccode)

                # commodity configureobj, get quote dir
                com_data_dir = os.path.join(app_dir, 'data', mcode, ccode)
                if v.get('cdir', False):
                    com_quote_dir = os.path.join(
                        v.get('cdir'), 'data', mcode, ccode)
                else:
                    # parent folder data/mcode/ccode
                    com_quote_dir = com_data_dir

                #self.loginfo(str(self.quote_process))
                if self.should_running(session_start, session_end, mtimezone):
                    # check this quote should running
                    if key not in self.quote_process:
                        # not running quote process
                        #s_hour, s_minute = map(int, session_start.split(':',1))
                        #now = get_now(mtimezone)
                        #market_start_time = get_tz_hhmm(s_hour, s_minute, mtimezone)
                        # we must start app 1 minute before market open
                        #if  (market_start_time-now).seconds < 60:
                        #quote_module = __import__("quote.%s" % source , fromlist=[source])
                        quote_exe = source + ".exe"

                        #--------------------------------------------------
                        # TODO nolonger use, REMOVE
                        #  start_quote_process and start_quote_workers
                        #t = start_quote_process( source, ccode, self.commodity_ini )
                        #self.quote_process[key] = t
                        #w = start_quote_workers(self.market_ini, self.commodity_ini, ccode)
                        #self.quote_workers[key] = w
                        #--------------------------------------------------

                        #--------------------------------------------------
                        # FIXME, need to uncomment
                        #  sub_quote_process and sub_quote_workers, add quote
                        #  for file path in case path have space
                        final_command = '%s --config "%s" --commodity %s' % (
                            quote_exe, self.commodity_ini, ccode)
                        self.loginfo(final_command)
                        t = sub_process(final_command)
                        self.quote_process[key] = t

                        final_command = '%s --mini "%s" --cini "%s" --commodity %s' % (QUOTE_WRITER_EXE, self.market_ini, self.commodity_ini, ccode)
                        self.loginfo(final_command)
                        w = sub_process(final_command)
                        self.quote_workers[key] = w
                        #--------------------------------------------------

                    #--------------------------------------------------
                    # check srategy should running
                    for sk, sv in self.s_obj.items():
                        # we store Troe False as string, TODO s_obj not update
                        # after saved, but should be lock update after running
                        # trader. ???
                        if sv['ccode'] == ccode:
                            if sv['run'] == True:
                                # prepare command
                                period_code = SUPPORT_TIME[
                                    SUPPORT_TIME_NAME.index(sv['period'])]
                                hisfile = os.path.join(
                                    com_data_dir, "%s.csv" % (period_code))
                                quotefile = os.path.join(
                                    com_quote_dir, "%s.ohlc" % (period_code))
                                #trader.py -his data\SMX\STW\min5.csv -q R:\TEMP\data\SMX\STW\min5.ohlc -f stest.py -g
                                final_command = r'%s --history "%s" --quote "%s" --file "%s" -g' % (TRADER_EXE, hisfile, quotefile, sv['strategyfile'])

                                # check exist or dead
                                if sk not in self.trader:
                                    self.loginfo(final_command)
                                    t = sub_process(final_command)
                                    self.trader[sk] = t
                                else:
                                    # have tarder running, let's poll it health
                                    if self.trader[sk].poll() is not None:
                                        # poll() == None mean running, maybe
                                        # some thing wrong restart it.
                                        self.trader.pop(sk)
                                        self.loginfo(final_command)
                                        t = sub_process(final_command)
                                        self.trader[sk] = t
                    #--------------------------------------------------

    def should_running(self, start, end, timezone):
        if (start and end and timezone):
            now = get_now(timezone)
            hh, mm = map(int, start.split(':', 1))
            tzstart = get_tz_hhmm(hh, mm, timezone)
            hh, mm = map(int, end.split(':', 1))
            tzend = get_tz_hhmm(hh, mm, timezone)
            if end < start:
                # trading time cross midnight
                return now >= tzstart or now <= tzend
            else:
                return now >= tzstart and now <= tzend

            return now >= tzstart

        return False

    def stop_process(self):

        # wait for close multiprocessing.Process
        #--------------------------------------------------
        for k in self.trader.keys():
            try:
                self.trader[k].terminate()
            except WindowsError:
                # if the quote source server already died
                # WindowsError: [Error 5]  Access Denied
                # FIXME
                pass
        for k in self.quote_process.keys():

            try:
                self.quote_process[k].terminate()
            except WindowsError:
                # if the quote source server already died
                # WindowsError: [Error 5]  Access Denied
                # FIXME
                pass

        for k in self.quote_workers.keys():
            try:
                self.quote_workers[k].terminate()
            except WindowsError:
                # if the quote source server already died
                # WindowsError: [Error 5]  Access Denied
                # FIXME
                pass

        #isalive = 1
        #while isalive:
            #isalive = 0
            #for k in self.quote_process.keys():
                #isalive = isalive + self.quote_process[k].is_alive()
        #isalive = 1
        #while isalive:
            #isalive = 0
            #for k in self.quote_workers.keys():
                #isalive = isalive + self.quote_workers[k].is_alive()
        #--------------------------------------------------

        #if hasattr(sys, 'frozen'):
            ## We need to wait for all child processes otherwise
            ## --onefile mode won't work.
            #while multiprocessing.active_children():
                #multiprocessing.active_children()[0].terminate()
            #time.sleep(3) # wait for kill all, FIXME better way for waitting

    def render_all(self):
        self.render_market()

        self.render_commodity()
        self.render_strategy()

    def render_market(self):
        self.mctrl.DeleteAllItems()
        for k, v in self.m_obj.items():
            index = self.mctrl.InsertStringItem(sys.maxint, v.get('mname'))
            self.mctrl.SetStringItem(index, 1, v.get('mcode'))
            self.mctrl.SetStringItem(index, 2, v.get('mtimezone'))
            self.mctrl.SetColumnWidth(2, 100)
            self.mctrl.SetItemBackgroundColour(index, wx.Color(229, 229, 229))

    def render_commodity(self):
        self.cctrl.DeleteAllItems()
        for k, v in self.c_obj.items():
            index = self.cctrl.InsertStringItem(sys.maxint, v.get('cname'))
            self.cctrl.SetStringItem(index, 1, v.get('ccode'))
            self.cctrl.SetStringItem(index, 2, v.get('mcode'))
            self.cctrl.SetStringItem(index, 3, v.get('csource'))
            self.cctrl.SetStringItem(index, 4, v.get('cdir'))
            self.cctrl.SetItemBackgroundColour(index, wx.Color(229, 229, 229))

    def render_strategy(self):
        self.sctrl.DeleteAllItems()
        for k, v in self.s_obj.items():
            index = self.sctrl.InsertStringItem(sys.maxint, k)
            self.sctrl.SetStringItem(index, 1, v.get('ccode'))
            self.sctrl.SetStringItem(index, 2, v.get('strategyfile'))
            self.sctrl.SetStringItem(index, 3, v.get('period'))
            self.sctrl.SetItemBackgroundColour(index, wx.Color(229, 229, 229))
            if v.get('run') == u"True":
                self.sctrl.CheckItem(index)

    def load_market(self):
        self.m_obj = ConfigObj(self.market_ini, encoding='utf-8')

    def load_commodity(self):
        self.c_obj = ConfigObj(self.commodity_ini, encoding='utf-8')

    def load_strategy(self):
        self.s_obj = ConfigObj(self.strategy_ini, encoding='utf-8')

    def loaddata(self):
        self.load_market()
        self.load_commodity()
        self.load_strategy()

    def loginfo(self, text=u""):
        if text:
            self.log.AppendText(datetime.datetime.now(
            ).strftime("%m-%d %H:%M:%S") + u" " + text + u"\n")
            self.logger.info(text)

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()  # multiprcessing workaround

    app = wx.PySimpleApp(False)

    #---------------------------------------------
    # locale
    #basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
    #localedir = os.path.join(basepath, "locale")
    langid = wx.LANGUAGE_DEFAULT
    mylocale = wx.Locale(langid)
    mylocale.AddCatalogLookupPathPrefix('./locale')
    mylocale.AddCatalog('messages')
    _ = wx.GetTranslation

    # override
    import __builtin__
    __builtin__._ = wx.GetTranslation

    # override wxobject
    import wxobject
    wxobject._ = wx.GetTranslation

    #---------------------------------------------

    frm = FF(None)
    frm.Show()

    # DEBUG comment out following two line
    #import wx.lib.inspection
    #wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()
