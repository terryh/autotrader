#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join
from glob import glob
import cx_Freeze
#import sys

from autotrader import __version__

data_files = []
data_files += glob(join('Microsoft.VC90.CRT', '*'))
data_files += glob(join('function', '*'))
data_files += glob(join('quote', '*'))
data_files += glob(join('config', '*'))
data_files += glob(join('locale', '*'))

includes = []
packages = []

# self packages
packages.append('quote')

# third party packages
packages.append('pytz')
packages.append('talib')
packages.append('wx')
packages.append('enable')  # FIXME enable.images not able to package on freeze
packages.append('pyface')  # FIXME pyface.images not able to package on freeze

packages.append('traits')
packages.append('traitsui')

# fix not include problem ;-(
# pytz.zonefile, enable.images , pyface.images

zip_files = []
zoneinfo_path = "C:\\Python27\Lib\site-packages\pytz\zoneinfo"
should_have_in_zip = [
    "C:\\Python27\Lib\site-packages\pytz\zoneinfo",
    "C:\\Python27\Lib\site-packages\enable\images",
    "C:\\Python27\Lib\site-packages\pyface\images",
]

for walk_path in should_have_in_zip:
    for root, dirs, files in os.walk(walk_path):
        for f in files:
            fn = os.path.join(root, f)
            zip_files.append((fn, fn.split('\site-packages\\')[1]))

base = None
#if sys.platform == "win32":
        #base = "Win32GUI"

buildOptions = {
    "packages": packages,
    "optimize": 2,
    #"create-shared-zip": True,
    "include_files": data_files,
    "zip_includes": zip_files,
    "excludes": [
    'Tkinter',
    'IPython',
    #'pyreadline',
    #'_ssl',
    #'locale',
    #'calendar'
    'Tkconstants',
    'Tkinter',
    'tcl',
    'tk',
    '_imagingtk',
    'curses',
    'PIL._imagingtk',
    'ImageTk',
    'PIL.ImageTk',
    'FixTk',
    'bsddb',
    'email',
    'pywin.debugger',
    'pywin.debugger.dbgcon',
    'matplotlib'
    ],
    "includes": includes
}
executables = [
    #cx_Freeze.Executable("autotrader.py", icon="icons/trade.ico", base = base),
    cx_Freeze.Executable(
        "autotrader.py", icon="icons/trade.ico", base="Win32GUI"),
    cx_Freeze.Executable(
        "quote/DDE.py", icon="icons/dde.ico", base=None),
    cx_Freeze.Executable("quote/quoteworker.py",
                         icon="icons/quoteworker.ico", base=None),
    cx_Freeze.Executable(
        "trader.py", icon="icons/trader.ico", base=None),
    cx_Freeze.Executable(
        "tools/taifex.py", icon="icons/compile.ico", base=None),
    cx_Freeze.Executable("pricechart.py", base="Win32GUI"),
]

cx_Freeze.setup(
    name="autotrader",
    version=__version__,
    description="AutoTrader",
    executables=executables,
    options=dict(build_exe=buildOptions))
