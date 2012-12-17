# -*- coding: utf-8 -*-
import os
import sys
import pytz
import datetime
import multiprocessing
import multiprocessing.forking

######################################################
# work around for pyinstaller
multiprocessing.freeze_support()
class _Popen(multiprocessing.forking.Popen):
    def __init__(self, *args, **kw):
        if hasattr(sys, 'frozen'):
            # We have to set _MEIPASS2 to get
            # --onefile and --onedir mode working.
            os.putenv('_MEIPASS2', sys._MEIPASS) # last character is stripped in C-loader
        try:
            super(_Popen, self).__init__(*args, **kw)
        finally:
            if hasattr(sys, 'frozen'):
                os.unsetenv('_MEIPASS2')

class Process(multiprocessing.Process):
    _Popen = _Popen

def get_now(timezone=''):
    #            self.tz = tz
    if timezone:
        tz = pytz.timezone(timezone)
        now = datetime.datetime.now(tz=tz)
    else:
        now = datetime.datetime.now()
    return now


def get_tz_hhmm(hour, minute,timezone=''):
    
    if timezone:
        # timezone
        tz = pytz.timezone(timezone)
        dt = datetime.datetime.now(tz=tz).replace(hour=hour, minute=minute, second=0, microsecond=0)
    else:
        dt = datetime.datetime.now().replace(second=0, microsecond=0)
        dt.replace(hour=hour, minute=minute)
    
    return dt
            
def get_quote_dir(market_code, commodity_code, app_dir='..' + os.path.sep):
    return os.path.join(app_dir, 'data', '%s_%s' % ( market_code, commodity_code ))

def get_data_dir(market_code, commodity_code, app_dir='..' + os.path.sep):
    return os.path.join(app_dir, 'data', '%s_%s' % ( market_code, commodity_code ))

def get_now_file(commodity_code, quote_dir='..' + os.path.sep):
    return os.path.join( quote_dir, commodity_code + ".now")

def get_ohlc_file(commodity_code, quote_dir='..' + os.path.sep):
    return os.path.join( quote_dir, commodity_code + ".ohlc")

