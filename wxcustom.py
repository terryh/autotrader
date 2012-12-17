# -*- coding: utf-8 -*- 

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent, *args):
        wx.ListCtrl.__init__(self, parent, *args)
        CheckListCtrlMixin.__init__(self)
    
    def OnCheckItem(self, index, flag):
        # proxy to parent method, for easy control
        self.GetParent().OnCheckItem(index, flag)
    
