#!/usr/bin/env python
# taken from http://code.activestate.com/recipes/577654-dde-client/
# Send DDE Execute command to running program

import os
import sys

import traceback
import imp
import datetime
import time
import types
import argparse

from configobj import ConfigObj
from collections import defaultdict

from ctypes import POINTER, WINFUNCTYPE, c_char_p, c_void_p, c_int, c_ulong
from ctypes.wintypes import BOOL, DWORD, BYTE, INT, LPCWSTR, UINT, ULONG


# DECLARE_HANDLE(name) typedef void *name;
HCONV = c_void_p  # = DECLARE_HANDLE(HCONV)
HDDEDATA = c_void_p  # = DECLARE_HANDLE(HDDEDATA)
HSZ = c_void_p  # = DECLARE_HANDLE(HSZ)
LPBYTE = c_char_p  # POINTER(BYTE)
LPDWORD = POINTER(DWORD)
LPSTR = c_char_p
ULONG_PTR = c_ulong

# See windows/ddeml.h for declaration of struct CONVCONTEXT
PCONVCONTEXT = c_void_p

DMLERR_NO_ERROR = 0

# Predefined Clipboard Formats
CF_TEXT = 1
CF_BITMAP = 2
CF_METAFILEPICT = 3
CF_SYLK = 4
CF_DIF = 5
CF_TIFF = 6
CF_OEMTEXT = 7
CF_DIB = 8
CF_PALETTE = 9
CF_PENDATA = 10
CF_RIFF = 11
CF_WAVE = 12
CF_UNICODETEXT = 13
CF_ENHMETAFILE = 14
CF_HDROP = 15
CF_LOCALE = 16
CF_DIBV5 = 17
CF_MAX = 18

DDE_FACK = 0x8000
DDE_FBUSY = 0x4000
DDE_FDEFERUPD = 0x4000
DDE_FACKREQ = 0x8000
DDE_FRELEASE = 0x2000
DDE_FREQUESTED = 0x1000
DDE_FAPPSTATUS = 0x00FF
DDE_FNOTPROCESSED = 0x0000

DDE_FACKRESERVED = (~(DDE_FACK | DDE_FBUSY | DDE_FAPPSTATUS))
DDE_FADVRESERVED = (~(DDE_FACKREQ | DDE_FDEFERUPD))
DDE_FDATRESERVED = (~(DDE_FACKREQ | DDE_FRELEASE | DDE_FREQUESTED))
DDE_FPOKRESERVED = (~(DDE_FRELEASE))

XTYPF_NOBLOCK = 0x0002
XTYPF_NODATA = 0x0004
XTYPF_ACKREQ = 0x0008

XCLASS_MASK = 0xFC00
XCLASS_BOOL = 0x1000
XCLASS_DATA = 0x2000
XCLASS_FLAGS = 0x4000
XCLASS_NOTIFICATION = 0x8000

XTYP_ERROR = (0x0000 | XCLASS_NOTIFICATION | XTYPF_NOBLOCK)
XTYP_ADVDATA = (0x0010 | XCLASS_FLAGS)
XTYP_ADVREQ = (0x0020 | XCLASS_DATA | XTYPF_NOBLOCK)
XTYP_ADVSTART = (0x0030 | XCLASS_BOOL)
XTYP_ADVSTOP = (0x0040 | XCLASS_NOTIFICATION)
XTYP_EXECUTE = (0x0050 | XCLASS_FLAGS)
XTYP_CONNECT = (0x0060 | XCLASS_BOOL | XTYPF_NOBLOCK)
XTYP_CONNECT_CONFIRM = (0x0070 | XCLASS_NOTIFICATION | XTYPF_NOBLOCK)
XTYP_XACT_COMPLETE = (0x0080 | XCLASS_NOTIFICATION)
XTYP_POKE = (0x0090 | XCLASS_FLAGS)
XTYP_REGISTER = (0x00A0 | XCLASS_NOTIFICATION | XTYPF_NOBLOCK)
XTYP_REQUEST = (0x00B0 | XCLASS_DATA)
XTYP_DISCONNECT = (0x00C0 | XCLASS_NOTIFICATION | XTYPF_NOBLOCK)
XTYP_UNREGISTER = (0x00D0 | XCLASS_NOTIFICATION | XTYPF_NOBLOCK)
XTYP_WILDCONNECT = (0x00E0 | XCLASS_DATA | XTYPF_NOBLOCK)
XTYP_MONITOR = (0x00F0 | XCLASS_NOTIFICATION | XTYPF_NOBLOCK)

XTYP_MASK = 0x00F0
XTYP_SHIFT = 4

TIMEOUT_ASYNC = 0xFFFFFFFF


