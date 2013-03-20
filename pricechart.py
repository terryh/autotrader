# -*- coding: utf-8 -*-
"""
Drawing realtime plot for trading
"""

# Major library imports
import time
import os
import sys
import wx
import random

#from numpy import arange, vstack
import numpy as np

# locale
#basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
#localedir = os.path.join(basepath, "locale")
#langid = wx.LANGUAGE_DEFAULT
#domain = "messages"
#mylocale = wx.Locale(langid)
#mylocale.AddCatalogLookupPathPrefix(localedir)
#mylocale.AddCatalog(domain)
#_ = wx.GetTranslation
import gettext
_ = gettext.gettext

# Enthought library imports
from enable.api import Window, BaseTool
from enable.component_editor import ComponentEditor
from traitsui.api import Item, View, Group, HGroup, VGroup, Handler
from traits.api import HasTraits, Instance, Int, Float, Str, Any
from enable.example_support import DemoFrame, demo_main

from traits.has_traits import on_trait_change
from pyface.timer.api import Timer

# Chaco imports
from chaco.api import (ArrayPlotData,
                       ArrayDataSource,
                       HPlotContainer,
                       VPlotContainer,
                       OverlayPlotContainer,
                       Plot,
                       PlotAxis,
                       BarPlot,
                       FilledLinePlot,
                       DataRange1D,
                       LinearMapper,
                       create_line_plot,
                       add_default_axes,
                       add_default_grids
                       )

from chaco.tools.api import PanTool, ZoomTool, LineInspector, BroadcasterTool
from chaco.data_range_2d import DataRange2D

################################################################################
## Attributes to use for the plot view.
size = (900, 600)
title = "Candlestick plot"
bg_color = "lightgray"
color_green = (139 / 255.0, 186 / 255.0, 71 / 255.0, 1)
color_red = (255 / 255.0, 33 / 255.0, 33 / 255.0, 1)
################################################################################


class XYTool(BaseTool):
    """
    CustomTool to return [X,Y] axis data
    """

    callback = Any()

    def normal_mouse_move(self, event):
        #print dir(event)
        if self.callback is not None:
            #print "Screen: ", event.x, event.y
            data = self.component.map_data((event.x, event.y))
            return self.callback(self, data)
        return []


class AnimationHandler(Handler):
    def init(self, info):
        super(AnimationHandler, self).init(info)
        #info.object.timer = Timer(10, info.object.on_timer)
        info.object.timer = Timer(300, info.object.on_timer)

    def closed(self, info, is_ok):
        super(AnimationHandler, self).closed(info, is_ok)
        info.object.timer.Stop()


