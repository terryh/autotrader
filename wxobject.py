# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Oct  8 2012)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from wxcustom import CheckListCtrl
import wx.lib.masked as masked

import gettext
_ = gettext.gettext

###########################################################################
## Class MyFrame
###########################################################################

class MyFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"AUTOTRADER"), pos = wx.DefaultPosition, size = wx.Size( 800,450 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( -1,-1 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVEBORDER ) )
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.menumain = wx.Menu()
		self.newmarket = wx.MenuItem( self.menumain, wx.ID_ANY, _(u"New Market")+ u"\t" + u"CTRL+M", wx.EmptyString, wx.ITEM_NORMAL )
		self.newmarket.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_ADD_BOOKMARK,  ) )
		self.menumain.AppendItem( self.newmarket )
		
		self.newcommodity = wx.MenuItem( self.menumain, wx.ID_ANY, _(u"New Commodity")+ u"\t" + u"CTRL+G", wx.EmptyString, wx.ITEM_NORMAL )
		self.newcommodity.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_NEW,  ) )
		self.menumain.AppendItem( self.newcommodity )
		
		self.newstrategy = wx.MenuItem( self.menumain, wx.ID_ANY, _(u"New Strategy")+ u"\t" + u"CTRL+S", wx.EmptyString, wx.ITEM_NORMAL )
		self.newstrategy.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_LIST_VIEW,  ) )
		self.menumain.AppendItem( self.newstrategy )
		
		self.menumain.AppendSeparator()
		
		self.quit = wx.MenuItem( self.menumain, wx.ID_ANY, _(u"Exit")+ u"\t" + u"CTRL+X", wx.EmptyString, wx.ITEM_NORMAL )
		self.quit.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_QUIT,  ) )
		self.menumain.AppendItem( self.quit )
		
		self.m_menubar1.Append( self.menumain, _(u"New") ) 
		
		self.menuabout = wx.Menu()
		self.about = wx.MenuItem( self.menuabout, wx.ID_ANY, _(u"About"), wx.EmptyString, wx.ITEM_NORMAL )
		self.about.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_HELP_PAGE,  ) )
		self.menuabout.AppendItem( self.about )
		
		self.m_menubar1.Append( self.menuabout, _(u"About") ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.bar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		vSizer = wx.BoxSizer( wx.VERTICAL )
		
		bSizer16 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer20 = wx.BoxSizer( wx.HORIZONTAL )
		
		sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Market") ), wx.VERTICAL )
		
		self.mctrl = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_HRULES|wx.LC_REPORT|wx.LC_SINGLE_SEL )
		self.mctrl.SetToolTipString( _(u"Manage market information") )
		
		sbSizer8.Add( self.mctrl, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer20.Add( sbSizer8, 1, wx.EXPAND, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"System log") ), wx.VERTICAL )
		
		self.log = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		self.log.SetMaxLength( 0 ) 
		sbSizer9.Add( self.log, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer20.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		
		bSizer16.Add( bSizer20, 1, wx.EXPAND, 5 )
		
		
		vSizer.Add( bSizer16, 5, wx.EXPAND, 5 )
		
		bSizer17 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer201 = wx.BoxSizer( wx.HORIZONTAL )
		
		sbSizer81 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Commodity") ), wx.VERTICAL )
		
		self.cctrl = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_HRULES|wx.LC_REPORT|wx.LC_SINGLE_SEL )
		self.cctrl.SetToolTipString( _(u"Manage commodity information") )
		
		sbSizer81.Add( self.cctrl, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer201.Add( sbSizer81, 1, wx.EXPAND, 5 )
		
		sbSizer10 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Strategy") ), wx.VERTICAL )
		
		self.sctrl = CheckListCtrl( self,  wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_HRULES|wx.LC_REPORT|wx.LC_SINGLE_SEL )
		self.sctrl.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.onStrategyActive )
		sbSizer10.Add( self.sctrl, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer201.Add( sbSizer10, 1, wx.EXPAND, 5 )
		
		
		bSizer17.Add( bSizer201, 1, wx.EXPAND, 5 )
		
		
		vSizer.Add( bSizer17, 5, wx.EXPAND, 5 )
		
		
		self.SetSizer( vSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.onQuit )
		self.Bind( wx.EVT_MENU, self.onMarket, id = self.newmarket.GetId() )
		self.Bind( wx.EVT_MENU, self.onCommodity, id = self.newcommodity.GetId() )
		self.Bind( wx.EVT_MENU, self.onStrategy, id = self.newstrategy.GetId() )
		self.Bind( wx.EVT_MENU, self.onQuit, id = self.quit.GetId() )
		self.Bind( wx.EVT_MENU, self.onAbout, id = self.about.GetId() )
		self.mctrl.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.onMarketActive )
		self.cctrl.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.onCommodityActive )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onQuit( self, event ):
		event.Skip()
	
	def onMarket( self, event ):
		event.Skip()
	
	def onCommodity( self, event ):
		event.Skip()
	
	def onStrategy( self, event ):
		event.Skip()
	
	
	def onAbout( self, event ):
		event.Skip()
	
	def onMarketActive( self, event ):
		event.Skip()
	
	def onCommodityActive( self, event ):
		event.Skip()
	

