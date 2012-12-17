#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A tool listen to DDE SERVER

ddecleint.py [options] outputfile 
 
    -i interval the timer for check the strategy, default 0.5 second

    --config=ddeconfig file file name must end with .py encoding utf-8

    example of config file:
    
    DDESERVERS = [
        {
            'server': u'DDEEXCEL',
            'topic': u'FUTURETXFA0',
            'price': u'市價',
            'total': u'累計交易量',
            'time': u'時間',
        },
        #{
        #    'server': u'',
        #    'topic': u'',
        #    'price': u'',
        #    'total': u'',
        #    'time': u'',
        #    },
    ]


this function need to install win32 package for python
Author: TerryH, email: terryh.tp at gmail.com,
License: BSD
"""
import time
import datetime
import sys
import codecs
import getopt
import re
import codecs

re_dde = re.compile("DDESERVERS.?=.?\[.*?\]",re.DOTALL)

try:
    import win32ui
    import dde
except:
    print "You must have pywin32 install, http://sourceforge.net/projects/pywin32/"
    sys.exit()

try:
    import cPickle as pickle
except:
    import pickle

class DDEClient(object):
    
    def __init__(self,server="",topic=""):
        # having our dde conversation fifrst
        self.ddeclient = dde.CreateServer()
        self.ddeclient.Create("AutoTrader")
        self.conversation = dde.CreateConversation(self.ddeclient)
        self.ddeserver = ""
        self.ddedata = ""
        self.configdict={}
        self.status = 0
        if server and topic:
            self.ddeserver = server
            self.ddedata = topic 
            self.connect()
    
    def resetclient(self):
        # having our dde conversation fifrst
        try:
            self.ddeclient.Destroy()
        except:
            pass
        
        self.ddeclient = dde.CreateServer()
        self.ddeclient.Create("AutoClient")
        self.conversation = dde.CreateConversation(self.ddeclient)
    
    def disconnect(self):
        # having our dde conversation fifrst
        try:
            # clean up
            self.ddeclient.Destroy()
            self.ddeserver = ""
            self.ddedata =  ""
        except:
            pass
    
    def connect(self, server="", topic=""):
        if server and topic:
            self.ddeserver = server
            self.ddedata = topic
        if self.ddeserver and self.ddedata:

            try:
                if self.conversation.Connected()==0:
                    self.conversation.ConnectTo(self.ddeserver,self.ddedata)
                    self.status = 1
            except:
                print "DDE connetion fail"
                self.status = 0
            
    def request(self, item=u""):
        if self.status and item:
            # FIXME because self.conversation.Connected() is break, so we use our own self.status
            try:
                value = self.conversation.Request(item)
                return value

            except:
                print "DDE request %s fail" % (item)
                self.status=0
        else:
            while not self.status:
                print "DDE connection fail or no topic"
                self.resetclient()
                self.connect()
                time.sleep(5)

def dde_query(dde_list=[],out=""):
    if dde_list and out:
        # reset some variabale
        content=""
        cl = [0,0,0]
        dt = 0
        HH = 0
        MM = 0
        SS = 0
        price = 0
        volume = 0
        dirty = 0
        dde_dt = 0
        dde_price = 0
        dde_volume = 0
        nl = []
        try:
            fp = file(out)
            content = fp.read()
            fp.close()

        except:
            fp = open(out,"w")
            fp.close()

        # the out file format is pickle in python list [time(),int(price),int(volume)]
        if fp:
            if content: 
                cl = pickle.loads(content)

                dde_volume = cl[2] 
            
        for dd in dde_list:
            tt = dd.request(dd.configdict['time'])
            try:
                pp = int(float(dd.request(dd.configdict['price'])))
            except:
                pp = 0
            try:
                vv = int(float(dd.request(dd.configdict['total'])))
            except:
                vv = 0
            if tt:
                if tt.find(":")>0:
                    # like HH:MM:SS
                    m1 = tt.find(":")
                    m2 = tt.rfind(":")
                    HH = int(tt[m1-2:m1])
                    MM = int(tt[m1+1:m2])
                    SS = int(tt[m2+1:m2+3])
                elif len(tt)>=5 and len(tt)<=6:
                    SS=int(tt[-2:])
                    MM=int(tt[-4:-2])
                    HH=int(tt[-6:-4])
                
                tt = datetime.time(HH,MM,SS)
                nl = [tt,pp,vv]
                #print nl
                if vv != dde_volume :
                    # volume bigger than update
                    fp = open(out,"w")
                    pickle.dump(nl,fp)
                    fp.close()
                    
                    dde_volume = vv

if __name__ == '__main__':
    # take from HTS for example
    #server,topic = "DDEEXCEL","FUTUREMXFA0"
    #DDE = DDEClient(server,topic)
    #print DDE.request(u"時間")
    
    opts, args = getopt.getopt(sys.argv[1:], "i:", 
                 ["config=",])
    
    if len(args) > 0:
        interval = 0.5
        config = ""
        out = args[0]
        cmd = ''

        for o, a in opts:
            if o in ("-i"):
                interval = float(a)
            elif o in ("--config"):
                config = a

        if config and  out and interval:  
            
            if config:
                
                ddeconfig = codecs.open(config, encoding='utf-8').read()

                if re_dde.search(ddeconfig):
                    cmd = re_dde.search(ddeconfig).group()
                
                exec(cmd)
                dde_list = []
                # FIXME find no way to create two dde Server at same time
                DDESERVERS = DDESERVERS[:1]
                for c in DDESERVERS:
                    if "server" in c and "topic" in c and 'price' in c and \
                        'time' in c and 'total' in c:
                        
                        #print c['server'],c['topic']
                        DDE = DDEClient(c['server'],c['topic'])
                        DDE.configdict = c
                        dde_list.append(DDE) 
                
            if dde_list:

                while True:
                    dde_query(dde_list,out) 
                    time.sleep(interval)
            
    else:
        print __doc__
        sys.exit()
