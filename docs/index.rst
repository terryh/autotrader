.. autotrader documentation master file, created by
   sphinx-quickstart on Sat Feb 23 22:06:30 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

======================================
Autotrader 說明文件
======================================

內容
=====


開始畫面
---------
    
    .. image:: _static/main.png
        :class: intro

    主要畫面，分為四的區塊，左上，目前有設定的交易市場，左下，目前設定的交易商品，
    右上，系統訊息，右下，交易策略設定。

新建市場
------------
    .. image:: _static/market.png
        :class: intro
    
    建立交易市場，名稱，代碼，交易市場的時區，第1盤，第2盤，交易開始時間，及結束時間，例如像是
    像是台灣的期貨市場，只要設定第1 盤即可，開始 08:45，結束 13:45 即可，直接點擊兩下，就可以
    進行修改。
    

新建商品
------------
    
    .. image:: _static/commodity.png
        :class: intro

    新增交易商品，商品名稱，代碼，選擇市場，設定每點價值，報價源資料，目前只支援 DDE，即時寫入報價檔
    的資料夾，最好是設定在 ramdisk 上面。

    .. image:: _static/dde.png
        :class: intro

    DDE 報價源設定，可以設定商品的 DDE 資訊，若是不清楚，可以拖曳報價資訊到到 Excel 表格下取得，
    請記得，在系統執行前，先開啟報價源的系統程式，台灣目前我是用康和的系統

    時間，最新交易的時間，價格，最新價格，總量，累計總成交量，及設要定產生時間類型歷史資料

新建策略
------------

    .. image:: _static/strategy.png
        :class: intro

    新增交易策略，選擇您編寫好的交易策略檔，純 Python 的檔案，您可以用您喜歡的編輯器，直接編輯，
    選擇交易商品的代碼，及使用的時間周期，設定策略使用的最大 K bar 資料比數

策略執行
---------
    
    .. image:: _static/chart.png
        :class: intro

    交易實際執行的畫面，trader.exe 及每一個程式都是各自獨立，autotrader 只是程序控制的介面

策略撰寫
---------

    策略的檔案是用 Python 的程式語法，並沒有內建的編輯器，您可以自己用喜歡的編輯器，編寫交易策略
    您可以參可坊間 Python 的書籍，或是線上的教學瞭解 Python 的語，基本上蠻類似英文，不同的程式
    區間需要用縮排區隔，這一點，可能先需習慣

    基礎的程式開頭::

        # 常數宣告
        PARAS={
        "ran":32,
        }
        # 變數宣告
        VARS = {
        "longentry":99999,
        "shortentry":0,
        "longex":0,
        "shortex":99999,
        "count":0,    
        }

    交易程式保留字

    BUY('Name',  price)        買入

    SELL('Name', price)        賣出

    EXITLONG('Name', price)    多單平倉

    EXITSHORT('Name', price)   空單平倉

    MARKETPOSITION 目前倉位

    ENTRYPRICE  最新的進場價格
    
    DATETIME   交易的時間陣列，DATETIME[-1] 是最新的 K bar 時間

    OPEN        K bar 的 Open 陣列，OPEN[-1] 是最新的 K bar open 價格

    HIGH        K bar 的 High 陣列，HIGH[-1] 是最新的 K bar high 價格

    LOW         K bar 的 Low 陣列，LOW[-1] 是最新的 K bar low 價格

    CLOSE       K bar 的 Close 陣列，CLOSE[-1] 是最新的 K bar close 價格

    VOLUME      K bar 的 Volume 陣列，VOLUME[-1] 是最新的 K bar 成交量


    完整程式範例，以 Open arange breakput 的當沖程式策略做範例，例如以每天
    開盤價格為基準，向上30 點做多，向下30點做空，多空點，也是停損點，一天只
    做一趟，收盤前，平倉
        
    程式如下::
    
        #!/usr/bin/env python
        # -*- coding: utf-8 -*-
        
        PARAS={
        "ran":30,
        }

        VARS = {
        "longentry":99999,
        "shortentry":0,
        "longex":0,
        "shortex":99999,
        "count":0,    
        }

        if DT[-1].date() != DT[-2].date():
            # 今日第1個 K bar，設定多單，及空單價位
            longentry = OPEN[-1]+ran
            shortentry = OPEN[-1]-ran

        if MARKETPOSITION == 0 and count == 0 and HIGH[-1] >= longentry:
            # 沒有倉位，目前高價，大於等於 longentry 多單進場點
            BUY("BUY",longentry) 

        if MARKETPOSITION == 0 and count == 0 and LOW[-1] <= shortentry:
            # 沒有倉位，目前低價，小於等於 shortentry 空單進場點
            SELL("SELL",shortentry) 


        if MARKETPOSITION > 0 and longex == 0:
            # 多單在手，longex為 0， 設定停損點
            longex = shortentry

        if MARKETPOSITION < 0 and shortex == 99999:
            # 空單在手，shortex為 99999， 設定停損點
            shortex = longentry

        if DT[-1].time() >= datetime.time(13,30,0) and MARKETPOSITION != 0:
            # 時間到了13:30 這一個 K bar ，手上有倉位，多單平倉，空單平倉
            EXITLONG("GYXL",C[-1])
            EXITSHORT("GYXS",C[-1])

        # 您可以直接在程式裡讀寫策略結果輸出檔，一樣，建議輸出到ramdisk
        # fp = open("R:\mytfx.txt","w")
        # fp.write("%s, %s" % (DATETIME[-1].strftime('%Y-%m-%d, %H:%M:%S'), MARKETPOSITION)