###########################################################################
## Class M
###########################################################################

class M ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Market"), pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		gSizer3 = wx.GridSizer( 4, 2, 0, 0 )
		
		self.statictext = wx.StaticText( self, wx.ID_ANY, _(u"Market Name"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext.Wrap( -1 )
		gSizer3.Add( self.statictext, 0, wx.ALL, 5 )
		
		self.mname = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.mname.SetMaxLength( 0 ) 
		gSizer3.Add( self.mname, 0, wx.ALL, 5 )
		
		self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, _(u"Market Code"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText15.Wrap( -1 )
		gSizer3.Add( self.m_staticText15, 0, wx.ALL, 5 )
		
		self.mcode = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.mcode.SetMaxLength( 0 ) 
		gSizer3.Add( self.mcode, 0, wx.ALL, 5 )
		
		self.m_staticText141 = wx.StaticText( self, wx.ID_ANY, _(u"Market Time Zone"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText141.Wrap( -1 )
		gSizer3.Add( self.m_staticText141, 0, wx.ALL, 5 )
		
		mtimezoneChoices = []
		self.mtimezone = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, mtimezoneChoices, 0 )
		self.mtimezone.SetSelection( 0 )
		gSizer3.Add( self.mtimezone, 0, wx.ALL, 5 )
		
		self.m_staticText17 = wx.StaticText( self, wx.ID_ANY, _(u"Session Clear Time"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText17.Wrap( -1 )
		gSizer3.Add( self.m_staticText17, 0, wx.ALL, 5 )
		
		self.mclear = masked.TimeCtrl( self, -1, name="", format='24HHMM', fmt24hr=True )
		
		gSizer3.Add( self.mclear, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( gSizer3, 2, wx.EXPAND, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Session 1") ), wx.VERTICAL )
		
		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, _(u"Start"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText16.Wrap( -1 )
		bSizer10.Add( self.m_staticText16, 0, wx.ALL, 5 )
		
		self.s1_start = masked.TimeCtrl( self, -1, name="l", format='24HHMM', fmt24hr=True )
		
		bSizer10.Add( self.s1_start, 0, wx.ALL, 5 )
		
		self.m_staticText171 = wx.StaticText( self, wx.ID_ANY, _(u"End"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText171.Wrap( -1 )
		bSizer10.Add( self.m_staticText171, 0, wx.ALL, 5 )
		
		self.s1_end = masked.TimeCtrl( self, -1, name="l", format='24HHMM', fmt24hr=True)
		
		bSizer10.Add( self.s1_end, 0, wx.ALL, 5 )
		
		
		sbSizer6.Add( bSizer10, 1, wx.EXPAND, 5 )
		
		
		bSizer7.Add( sbSizer6, 1, wx.EXPAND, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Session 2") ), wx.VERTICAL )
		
		bSizer101 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText161 = wx.StaticText( self, wx.ID_ANY, _(u"Start"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText161.Wrap( -1 )
		bSizer101.Add( self.m_staticText161, 0, wx.ALL, 5 )
		
		self.s2_start = masked.TimeCtrl( self, -1, name="", format='24HHMM', fmt24hr=True )
		
		bSizer101.Add( self.s2_start, 0, wx.ALL, 5 )
		
		self.m_staticText1711 = wx.StaticText( self, wx.ID_ANY, _(u"End"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1711.Wrap( -1 )
		bSizer101.Add( self.m_staticText1711, 0, wx.ALL, 5 )
		
		self.s2_end = masked.TimeCtrl( self, -1, name="", format='24HHMM', fmt24hr=True )
		
		bSizer101.Add( self.s2_end, 0, wx.ALL, 5 )
		
		
		sbSizer9.Add( bSizer101, 1, wx.EXPAND, 5 )
		
		
		bSizer7.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Trade Day") ), wx.VERTICAL )
		
		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.d0 = wx.CheckBox( self, wx.ID_ANY, _(u"Sun"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.d0, 0, wx.ALL, 5 )
		
		self.d1 = wx.CheckBox( self, wx.ID_ANY, _(u"Mon"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.d1.SetValue(True) 
		bSizer12.Add( self.d1, 0, wx.ALL, 5 )
		
		self.d2 = wx.CheckBox( self, wx.ID_ANY, _(u"Tue"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.d2.SetValue(True) 
		bSizer12.Add( self.d2, 0, wx.ALL, 5 )
		
		self.d3 = wx.CheckBox( self, wx.ID_ANY, _(u"Wed"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.d3.SetValue(True) 
		bSizer12.Add( self.d3, 0, wx.ALL, 5 )
		
		self.d4 = wx.CheckBox( self, wx.ID_ANY, _(u"Thu"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.d4.SetValue(True) 
		bSizer12.Add( self.d4, 0, wx.ALL, 5 )
		
		self.d5 = wx.CheckBox( self, wx.ID_ANY, _(u"Fri"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.d5.SetValue(True) 
		bSizer12.Add( self.d5, 0, wx.ALL, 5 )
		
		self.d6 = wx.CheckBox( self, wx.ID_ANY, _(u"Sat"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.d6, 0, wx.ALL, 5 )
		
		
		sbSizer11.Add( bSizer12, 1, wx.EXPAND, 5 )
		
		
		bSizer7.Add( sbSizer11, 1, wx.EXPAND, 5 )
		
		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.submit = wx.Button( self, wx.ID_ANY, _(u"Submit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.submit, 1, wx.ALL, 20 )
		
		self.cancel = wx.Button( self, wx.ID_ANY, _(u"Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.cancel, 1, wx.ALL, 20 )
		
		self.delete = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.delete, 1, wx.ALL, 20 )
		
		
		bSizer7.Add( bSizer9, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer7 )
		self.Layout()
		bSizer7.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.mcode.Bind( wx.EVT_CHAR, self.on_Code )
		self.submit.Bind( wx.EVT_BUTTON, self.onSubmit )
		self.cancel.Bind( wx.EVT_BUTTON, self.onCancel )
		self.delete.Bind( wx.EVT_BUTTON, self.onDelete )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_Code( self, event ):
		event.Skip()
	
	def onSubmit( self, event ):
		event.Skip()
	
	def onCancel( self, event ):
		event.Skip()
	
	def onDelete( self, event ):
		event.Skip()
	

###########################################################################
## Class C
###########################################################################

class C ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Commodity"), pos = wx.DefaultPosition, size = wx.Size( 580,300 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer11 = wx.BoxSizer( wx.VERTICAL )
		
		gSizer1 = wx.GridSizer( 6, 2, 0, 0 )
		
		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, _(u"Commodity Name"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		gSizer1.Add( self.m_staticText7, 0, wx.ALL, 5 )
		
		self.cname = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.cname.SetMaxLength( 0 ) 
		gSizer1.Add( self.cname, 0, wx.ALL, 5 )
		
		self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, _(u"Commodity Code"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		gSizer1.Add( self.m_staticText10, 0, wx.ALL, 5 )
		
		self.ccode = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.ccode.SetMaxLength( 0 ) 
		gSizer1.Add( self.ccode, 0, wx.ALL, 5 )
		
		self.m_staticText101 = wx.StaticText( self, wx.ID_ANY, _(u"Point Value or Scale"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText101.Wrap( -1 )
		gSizer1.Add( self.m_staticText101, 0, wx.ALL, 5 )
		
		self.cpov = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.cpov.SetMaxLength( 0 ) 
		gSizer1.Add( self.cpov, 0, wx.ALL, 5 )
		
		self.m_staticText161 = wx.StaticText( self, wx.ID_ANY, _(u"Market Code"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText161.Wrap( -1 )
		gSizer1.Add( self.m_staticText161, 0, wx.ALL, 5 )
		
		mcodeChoices = []
		self.mcode = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, mcodeChoices, 0 )
		self.mcode.SetSelection( 0 )
		gSizer1.Add( self.mcode, 0, wx.ALL, 5 )
		
		self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, _(u"Quote Source Directory"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText15.Wrap( -1 )
		gSizer1.Add( self.m_staticText15, 0, wx.ALL, 5 )
		
		csourceChoices = []
		self.csource = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, csourceChoices, 0 )
		self.csource.SetSelection( 0 )
		gSizer1.Add( self.csource, 0, wx.ALL, 5 )
		
		self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, _(u"Quote Folder"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText16.Wrap( -1 )
		gSizer1.Add( self.m_staticText16, 0, wx.ALL, 5 )
		
		self.cdir = wx.DirPickerCtrl( self, wx.ID_ANY, wx.EmptyString, _(u"Select a folder"), wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE )
		self.cdir.SetToolTipString( _(u"Quote Folder for real time data processing, better at a ram disk folder.") )
		
		gSizer1.Add( self.cdir, 0, wx.ALL, 5 )
		
		
		bSizer11.Add( gSizer1, 5, wx.EXPAND, 5 )
		
		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.submit = wx.Button( self, wx.ID_ANY, _(u"Submit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.submit, 1, wx.ALL, 5 )
		
		self.config = wx.Button( self, wx.ID_ANY, _(u"Config Quote Surce"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.config.Enable( False )
		
		bSizer12.Add( self.config, 2, wx.ALL, 5 )
		
		self.history = wx.Button( self, wx.ID_ANY, _(u"Show History Quote"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.history.Enable( False )
		self.history.SetToolTipString( _(u"The Folder store history, running strategy will copy nessay data to Quote Source Directory.") )
		
		bSizer12.Add( self.history, 2, wx.ALL, 5 )
		
		self.delete = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.delete, 1, wx.ALL, 5 )
		
		
		bSizer11.Add( bSizer12, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer11 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.mcode.Bind( wx.EVT_CHOICE, self.onMcode )
		self.csource.Bind( wx.EVT_CHOICE, self.onSource )
		self.submit.Bind( wx.EVT_BUTTON, self.onSubmit )
		self.config.Bind( wx.EVT_BUTTON, self.onConfig )
		self.history.Bind( wx.EVT_BUTTON, self.onHistory )
		self.delete.Bind( wx.EVT_BUTTON, self.onDelete )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onMcode( self, event ):
		event.Skip()
	
	def onSource( self, event ):
		event.Skip()
	
	def onSubmit( self, event ):
		event.Skip()
	
	def onConfig( self, event ):
		event.Skip()
	
	def onHistory( self, event ):
		event.Skip()
	
	def onDelete( self, event ):
		event.Skip()
	

###########################################################################
## Class D
###########################################################################

class D ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"DDE"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		gSizer3 = wx.GridSizer( 1, 2, 0, 0 )
		
		self.statictext = wx.StaticText( self, wx.ID_ANY, _(u"Market Code"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext.Wrap( -1 )
		gSizer3.Add( self.statictext, 0, wx.ALL, 5 )
		
		self.mcode = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		self.mcode.SetMaxLength( 0 ) 
		gSizer3.Add( self.mcode, 0, wx.ALL, 5 )
		
		self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, _(u"Commodity Code"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText15.Wrap( -1 )
		gSizer3.Add( self.m_staticText15, 0, wx.ALL, 5 )
		
		self.ccode = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		self.ccode.SetMaxLength( 0 ) 
		gSizer3.Add( self.ccode, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( gSizer3, 1, wx.EXPAND, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"DDE 1") ), wx.VERTICAL )
		
		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText162 = wx.StaticText( self, wx.ID_ANY, _(u"Server"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText162.Wrap( -1 )
		bSizer10.Add( self.m_staticText162, 0, wx.ALL, 5 )
		
		self.dde1_server = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde1_server.SetMaxLength( 0 ) 
		bSizer10.Add( self.dde1_server, 0, wx.ALL, 5 )
		
		self.m_staticText163 = wx.StaticText( self, wx.ID_ANY, _(u"Topic"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText163.Wrap( -1 )
		bSizer10.Add( self.m_staticText163, 0, wx.ALL, 5 )
		
		self.dde1_topic = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde1_topic.SetMaxLength( 0 ) 
		bSizer10.Add( self.dde1_topic, 0, wx.ALL, 5 )
		
		self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, _(u"Time"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText16.Wrap( -1 )
		bSizer10.Add( self.m_staticText16, 0, wx.ALL, 5 )
		
		self.dde1_time = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde1_time.SetMaxLength( 0 ) 
		bSizer10.Add( self.dde1_time, 0, wx.ALL, 5 )
		
		self.m_staticText171 = wx.StaticText( self, wx.ID_ANY, _(u"Price"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText171.Wrap( -1 )
		bSizer10.Add( self.m_staticText171, 0, wx.ALL, 5 )
		
		self.dde1_price = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde1_price.SetMaxLength( 0 ) 
		bSizer10.Add( self.dde1_price, 0, wx.ALL, 5 )
		
		self.m_staticText1712 = wx.StaticText( self, wx.ID_ANY, _(u"Volume"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1712.Wrap( -1 )
		bSizer10.Add( self.m_staticText1712, 0, wx.ALL, 5 )
		
		self.dde1_volume = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde1_volume.SetMaxLength( 0 ) 
		bSizer10.Add( self.dde1_volume, 0, wx.ALL, 5 )
		
		
		sbSizer6.Add( bSizer10, 1, wx.EXPAND, 5 )
		
		
		bSizer7.Add( sbSizer6, 1, wx.EXPAND, 5 )
		
		sbSizer61 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"DDE 2") ), wx.VERTICAL )
		
		bSizer101 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText1621 = wx.StaticText( self, wx.ID_ANY, _(u"Server"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1621.Wrap( -1 )
		bSizer101.Add( self.m_staticText1621, 0, wx.ALL, 5 )
		
		self.dde2_server = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde2_server.SetMaxLength( 0 ) 
		bSizer101.Add( self.dde2_server, 0, wx.ALL, 5 )
		
		self.m_staticText1631 = wx.StaticText( self, wx.ID_ANY, _(u"Topic"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1631.Wrap( -1 )
		bSizer101.Add( self.m_staticText1631, 0, wx.ALL, 5 )
		
		self.dde2_topic = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde2_topic.SetMaxLength( 0 ) 
		bSizer101.Add( self.dde2_topic, 0, wx.ALL, 5 )
		
		self.m_staticText161 = wx.StaticText( self, wx.ID_ANY, _(u"Time"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText161.Wrap( -1 )
		bSizer101.Add( self.m_staticText161, 0, wx.ALL, 5 )
		
		self.dde2_time = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde2_time.SetMaxLength( 0 ) 
		bSizer101.Add( self.dde2_time, 0, wx.ALL, 5 )
		
		self.m_staticText1711 = wx.StaticText( self, wx.ID_ANY, _(u"Price"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1711.Wrap( -1 )
		bSizer101.Add( self.m_staticText1711, 0, wx.ALL, 5 )
		
		self.dde2_price = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde2_price.SetMaxLength( 0 ) 
		bSizer101.Add( self.dde2_price, 0, wx.ALL, 5 )
		
		self.m_staticText17121 = wx.StaticText( self, wx.ID_ANY, _(u"Volume"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText17121.Wrap( -1 )
		bSizer101.Add( self.m_staticText17121, 0, wx.ALL, 5 )
		
		self.dde2_volume = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dde2_volume.SetMaxLength( 0 ) 
		bSizer101.Add( self.dde2_volume, 0, wx.ALL, 5 )
		
		
		sbSizer61.Add( bSizer101, 1, wx.EXPAND, 5 )
		
		
		bSizer7.Add( sbSizer61, 1, wx.EXPAND, 5 )
		
		sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Tracking Trade Time Period") ), wx.VERTICAL )
		
		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.min1 = wx.CheckBox( self, wx.ID_ANY, _(u"1 MIN"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.min1, 0, wx.ALL, 5 )
		
		self.min2 = wx.CheckBox( self, wx.ID_ANY, _(u"2 MIN"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.min2, 0, wx.ALL, 5 )
		
		self.min3 = wx.CheckBox( self, wx.ID_ANY, _(u"3 MIN"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.min3, 0, wx.ALL, 5 )
		
		self.min5 = wx.CheckBox( self, wx.ID_ANY, _(u"5 MIN"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.min5, 0, wx.ALL, 5 )
		
		self.min15 = wx.CheckBox( self, wx.ID_ANY, _(u"15 MIN"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.min15, 0, wx.ALL, 5 )
		
		self.min30 = wx.CheckBox( self, wx.ID_ANY, _(u"30 MIN"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.min30, 0, wx.ALL, 5 )
		
		self.hour1 = wx.CheckBox( self, wx.ID_ANY, _(u"1 HOUR"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.hour1, 0, wx.ALL, 5 )
		
		self.day1 = wx.CheckBox( self, wx.ID_ANY, _(u"1 DAY"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.day1, 0, wx.ALL, 5 )
		
		
		sbSizer11.Add( bSizer12, 1, wx.EXPAND, 5 )
		
		
		bSizer7.Add( sbSizer11, 1, wx.EXPAND, 5 )
		
		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.submit = wx.Button( self, wx.ID_ANY, _(u"Submit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.submit, 1, wx.ALL, 20 )
		
		self.cancel = wx.Button( self, wx.ID_ANY, _(u"Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.cancel, 1, wx.ALL, 20 )
		
		self.delete = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.delete, 1, wx.ALL, 20 )
		
		
		bSizer7.Add( bSizer9, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer7 )
		self.Layout()
		bSizer7.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.ccode.Bind( wx.EVT_CHAR, self.on_Code )
		self.submit.Bind( wx.EVT_BUTTON, self.onSubmit )
		self.cancel.Bind( wx.EVT_BUTTON, self.onCancel )
		self.delete.Bind( wx.EVT_BUTTON, self.onDelete )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_Code( self, event ):
		event.Skip()
	
	def onSubmit( self, event ):
		event.Skip()
	
	def onCancel( self, event ):
		event.Skip()
	
	def onDelete( self, event ):
		event.Skip()
	

###########################################################################
## Class S
###########################################################################

class S ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Strategy"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		gSizer3 = wx.GridSizer( 5, 2, 0, 0 )
		
		self.statictext = wx.StaticText( self, wx.ID_ANY, _(u"Strategy file"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext.Wrap( -1 )
		gSizer3.Add( self.statictext, 0, wx.ALL, 5 )
		
		self.strategyfile = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, _(u"Select a file"), u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
		gSizer3.Add( self.strategyfile, 0, wx.ALL, 5 )
		
		self.m_staticText152 = wx.StaticText( self, wx.ID_ANY, _(u"Commodity Code"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText152.Wrap( -1 )
		gSizer3.Add( self.m_staticText152, 0, wx.ALL, 5 )
		
		ccodeChoices = []
		self.ccode = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ccodeChoices, 0 )
		self.ccode.SetSelection( 0 )
		gSizer3.Add( self.ccode, 0, wx.ALL, 5 )
		
		self.m_staticText1521 = wx.StaticText( self, wx.ID_ANY, _(u"Trade time period"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1521.Wrap( -1 )
		gSizer3.Add( self.m_staticText1521, 0, wx.ALL, 5 )
		
		periodChoices = []
		self.period = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, periodChoices, 0 )
		self.period.SetSelection( 0 )
		gSizer3.Add( self.period, 0, wx.ALL, 5 )
		
		self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, _(u"Max number of bars strategy will use"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText15.Wrap( -1 )
		gSizer3.Add( self.m_staticText15, 0, wx.ALL, 5 )
		
		self.num = wx.TextCtrl( self, wx.ID_ANY, _(u"300"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.num.SetMaxLength( 0 ) 
		gSizer3.Add( self.num, 0, wx.ALL, 5 )
		
		self.m_staticText151 = wx.StaticText( self, wx.ID_ANY, _(u"Commision cost per unit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText151.Wrap( -1 )
		gSizer3.Add( self.m_staticText151, 0, wx.ALL, 5 )
		
		self.cost = wx.TextCtrl( self, wx.ID_ANY, _(u"0"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.cost.SetMaxLength( 0 ) 
		gSizer3.Add( self.cost, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( gSizer3, 4, wx.EXPAND, 5 )
		
		sbSizer61 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Back test period") ), wx.VERTICAL )
		
		bSizer101 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText161 = wx.StaticText( self, wx.ID_ANY, _(u"Start"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText161.Wrap( -1 )
		bSizer101.Add( self.m_staticText161, 0, wx.ALL, 5 )
		
		self.start = wx.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT )
		bSizer101.Add( self.start, 0, wx.ALL, 5 )
		
		self.m_staticText1711 = wx.StaticText( self, wx.ID_ANY, _(u"End"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1711.Wrap( -1 )
		bSizer101.Add( self.m_staticText1711, 0, wx.ALL, 5 )
		
		self.end = wx.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT )
		bSizer101.Add( self.end, 0, wx.ALL, 5 )
		
		self.m_staticText17111 = wx.StaticText( self, wx.ID_ANY, _(u"History Quote File"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText17111.Wrap( -1 )
		self.m_staticText17111.SetToolTipString( _(u"You sould pick a longer history file for backtest.") )
		
		bSizer101.Add( self.m_staticText17111, 0, wx.ALL, 5 )
		
		self.historyfile = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, _(u"Select a file"), u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
		bSizer101.Add( self.historyfile, 0, wx.ALL, 5 )
		
		self.backtest = wx.Button( self, wx.ID_ANY, _(u"Back test"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer101.Add( self.backtest, 0, wx.ALL, 5 )
		
		
		sbSizer61.Add( bSizer101, 1, wx.EXPAND, 5 )
		
		
		bSizer7.Add( sbSizer61, 1, wx.EXPAND, 5 )
		
		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.run = wx.CheckBox( self, wx.ID_ANY, _(u"Running"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.run, 1, wx.ALL, 20 )
		
		self.submit = wx.Button( self, wx.ID_ANY, _(u"Submit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.submit, 1, wx.ALL, 20 )
		
		self.check = wx.Button( self, wx.ID_ANY, _(u"Validate"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.check, 1, wx.ALL, 20 )
		
		self.delete = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.delete, 1, wx.ALL, 20 )
		
		self.sid = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 0,0 ), wx.TE_READONLY )
		self.sid.SetMaxLength( 0 ) 
		bSizer9.Add( self.sid, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( bSizer9, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer7 )
		self.Layout()
		bSizer7.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.cost.Bind( wx.EVT_CHAR, self.on_Code )
		self.backtest.Bind( wx.EVT_BUTTON, self.onBackTest )
		self.submit.Bind( wx.EVT_BUTTON, self.onSubmit )
		self.check.Bind( wx.EVT_BUTTON, self.onValidate )
		self.delete.Bind( wx.EVT_BUTTON, self.onDelete )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_Code( self, event ):
		event.Skip()
	
	def onBackTest( self, event ):
		event.Skip()
	
	def onSubmit( self, event ):
		event.Skip()
	
	def onValidate( self, event ):
		event.Skip()
	
	def onDelete( self, event ):
		event.Skip()
	