def get_winfunc(libname, funcname, restype=None, argtypes=(), _libcache={}):
    """Retrieve a function from a library, and set the data types."""
    from ctypes import windll

    if libname not in _libcache:
        _libcache[libname] = windll.LoadLibrary(libname)
    func = getattr(_libcache[libname], funcname)
    func.argtypes = argtypes
    func.restype = restype

    return func


DDECALLBACK = WINFUNCTYPE(HDDEDATA, UINT, UINT, HCONV, HSZ, HSZ, HDDEDATA,
                          ULONG_PTR, ULONG_PTR)


class DDE(object):
    """Object containing all the DDE functions"""
    AccessData = get_winfunc(
        "user32", "DdeAccessData", LPBYTE, (HDDEDATA, LPDWORD))
    ClientTransaction = get_winfunc("user32", "DdeClientTransaction", HDDEDATA, (LPBYTE, DWORD, HCONV, HSZ, UINT, UINT, DWORD, LPDWORD))
    Connect = get_winfunc("user32", "DdeConnect", HCONV,
                          (DWORD, HSZ, HSZ, PCONVCONTEXT))
    CreateStringHandle = get_winfunc(
        "user32", "DdeCreateStringHandleW", HSZ, (DWORD, LPCWSTR, UINT))
    Disconnect = get_winfunc(
        "user32", "DdeDisconnect", BOOL, (HCONV,))
    GetLastError = get_winfunc(
        "user32", "DdeGetLastError", UINT, (DWORD,))
    Initialize = get_winfunc("user32", "DdeInitializeW", UINT,
                             (LPDWORD, DDECALLBACK, DWORD, DWORD))
    FreeDataHandle = get_winfunc(
        "user32", "DdeFreeDataHandle", BOOL, (HDDEDATA,))
    FreeStringHandle = get_winfunc(
        "user32", "DdeFreeStringHandle", BOOL, (DWORD, HSZ))
    QueryString = get_winfunc("user32", "DdeQueryStringA", DWORD,
                              (DWORD, HSZ, LPSTR, DWORD, c_int))
    UnaccessData = get_winfunc(
        "user32", "DdeUnaccessData", BOOL, (HDDEDATA,))
    Uninitialize = get_winfunc(
        "user32", "DdeUninitialize", BOOL, (DWORD,))


class DDEError(RuntimeError):
    """Exception raise when a DDE errpr occures."""
    def __init__(self, msg, idInst=None):
        if idInst is None:
            RuntimeError.__init__(self, msg)
        else:
            RuntimeError.__init__(
                self, "%s (err=%s)" % (msg, hex(DDE.GetLastError(idInst))))