class Trait(HasTraits):
    """
    Main Drawing view for plot
    """
    container = VPlotContainer(padding=0, fill_padding=True,
                               bgcolor="lightgray", use_backbuffer=True)

    #container2 = OverlayPlotContainer(padding = 5, fill_padding = True,
    #                    bgcolor = "lightgray", use_backbuffer=True)
    str_time = Str
    float_open = Float
    float_high = Float
    float_low = Float
    float_close = Float
    float_volumn = Float

    plot = Instance(Plot)
    # TraitsUI view
    traits_view = View(Group(
        VGroup(
            #HGroup(Item("str_time", label="時間"), show_border = True, label = u"詳細資料"),
            HGroup(Item("str_time", label=_("time")),
                   Item("float_open", label=_("open")),
                   Item("float_high", label=_("high")),
                   Item("float_low", label=_("low")),
                   Item("float_close", label=_("close")),
                   Item("float_volumn", label=_("volumn")),
                   show_border=True, label=u"詳細資料"),
            VGroup(Item(
                "container", editor=ComponentEditor(), show_label=False))
        )),
        resizable=True,
        width=size[0],
        height=size[1],
        handler=AnimationHandler(),
        title=u"Autotrader")
            #title=u"Plot 中文")

    # Constructor
    def __init__(self, dataframe=None):
        super(Trait, self).__init__()
        # main data frame for whole plot
        self.df = dataframe
        self.plot = self._create_plot()

    ############################################################################
    ###  adjust boundary
    def _compute_range2d(self):
        #if len(self.df)> 100:
        lowy = min(self.df.low[-100:])
        lowy = lowy * 0.998
        lowx = len(self.df) - 100

        highy = max(self.df.high[-300:])
        highy = highy * 1.002

        highx = len(self.df)
        range2d = DataRange2D(low=(lowx, lowy),
                              high=(highx, highy))
        return range2d

    @on_trait_change('redraw', post_init=True)
    def _update_range2d(self):
        self.plot.range2d = self._compute_range2d()

    def _create_plot(self):

        # count data
        if len(self.df) > 0:
            self.indexes = np.arange(len(self.df.date_time))
            time_ds = ArrayDataSource(self.indexes)
            vol_ds = ArrayDataSource(self.df.volumn.values, sort_order="none")
            xmapper = LinearMapper(range=DataRange1D(time_ds))
            vol_mapper = LinearMapper(range=DataRange1D(vol_ds))

            ####################################################################
            # create volumn plot
            vol_plot = BarPlot(index=time_ds, value=vol_ds,
                               index_mapper=xmapper,
                               value_mapper=vol_mapper,
                               line_color="transparent",
                               fill_color="blue",
                               bar_width=0.6,
                               antialias=False,
                               height=100,
                               resizable="h",
                               origin="bottom left",
                               bgcolor="white",
                               border_visible=True
                               )

            vol_plot.padding = 30
            vol_plot.padding_left = 40
            vol_plot.tools.append(
                PanTool(vol_plot, constrain=True, constrain_direction="x"))
            add_default_grids(vol_plot)
            add_default_axes(vol_plot)

            #print vol_plot.index_mapper.range.high
            #print vol_plot.value_mapper.range.low, vol_plot.value_mapper.range.high
            self.vol_plot = vol_plot
            self.container.add(vol_plot)

            ####################################################################
            ## Create price plot

            sorted_vals = np.vstack(
                (self.df.open, self.df.high, self.df.low, self.df.close))
            sorted_vals.sort(0)
            __bool = self.df.close.values - self.df.open.values
            self.up_boolean = __bool >= 0
            self.down_boolean = np.invert(self.up_boolean)

            pd = ArrayPlotData(
                up_index=self.indexes[self.up_boolean],
                up_min=sorted_vals[0][self.up_boolean],
                up_bar_min=sorted_vals[1][self.up_boolean],
                up_bar_max=sorted_vals[2][self.up_boolean],
                up_max=sorted_vals[3][self.up_boolean],
                down_index=self.indexes[self.down_boolean],
                down_min=sorted_vals[0][self.down_boolean],
                down_bar_min=sorted_vals[1][self.down_boolean],
                down_bar_max=sorted_vals[2][self.down_boolean],
                down_max=sorted_vals[3][self.down_boolean],
                volumn=self.df.volumn.values,
                index=self.indexes
            )

            price_plot = Plot(pd)

            up_plot = price_plot.candle_plot(
                ("up_index", "up_min", "up_bar_min", "up_bar_max", "up_max"),
                color=color_red,
                bgcolor="azure",
                bar_line_color="black",
                stem_color="black",
                end_cap=False)[0]

            down_plot = price_plot.candle_plot(
                ("down_index", "down_min", "down_bar_min",
                 "down_bar_max", "down_max"),
                color=color_green,
                bar_line_color="black",
                stem_color="black",
                end_cap=False)[0]

            price_plot.fill_padding = True
            price_plot.padding = 30
            price_plot.padding_left = 40

            price_plot.tools.append(ZoomTool(component=price_plot, tool_mode="box", zoom_factor=1.2, always_on=False))
            price_plot.tools.append(PanTool(price_plot, drag_button="left"))
            price_plot.tools.append(
                XYTool(price_plot, callback=self._update_ohlc))  # get data
            self._add_line_tool(up_plot)
            self._add_line_tool(down_plot)
            price_plot.range2d = self._compute_range2d()

            price_plot.index_mapper = vol_plot.index_mapper  # maper vol_plot and price_plot
            self.price_plot = price_plot

            self.container.add(price_plot)

    def _update_ohlc(self, tool, xyarray):
        """Update Open, High, Low, Close, DateTime, items"""
        if xyarray.size == 2:
            # [x,y] ndarray
            xindex = int(round(xyarray[0]))
            if xindex >= 0 and xindex <= self.df.last_valid_index():
                self.str_time = self.df.date_time[xindex].strftime("%H:%M")
                self.float_open = self.df.open[xindex]
                self.float_high = self.df.high[xindex]
                self.float_low = self.df.low[xindex]
                self.float_close = self.df.close[xindex]
                self.float_volumn = self.df.volumn[xindex]
            #print self.df.open[xindex]

    def _add_line_tool(self, input_plot):
            input_plot.overlays.append(LineInspector(input_plot, axis='index',
                                                     #inspect_mode="indexed", # will show two line
                                                     color="gray",
                                                     write_metadata=True,
                                                     is_listener=True))

    ############################################################################
    ###  check plot data
    def update_plot_data(self):
        """Update drawing"""
        #t1 = time.time()
        # vol_plot value update
        self.vol_plot.value.set_data(self.df.volumn.values)
        # price_plot value update
        sorted_vals = np.vstack(
            (self.df.open, self.df.high, self.df.low, self.df.close))
        sorted_vals.sort(0)
        __bool = self.df.close.values - self.df.open.values
        self.up_boolean = __bool >= 0
        self.down_boolean = np.invert(self.up_boolean)

        self.price_plot.data.set_data(
            'up_index', self.indexes[self.up_boolean])
        self.price_plot.data.set_data(
            'up_min', sorted_vals[0][self.up_boolean])
        self.price_plot.data.set_data(
            'up_bar_min', sorted_vals[1][self.up_boolean])
        self.price_plot.data.set_data(
            'up_bar_max', sorted_vals[2][self.up_boolean])
        self.price_plot.data.set_data(
            'up_max', sorted_vals[3][self.up_boolean])
        self.price_plot.data.set_data(
            'down_index', self.indexes[self.down_boolean])
        self.price_plot.data.set_data(
            'down_min', sorted_vals[0][self.down_boolean])
        self.price_plot.data.set_data(
            'down_bar_min', sorted_vals[1][self.down_boolean])
        self.price_plot.data.set_data(
            'down_bar_max', sorted_vals[2][self.down_boolean])
        self.price_plot.data.set_data(
            'down_max', sorted_vals[3][self.down_boolean])
        #print "T1", time.time() - t1

    def on_timer(self):
        # debug
        #self.df.volumn[self.df.last_valid_index()] = random.randrange(300,3000)
        #self.vol_plot.value.set_data(self.df.volumn.values)

        self.update_plot_data()
        self.container.request_redraw()
        return

if __name__ == "__main__":
    # TODO test
    import pandas

    res = pandas.read_csv('T.CSV', names=['date', 'time', 'open', 'high', 'low', 'close', 'volumn', 'nan'], parse_dates=[[0, 1]])

    gui = Trait(res)
    gui.configure_traits()

    #app = wx.GetApp()
    #if app is None:
        #app = wx.PySimpleApp()
        ##frame = PlotFrame(t.dataframe, size=(600,500), title='Plot')
    #frame = PlotFrame(res, None, size=(700,400), title='Plot')
    #app.SetTopWindow(frame)
    #app.MainLoop()
    #demo_main(PlotFrame, size=(600,500), title="plot")