程式及資料夾介紹
----------------

    autotrader.exe 主要的執行程式名稱，基本介面，設定各種交易所需的條件，及主要的其他子程式的管理介面。

    DDE.exe 基本 windows 歷史悠久的報價服務，目前台灣落後的程式交易環境，幾乎所有的看盤報價程式都有提供，
    非常方便簡單的報價源，目前報價介面的設計，沒有支援 ticket 的方式，採用的總量的計算。

        基本上，都會由主程式控制，您也可以完全自己執行

        使用: windows DDE client 端，查尋 DDE 報價資訊

        程式執行可以下的參數

        -h, --hellp     顯示說明
        
        -i INTERVAL, --interval INTERVAL 設定查詢 DDE 報價休息中斷時間，預設是 0.3 秒
        
        -com COMMODITY, --commodity COMMODITY 指定所對應的商品代碼

        -c CONFIG, --config CONFIG 商品設定檔的路徑
    
    quoteworker.exe 獨立程序，合併報價源資料後，產生新的K線資料，作為程式策略交易的報價資訊

        程式執行可以下的參數
        
        -h, --hellp     顯示說明

        -i INTERVAL, --interval INTERVAL 設定查詢報價源報，休息中斷時間，預設是 0.3 秒

        -c CINI, --cini CINI 商品設定檔的路徑
        
        -m MINI, --mini MINI 交易市場的設定檔路徑
        
        -com COMMODITY, --commodity COMMODITY 指定所對應的商品代碼

    trader.exe 交易策略執行的程序
        
        程式執行可以下的參數

        -h, --hellp     顯示說明

        -f FILE, --file FILE 策略檔

        -q QUOTE, --quote QUOTE 最新報價的文字檔

        -his HISTORY, --history HISTORY 歷史報價文字檔

        -s START, --start START 回測開始日期

        -e END, --end END 回測結束日期

        -b BACKBARS, --backbars BACKBARS 策略執行，所需要的最少 K bar 數量

        -pv POV, --pov POV 每點數值，對應的價值 point of v alaue

        -tx TAX, --tax TAX 所需稅金

        -i INTERVAL, --interval INTERVAL 設定每次執行策略休息中斷時間，預設是 0.3 秒

        -g, --gui 開啟 GUI 模式，顯示報價資料

    taifex.exe 簡易整和台灣期貨交易歷史資料工具，下載的歷史資資料來自 http://taifex.com.tw/ ，目前有提供
    最近30 日的交易資料，可共下載，此程序，可以合併生成 1, 3, 5, 15, 30 分鐘線，方便策略交易。

    代碼

    TX  台指期
    MTX 小台指
    TE  電子期
    TF  金融期

        程式執行可以下的參數

        -h, --hellp     顯示說明

        -s START, --start START 開始下載資料的日期，格式 YYYYMMDD，

        -ym YM, --ym YM 目標合約的年月，格式 YYYYMM

        -d, --download 指定只由期交所下載資料

        -a, --auto 自動模式，收集最近 5 天的報價資料，自動猜最適合合約的月份

        -code CODE, --code CODE 申明只要整理某商品代碼的歷史資料

        -dir DIR, --dir DIR 將處理完的歷史資料複製到這一個資料夾




.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