class DDEClient(object):
    """The DDEClient class.

    Use this class to create and manage a connection to a service/topic.  To get
    classbacks subclass DDEClient and overwrite callback."""

    def __init__(self, service, topic):
        """Create a connection to a service/topic."""
        from ctypes import byref

        self._idInst = DWORD(0)
        self._hConv = HCONV()
        self.configdict = {}

        self._callback = DDECALLBACK(self._callback)
        res = DDE.Initialize(
            byref(self._idInst), self._callback, 0x00000010, 0)
        if res != DMLERR_NO_ERROR:
            raise DDEError("Unable to register with DDEML (err=%s)" % hex(res))

        hszService = DDE.CreateStringHandle(self._idInst, service, 1200)
        hszTopic = DDE.CreateStringHandle(self._idInst, topic, 1200)
        self._hConv = DDE.Connect(
            self._idInst, hszService, hszTopic, PCONVCONTEXT())
        DDE.FreeStringHandle(self._idInst, hszTopic)
        DDE.FreeStringHandle(self._idInst, hszService)
        if not self._hConv:
            raise DDEError("Unable to establish a conversation with server",
                           self._idInst)

    def __del__(self):
        """Cleanup any active connections."""
        if self._hConv:
            DDE.Disconnect(self._hConv)
        if self._idInst:
            DDE.Uninitialize(self._idInst)
        print 'DDECleint Close Connection'

    def advise(self, item, stop=False):
        """Request updates when DDE data changes."""

        hszItem = DDE.CreateStringHandle(self._idInst, item, 1200)
        hDdeData = DDE.ClientTransaction(LPBYTE(), 0, self._hConv, hszItem, CF_TEXT, XTYP_ADVSTOP if stop else XTYP_ADVSTART, TIMEOUT_ASYNC, LPDWORD())
        DDE.FreeStringHandle(self._idInst, hszItem)
        if not hDdeData:
            raise DDEError("Unable to %s advise" % (
                "stop" if stop else "start"), self._idInst)
        DDE.FreeDataHandle(hDdeData)

    def execute(self, command, timeout=5000):
        """Execute a DDE command."""
        pData = c_char_p(command)
        cbData = DWORD(len(command) + 1)
        hDdeData = DDE.ClientTransaction(pData, cbData, self._hConv, HSZ(
        ), CF_TEXT, XTYP_EXECUTE, timeout, LPDWORD())
        if not hDdeData:
            raise DDEError("Unable to send command", self._idInst)
        DDE.FreeDataHandle(hDdeData)

    def request(self, item, timeout=5000):
        """Request data from DDE service."""
        from ctypes import byref

        hszItem = DDE.CreateStringHandle(self._idInst, item, 1200)
        hDdeData = DDE.ClientTransaction(LPBYTE(), 0, self._hConv, hszItem, CF_TEXT, XTYP_REQUEST, timeout, LPDWORD())
        DDE.FreeStringHandle(self._idInst, hszItem)
        if not hDdeData:
            raise DDEError("Unable to request item", self._idInst)

        if timeout != TIMEOUT_ASYNC:
            pdwSize = DWORD(0)
            pData = DDE.AccessData(hDdeData, byref(pdwSize))
        #print 'PDATA->',pData, type(pData)
        if not pData:
            DDE.FreeDataHandle(hDdeData)
            raise DDEError("Unable to access data", self._idInst)
            # TODO: use pdwSize
            DDE.UnaccessData(hDdeData)
        else:
            #pData = None
            DDE.FreeDataHandle(hDdeData)
            return pData
        return None

    def callback(self, value, item=None):
        """Calback function for advice."""
        print "%s: %s" % (item, value)

    def _callback(self, wType, uFmt, hConv, hsz1, hsz2, hDdeData, dwData1, dwData2):
        from ctypes import byref
        if wType == XTYP_ADVDATA:
            from ctypes import create_string_buffer

        dwSize = DWORD(0)
        pData = DDE.AccessData(hDdeData, byref(dwSize))
        if pData:
            item = create_string_buffer('\000' * 128)
            DDE.QueryString(self._idInst, hsz2, item, 128, 1004)
            self.callback(pData, item.value)
            DDE.UnaccessData(hDdeData)
            return DDE_FACK
        return 0


def WinMSGLoop():
    """Run the main windows message loop."""
    from ctypes import POINTER, byref, c_ulong
    from ctypes.wintypes import BOOL, HWND, MSG, UINT

    LPMSG = POINTER(MSG)
    LRESULT = c_ulong
    GetMessage = get_winfunc(
        "user32", "GetMessageW", BOOL, (LPMSG, HWND, UINT, UINT))
    TranslateMessage = get_winfunc(
        "user32", "TranslateMessage", BOOL, (LPMSG,))
    # restype = LRESULT
    DispatchMessage = get_winfunc(
        "user32", "DispatchMessageW", LRESULT, (LPMSG,))

    msg = MSG()
    lpmsg = byref(msg)
    while GetMessage(lpmsg, HWND(), 0, 0) > 0:
        #print lpmsg, HWND()
        #print lpmsg, HWND()
        #print
        TranslateMessage(lpmsg)
        DispatchMessage(lpmsg)

################################################################################
request_item = ['price', 'volume', 'time']  # FIXME, get this from DB
################################################################################


def query(quote_list=[], out=''):
    if quote_list and out:

        # reset some variabale
        content = ""
        content_list = [0, 0, 0]
        next_list = []
        hour = 0
        minute = 0
        second = 0
        price = 0
        volume = 0
        origin_volume = 0

        try:
            fp = file(out)
            content = fp.read()
            fp.close()

        except:
            fp = open(out, "w")
            fp.close()

        # the out file format is repr in python list [time(),float(price),int(volume)]
        if fp and content:
                content_list = eval(content)
                try:
                    origin_volume = content_list[2]
                except:
                    pass

        for dd in quote_list:
            quote_time = dd.request(dd.configdict['time'])
            try:
                price = float(
                    dd.request(dd.configdict['price']))  # price float
            except:
                price = 0
            try:
                volume = int(
                    (dd.request(dd.configdict['volume'])))  # volumn integer
            except:
                volume = 0

            if quote_time:

                if quote_time.find(":") > 0:
                    # like HH:MM:SS, clean up
                    quote_time = quote_time[
                        quote_time.find(':') - 2:quote_time.rfind(':') + 3]
                    hour, minute, second = map(int, quote_time.split(':')[:3])
                elif len(quote_time) >= 5 and len(quote_time) <= 6:
                    second = int(quote_time[-2:])
                    minute = int(quote_time[-4:-2])
                    hour = int(quote_time[-6:-4])

                new_time = datetime.time(hour, minute, second)
                next_list = [new_time, price, volume]
                #print next_list

                if volume != origin_volume or origin_volume == 0:
                    # volume bigger than update
                    fp = open(out, "w")
                    fp.write(repr(next_list))
                    fp.close()
                    origin_volume = volume


def main_is_frozen():
    return (hasattr(sys, "frozen") or  # new py2exe
            hasattr(sys, "importers")  # old py2exe
            or imp.is_frozen("__main__"))  # tools/freeze


def get_main_dir():
    if main_is_frozen():
        # executable at app/
        return os.path.dirname(sys.executable)
    # app/quote/DDE.py
    quote_realpath = os.path.realpath(sys.argv[0])
    app_dir = os.path.dirname(os.path.dirname(quote_realpath))
    return app_dir


def main(commodity, config_ini, interval=0.3):
    #app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_dir = get_main_dir()
    #print app_dir
    configdict = defaultdict(dict)
    output_file = ''
    quote_dir = ''
    quote_dict = {}
    quote_config = {}
    quote_keyids = []

    if commodity and config_ini:
            configobj = ConfigObj(config_ini, encoding='utf-8')
            if configobj.get(commodity, False) and configobj[commodity].get('quote', False):
                quoteobj = configobj[commodity]['quote']
                for k, v in quoteobj.items():
                    if k.startswith('dde'):
                        # multiple dde server
                        key, subkey = k.split('_', 1)
                        if v:
                            configdict[key][subkey] = v

                mcode = quoteobj['mcode']
                ccode = quoteobj['ccode']

                if configobj[commodity].get('cdir', False):
                    quote_dir = os.path.join(configobj[commodity].get(
                        'cdir'), 'data', mcode, ccode)
                else:
                    # parent folder data/mcode/ccode
                    quote_dir = os.path.join(app_dir, 'data', mcode, ccode)

                if quote_dir and not os.path.isdir(quote_dir):
                    os.makedirs(quote_dir)

                output_file = os.path.join(quote_dir, ccode + ".now")
            # function to catch DDE error

            def gen_ddeclient(s='', t=''):
                dc = None
                try:
                    dc = DDEClient(s, t)
                except:
                    # dde error
                    dc = None
                return dc

            # check all needed configure
            for key, value in configdict.items():
                # safe check
                for k in request_item + ['server', 'topic']:
                    if k not in value.keys():
                        print "Do not config correctly !"
                        sys.exit()

                # retry time
                retry_time = time.time() + 10
                quote_key_id = '%s_%s' % (mcode, ccode)

                quote_config[quote_key_id] = value
                quote_keyids.append(quote_key_id)

                dde_instance = gen_ddeclient(value['server'], value['topic'])
                if dde_instance:
                    dde_instance.configdict = quote_config[quote_key_id]
                    quote_dict[quote_key_id] = dde_instance

                #DDE_INS = DDEClient(value['server'], value['topic'])
                #DDE_INS.configdict = value
                #quote_list.append(DDE_INS)
                #quote_dict[quote_key_id] = DDE_INS
            # Main loop
            # FIXME only retry for start up fails, not fail after dde client start
            #if quote_dict:
            try:
                while True:
                    query(quote_dict.values(), output_file)
                    time.sleep(interval)

                    # retry
                    if len(quote_dict.keys()) != len(quote_keyids) and time.time() > retry_time:
                        # some dde started failed
                        retry_time = time.time() + 10
                        print "Next retry time ", retry_time
                        for keyid in quote_keyids:
                            if keyid not in quote_dict.keys():
                                dde_instance = gen_ddeclient(quote_config[keyid]['server'], quote_config[keyid]['topic'])
                                if dde_instance:
                                    dde_instance.configdict = quote_config[
                                        keyid]
                                    quote_dict[quote_key_id] = dde_instance
            except:
                print traceback.format_exc()
            finally:
                print 'Execute Finally'
                for dde_to_kill in quote_dict.values():
                    dde_to_kill.__del__()


if __name__ == '__main__':

    # command line tool wrapper
    parser = argparse.ArgumentParser("""
    run windows DDE client to send requst to query DDE infomation.
    """)

    parser.add_argument('-i', '--interval', type=float, default=0.3,
                        help="The interval in second to check and request DDE topic. (default is 0.3 second )")

    parser.add_argument(
        '-com', '--commodity', help="The unique commodity name code.")
    parser.add_argument(
        '-c', '--config', help="The path to commodity configure file.")

    args = parser.parse_args()

    if args.commodity and args.config and os.path.isfile(args.config):
        main(args.commodity, args.config, args.interval)
    else:
        print parser.print_help()
