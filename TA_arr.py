# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')



import basefunc
from basefunc import daytostrFunc, inttodayFunc, istradeTime, tdxclient, numtoday, bigMemory, sm
from webData.cninfo import getStockList_cninfo
import os
import math
from collections import OrderedDict
import numpy as np
from tools.pandas_util import pd
from basedata.zdbl import zdbl
from kdata import kdata
from modules import globals as Globals
from SystemDir import *
from TAFunc import *
from PyQt5.QtWidgets import QApplication
#from Jrj.quotes_jrj import quotes_jrj
from realtimeCac.ema import *
from realtimeCac.dmi import dmi
from SystemDir import datadir
from tdx.settings import *
from dbConstant import *
from tools.Mongodb import db_drop_duplicates
from webData.cninfo import tradeCelender
from tools.Mongodb import df2dict
from tools.Mongodb import Mongodb
from PyQt5.QtCore import QObject, pyqtSignal
from realtimeCac.tsi import tsi, TSI
from realtimeCac.ma import MA, ma
from dbConstant import dayDB, jrjDayDB, dateDB
from dbList import dfcfDayDataDB,fqIndexdb

TDX = tdxclient(multithread=True)
TDX.connect(defaltIP['ip'], defaltIP['port'])
# _zdbl = zdbl().cal().reset_index()  # 涨跌比率
# _zdbl = _zdbl[_zdbl.date > 11]
# zdblDict = dict(zip(_zdbl.date, _zdbl['涨跌比率']))
cols = ['code', 'yc', 'o', 'h', 'l', 'c', 'vol',
        'volp', 'ltgb', 'tmc', 'mc', 'chg', 'hsl', 'date']
# from utils.histDate import histDate
histData_columns = ['c', 'chg', 'code', 'date', 'h', 'hsl', 'l', 'ltgb', 'mc', 'o', 'tmc',
                    'vol', 'volp', 'yc', 'zde', '成交笔数']
_temp = pd.DataFrame(dateDB.collection.find(
    {}, {'_id': 0, 'intdate': 1, 'week': 1}))
weekDict = dict(zip(_temp['intdate'], _temp['week']))


def dataAnalysis(ret):
    ret.replace('None', np.nan, inplace=True)
    convert_columns(ret)
    del ret['name']
    ret['code'] = int(ret.loc[0, 'code'][1:])
    ret['date'] = date_normalize(ret['date'])
    for col in ret.columns:
        if ret[col].dtypes == 'O':
            try:
                ret[col] = ret[col].astype(np.float)
            except Exception as e:
                print(f"error:{e}")
    ret['ltgb'] = ret['vol']/ret['hsl']
    ret = ret[ret.c > 0].copy()
    ret['avgp'] = ret.volp/ret.vol
    ret['drdk'] = 100*ret.c/ret.avgp-100
    return ret


def formatTodot2(data):
    return 1e4*data//1e2/100


def ffq_df(df, **kwargs):
    chg_adj = .01
    arr = np.array(df.chg)
    arrc = np.array(df.c)
    if kwargs.get('ascending'):
        arr = arr[::-1]
        last_c = arrc[-1]
        arrc = arrc[::-1]
    else:
        last_c = arrc[0]
    arr[1:] = 1-chg_adj*arr[:-1]
    arr[0] = 1

    adj_c = last_c*np.multiply.accumulate(arr)
    factor = np.true_divide(adj_c,arrc)
    if kwargs.get('ascending'):
        factor = factor[::-1]
    return factor



# db_drop_duplicates(fqIndexdb,['SECCODE','F003D'])
fqIndex = pd.DataFrame(fqIndexdb.collection.find({}, {'_id': 0}))
# fqIndex.drop_duplicates(inplace=True)
fqIndex.index = fqIndex['F003D'].apply(lambda x: int(x.replace('-', '')))
fqIndex.index.name = 'date'
fqIndex['date'] = fqIndex.index
# _tmp = pd.DataFrame(tradeCelender().db.collection.find({},{'_id':0}))
# fqIndex['F003D'] = fqIndex['F003D'].map(dict(zip(_tmp['F001D'],_tmp['F011D'])))


def hlfd_db(db):
    """
    回落幅度
    """
    for i in db.collection.find({'vol': None}, {}):
        db.collection.find_one_and_delete({'_id': i['_id']})
    for i in cninfodaydb.collection.find({'hlfd': {'$exists': False}}, {'c', 'h'}):
        db.collection.find_one_and_update(
            {'_id': i['_id']}, {'$set': {'hlfd': 100*i['h']/i['c']-100}})
# hlfd_db(cninfodaydb)


def loadData(code='000001', usedfcf=True,db=dfcfDayDataDB,if_cninfo=False):
    ret = []
    # data = dayDB.loadDf({'code':code})
    # data = pd.DataFrame(dfcfHQDB.collection.find({'code':'000001'},{'_id':0}))
    if if_cninfo:
        db = cninfodaydb
    if usedfcf:
        data = pd.DataFrame(db.collection.find({'code': code, }, {'date', 'c', 'chg', 'code',
                                                                           'h', 'hsl', 'l', 'ltgb', 'o', 'pe', 'vol', 'volp', 'yc', 'zde', 'zf',
                                                                           'zgb', '成交笔数', 'hlfd', 'avgp', 'drdk', 'ffq', 'week', 'lost'}))
        if len(data):
            data.pop('_id')
            # data = pd.DataFrame(cninfodaydb.collection.find({'code':code},{'_id':0}))
            data = data.sort_values('date', ascending=True)
            for i in set(data.columns)-set(['code', 'date']):
                try:
                    data[i] = data[i].apply(
                        lambda x: x.replace(',', '')).astype(float)
                except:
                    pass
            data.index = data['date']
            tmp = np.zeros(len(data))*np.nan
            tmp[1:] = np.array(data['c'])[:-1]
            data['yc'] = tmp
            # data['chg'] = 100*data['c']/data['yc']-100
            data['volp']=data['volp'].astype(str).apply(lambda x:float(x.replace(',','')))
            data['vol']=data['vol'].astype(str).apply(lambda x:float(x.replace(',','')))
            data['avgp'] = data['volp']/data['vol']
            data['drdk'] = 100*data['c']/data['avgp']-100
            qfq = fqIndex[fqIndex['SECCODE'] == code][[
                'F003D', 'F010N', 'F011N', 'date']]
            qfq['ffq'] = np.multiply.accumulate(qfq['F010N'][::-1])[::-1]
            # data['ffq'] = data['date'].map(dict(zip(qfq['F003D'],qfq['ffq'])))
            # data = pd.concat([data, qfq[['ffq', 'date']]], axis=1)
            # data.index.name = 'D'
            # data.sort_values(['date', 'c'], inplace=True, ascending=True)
            # if list(data.date[-1:]) > list(qfq['ffq'].index[-1:]):
            #     data.loc[data.index[-1], 'ffq'] = 1
            # data.ffq.fillna(method='bfill', inplace=True)
            # data = data[data.c > 0]
            # # if math.isnan(data.loc[data.index[-1],'ffq']):
            # #     data.loc[data.index[-1],'ffq'] = 1
            # data.ffq.fillna(method='bfill', inplace=True)
            # tmp = np.array(data['ffq'])
            # tmp[:-1] = tmp[1:]
            # # tmp[-1] = 1
            # data['ffq'] = tmp
            # data = data[data.c > 0]
            """
            # data.sort_values('date',inplace=True,ascending=False)
            # data['ffq'] = ffq_df(data)
            # data.sort_values('date',inplace=True,ascending=True)
            # data['date'] = data['date'].apply(lambda x:int(x.replace('-','')))
            """
            data['ffq'] = data['date'].map(
                dict(zip(qfq['date'], qfq['F010N'])))
            data['ffq'] = data.ffq.fillna(1)
            data['ffq'] = np.multiply.accumulate(
                np.array(data.ffq)[::-1])[::-1]
            data['ffq'] = data.ffq.shift(-1)
            if hasattr(data, 'lost'):
                data = data[data['lost'] != 1]
            ret = data
    else:
        data = dayDB.loadDf({'code': code})
        data = data[data.c > 0]
        data['avgp'] = 1e2*data['volp']/data['vol']
        if len(data):
            temp = jrjDayDB.load(
                {'$and': [{'date': {'$gt': np.unique(data.date)[-1]}}, {'code': code}]})
            if temp:
                if isinstance(temp, dict):
                    temp = [temp]
                temp = pd.DataFrame(temp)
                temp['drdk'] = 100*temp.c/temp.avgp-100
                temp['ffq'] = data.iloc[0]['ffq']
                temp['成交笔数'] = data.iloc[0]['成交笔数'] * \
                    temp['vol']/data.iloc[0]['vol']
                temp['code'] = int(code)
                ret = pd.concat([temp[data.columns], data])
            else:
                ret = data
            ret = ret[ret['c'] > 0]
            ret.sort_values('date', inplace=True, ascending=True)
        else:
            ret = pd.DataFrame()
    if len(ret):
        if hasattr(ret, 'date'):
            ret['week'] = ret['date'].map(weekDict)
            ret['month'] = ret['date'].map(monthDict)
    return ret


dayDfColumns = dayDB.col
reset_dataFunc = {'m': toMonth, 'w': toWeek}


class TA_data(QObject):
    datafinished = pyqtSignal()
    periodchanged = pyqtSignal(str)

    def __init__(self, histData=pd.DataFrame()):
        super(TA_data, self).__init__()
#        dayDB = Mongodb('stock_day', 'ntes')
        self.ascending = False
        self.colDict = {}
        self.col = dayDfColumns
        self.period = 'd'
        # [self.colDict.update({col:idx}) for idx,col in enumerate(cols)]
        self.DataDict = {}
        self.periodchanged.connect(self.reset_data)

    def set_data(self, code):
        if isinstance(code, np.ndarray):
            self.dayArr = code
            for col in self.dayArr.dtype.names:
                if col in ['c', 'h', 'o', 'l', 'hsl', 'yc', 'zde']:
                    self.dayArr[col] = 1e4*self.dayArr[col]//1e2/100
            self.data = ffq_np(self.dayArr)
            for col in self.data.dtype.names:
                if col in ['c', 'h', 'o', 'l', 'hsl', 'yc', 'zde']:
                    self.data[col] = 1e4*self.data[col]//1e2/100
        elif isinstance(code, pd.core.frame.DataFrame):
            self.data = code
            self.code = str(int(self.data['code'].iloc[0]))
        else:
            self.code = code
            self.data = loadData(code)
        self.initData()

    def set_period(self, period):
        self.period = period
        self.periodchanged.emit(self.period)

    def reset_data(self):
        self.data = reset_dataFunc.get(self.period)(self.DataDict.get('d'))
        # self.initData()

    def initData(self):
        #data = self.data
        if isinstance(self.data, pd.DataFrame):
            # data[['c', 'h', 'o', 'l', 'avgp']] = 1e4 * \
            #     self.data[['c', 'h', 'o', 'l', 'avgp']]
            # for col in ['c', 'h', 'o', 'l', 'avgp']:
            #     data[col] = data[col]*data['ffq']//1e2/100
            tmp = np.array(self.data[['c', 'h', 'o', 'l', 'avgp']]
                           ).T*np.array(self.data['ffq'])*1e4//1e2/100
            self.data[['c', 'h', 'o', 'l', 'avgp']] = tmp.T
            self.data = self.data[self.data.c > 0]
            self.data['vol'] = 1e4*self.data['vol']/self.data['ffq']//1e2/100
            self.data['yc'] = self.data['c'].shift(1)
            if self.data['date'].iloc[0] > self.data['date'].iloc[-1]:
                holdday = Cac_holdday_arr(np.array(self.data.hsl))
                self.data['holdday'] = holdday
                # updateColDict('holdday')
                ascending = True
                self.data.sort_values('date', inplace=True)
            #self.data = data
            self.Data = self.data.copy()
            self.DataDict.update({self.period: self.Data})
            self.dayArr = np.array(self.Data)
            #self.dateArr = self.dayArr[:, 0].astype(int).astype(str)
            self.dateArr = np.array(self.data.date.astype(int).astype(str))
            self.colDict = dict(
                zip(self.data.columns, range(self.dayArr.shape[1])))
            return self.data

    def updateData(self):
        market = 0
        if self.code[0] in ['6']:
            market = 1
        temp = None
        temp = TDX.get_security_bars(9, market, self.code, 0, 1, Gui=True)
        if temp != None:
            self.Data[-1:][['o', 'c', 'h', 'l',
                            'vol', 'volp', 'avgp', 'drdk']] = temp
        self.dayArr = np.array(self.Data)

    def Cac_holdday_arr(self, hsl, hsnums=1):
        less100 = np.add.accumulate(hsl[-200:][::-1])
        mx = 100*hsnums
        startidx = np.argmin(less100 < mx)
        ret = np.zeros(len(hsl), dtype=np.int)
        for arridx in range(0, len(hsl)-startidx):
            temp = np.add.accumulate(hsl[arridx:])
            ret[arridx] = np.argmax(temp > mx)
        ret[:len(hsl)-startidx] += 1
        return ret

    def updateColDict(self, item=''):
        if item != '':
            self.colDict.update({item: self.data.shape[1]-1})
        else:
            [self.colDict.update({col: idx})
             for idx, col in enumerate(self.data.columns)]
        self.dayArr = np.array(self.data)
        self.Data = self.data.copy()


class TA_arr(TA_data):
    datafinished = pyqtSignal()

    def __init__(self, histData=pd.DataFrame()):
        super(TA_arr, self).__init__()
        self.code_columns = 'code'
        self.dataChanged = False
        self.daydata = pd.DataFrame()
        self.kdata = []
        self.histData = histData
        self.data = pd.DataFrame()
        self.grouped = False
        self.groupcol = ''
        self.mulitcode = False
        self.realtime = True
        # self.period = 'D'
        self.isfq = True
        self.multicode = False
        # defined for MA
        self.maArr = np.array([])
        self.prePriodSum = 0
        self.indicator = {}
        self.funcDict = {'avolma': self.AVOLMA}
#    def reset_data(self):
#        if hasattr(self,'tsiArr'):
#            self.tsiArr=self.fastarr=self.fastarrabs = []
#            self.dmiArr = []
#        # self.load_indexData()

    def _init_code_columns(self, code_columns='code'):
        if 'code' not in self.data.columns:
            temp = [i for i in self.data.columns if (
                ('bk_' in i) | ('block_' in i))]
            if len(temp) > 0:
                self.code_columns = temp[0]
            else:
                self.code_columns = code_columns

    def setDataFrameByCode(self, stockcode=[], code_columns='code', fq=1):
        self.reset_data()
        if fq == 1:
            self.isfq = True
        else:
            self.isfq = False
        if True:
            if isinstance(stockcode, (str, np.int, np.float)):
                self.old_data = self.histData[self.histData.code == int(
                    stockcode)]
                stockcode = [stockcode]
                self.multicode = False
#            elif isinstance(stockcode,pd.DataFrame):
#                self.old_data = stockcode
#                self.multicode = False
            elif hasattr(stockcode, '__iter__'):
                if not isinstance(stockcode, list):
                    stockcode = list(stockcode)
                    if len(stockcode) == 1:
                        self.multicode = False
                    else:
                        self.mulitcode = True
                if len(stockcode) == 0:
                    self.mulitcode = True
                    stockcode = all_stocklist
                    self.old_data = self.histData
                elif len(stockcode) == 1:
                    self.old_data = self.histData[self.histData.code == int(
                        stockcode[0])]
                else:
                    self.old_data = self.histData.query(
                        "code in %s" % stockcode).copy()
            if istradeTime():
                existCode = self.old_data[self.old_data.date ==
                                          inttoday].code.tolist()
                download_stockcode = [
                    i for i in stockcode if int(i) not in existCode]
            else:
                download_stockcode = []
            if len(download_stockcode):
                tmp = quotes_jrj().parse(download_stockcode)[cols]
                tmp.index = tmp.date.values
                self.daydata = self.old_data.append(tmp)
            else:
                self.daydata = self.old_data.copy()
            self.initdata(fq=fq)
        else:
            if isinstance(stockcode, (str, np.int, np.float)):
                self.old_data = hist_data.select(
                    'ntes', where="code in %s" % [stockcode])
                stockcode = [stockcode]
                self.multicode = False
            elif hasattr(stockcode, '__iter__'):
                if not isinstance(stockcode, list):
                    stockcode = list(stockcode)
                    if len(stockcode) == 1:
                        self.multicode = False
                    else:
                        self.mulitcode = True
                if len(stockcode) == 0:
                    self.mulitcode = True
                    stockcode = all_stocklist
                    self.old_data = hist_data.select('ntes')
                else:
                    self.old_data = hist_data.select(
                        'ntes', where="code in %s" % stockcode)
            if istradeTime():
                existCode = self.old_data[self.old_data.date ==
                                          inttoday].code.tolist()
                download_stockcode = [
                    i for i in stockcode if int(i) not in existCode]
            else:
                download_stockcode = []
            if len(download_stockcode):
                tmp = quotes_jrj().parse(download_stockcode)[cols]
                tmp.index = tmp.date.values
                self.daydata = self.old_data.append(tmp)
            else:
                self.daydata = self.old_data
            self.initdata(fq=fq)
        if self.period in ['D', 'd']:
            self.initdata(fq=fq)
        self.dayArr = np.asarray(self.data)
        if hasattr(self, 'date'):
            try:
                self.data['date'] = self.date = self.date.astype(np.int)
                self.year = (self.date/1e4).astype(np.int)
                self.month = (self.date/1e2).astype(np.int)
            except:
                pass
        return self

    def query(self, item):
        if isinstance(item, (list, tuple)):
            columns = [colDict.get(i) for i in item]
        else:
            columns = self.colDict.get(item)
        if not (columns == None):
            return self.dayArr[:, columns]
        elif hasattr(self, item[:-3]):
            self.func[item[:-3]]()
            self.query(item)

    def getArr(self, item):
        ret = None
        if not (hasattr(self, item) or hasattr(self.data, item)):
            ret = self.funcDict.get(item)()
        elif hasattr(self.data, item):
            ret = self.query(item)
        return ret

    def get(self, item):
        return self.getArr(item)

    def ref(self, item, n):
        if not isinstance(item, (list, tuple)):
            return self.dayArr[-n-1, self.colDict[item]]
        else:
            return [self.ref(i, n) for i in item]

    def refs(self, item, n):
        if isinstance(item, (list, tuple)):
            columns = [self.colDict[i] for i in item]
        else:
            columns = self.colDict[item]
        return self.dayArr[-n:, columns]

    def TSI(self, fastperiod=25, lowperiod=13):
        if hasattr(self, 'tsiArr'):
            self.tsiArr[-1] = tsi(self.ref('c', 0), self.ref('c', 1), self.fastarr,
                                  self.fastarrabs, self.tsiArr, fastperiod, lowperiod)[-1]
        else:
            self.fastarr, self.fastarrabs, self.tsiArr = TSI(
                self.query('c'), fastperiod, lowperiod)
        self.indicator.update({'TSIArr': self.tsiArr})
        return self.tsiArr

    def MA(self, period, item='c'):
        if len(self.maArr):
            ma(self.maArr, self.ref(item, 0), self.prePriodSum, period)
        else:
            self.maArr, self.prePriodSum = MA(self.query(item), period)
        return self.maArr

    def initdata(self, fq=1):
        if 'volp' in self.daydata.columns:
            self.daydata['avgp'] = np.asarray(
                self.daydata.volp)/np.asarray(self.daydata.vol)
            self.daydata['drdk'] = 100*self.daydata.c/self.daydata.avgp-100
            self.daydata['ltgb'] = self.daydata.vol/self.daydata.hsl
        if Globals.excludenonetrading:
            try:
                self.daydata = self.daydata[self.daydata.trade]
            except:
                pass
        if Globals.excludewkb:
            try:
                self.daydata = self.daydata[self.daydata.kb]
            except:
                pass
        if 'ffq' in self.daydata.columns:
            self.daydata['avgp'] = self.daydata.ffq*self.daydata.avgp
        self.daydata.sort_values(['code', 'date'], inplace=True)
        self.daydata.index = range(len(self.daydata))
        self.data = self.daydata
        self._init_code_columns()
        try:
            self.precaculate()
        except:
            pass
        if (fq == 1) & (len(self.data) > 0):
            self.data = ffq(self.data, groupcol='code')
            self.data['avgp'] = self.data.ffq*self.data.avgp
        if 'code' in self.data.columns:
            if len(self.data.code.unique()) > 1:
                self.multicode = True
                self._groupAnalysis()
            else:
                self.multicode = False
        else:
            self.multicode = False
        if self.multicode:
            self.groupcol = self.code_columns
        else:
            self.groupcol = ''
        self._groupAnalysis()
        return self

    def setDataFrame(self, data=pd.DataFrame(), code_columns='code', fq=1, **kwargs):
        if data.empty:
            self.setDataFrameByCode(
                stockcode=[], code_columns='code', fq=1, **kwargs)
        else:
            stockcode = data.code[0]
            self.data = data.copy()
            self.old_data = self.data
            if inttoday not in self.old_data.date:
                tmp = quotes_jrj().parse(stockcode)[cols]
                tmp['date'] = tmp.date.map(dayDict)
                tmp.index = tmp.date.values
                self.daydata = self.old_data.append(tmp)
            else:
                self.daydata = self.old_data
            self.initdata(fq=fq)
        return self

    def _groupAnalysis(self):
        if 'code' in self.data.columns:
            self.groupbycode = self.data.groupby(
                'code', sort=False, as_index=False)
            self.grouped = True
        return self

    def toDisp(self, item=''):
        pass
        #self.data['date'] = self.data.date.map(daytostr).replace('-', '')

    def for_realtime(self, df):
        cols = [i for i in self.data.columns if i in df.columns]
        self.data = self.data.append(df[cols])
        self.data.sort_values('date', inplace=True)
        self.data.index = range(len(self.data))
        return self

    def precaculate(self):
        self.data = self.data.groupby('code').apply(determin_kb)
        self.data = self.data[self.data.kb]
        self.data = self.data[self.data.c > 0]
        datecols = [i for i in self.data.columns if i in [
            'date', 'datetime']]
        if self.multicode:
            self.groupbycode = self.data.groupby(self.code_columns)

    def Cal_avgp(self):
        if ('volp' in self.data.columns) & ('vol' in self.data.columns):
            self.data['avgp'] = np.asarray(
                self.data.ffq)*np.asarray(self.data.volp)/np.asarray(self.data.vol)
        if ('vol' in self.data.columns) & ('hls' in self.data.columns):
            self.data['ltgb'] = np.array(self.data.vol)/np.array(self.data.hsl)

    def Cal_avgvolp(self):
        if self.mulitcode:
            temp = self.data.groupby('date', as_index=False, sort=False)[
                ['volp', '成交笔数']].sum()
            self.data['avgvolp'] = temp.volp/temp['成交笔数']
        else:
            self.data['avgvolp'] = self.data.volp/self.data['成交笔数']

    def Cac_chg_from(self, date):
        datefilter = np.where(self.date >= histDate().intDate(date))
        data = self.c[datefilter]
        maxIdx = np.argmax(data)
        minData = np.nanmin(data[maxIdx:])
        ret = 100*minData/data[maxIdx]-100
        ret1 = 100*data[-1]/minData - 100
        return ret, ret1

    def AMA(self, n=10, item='c'):
        fsc = 2/3
        ssc = 2/31
        price = list(self.data[item])
        datalenth = len(price)
        if not hasattr(n, '__iter__'):
            n = [n]
        grouped = self.data.groupby('code')
        for i in n:
            var = np.abs(grouped.c.shift(0)-grouped.c.shift(1)
                         ).rolling(window=i, min_periods=0).sum()
            # x.shift(0)-x.shift(1))#.cshift(0)-self.data.groupby('code').c.shift(i)
            direction = grouped.c.apply(diff)
            ER = np.true_divide(np.abs(direction), var)  # 效率系数
            smooth = list((ER*(fsc-ssc)+ssc)**2)

            def func1(data):
                ret = list(self.data.ama[:i])
                for _i in range(i, datalenth):
                    ret.append(smooth[_i] * price[_i] +
                               (1 - smooth[_i]) * ret[-1])
                return ret
            self.data['ama'] = grouped[item].rolling(
                i, min_periods=0).mean().values
            self.data['ama_%s' % i] = np.concatenate(
                grouped[item].apply(func1))
        del self.data['ama']
        self.updateColDict()
        return self

    def SMA(self, n=8, m=1, item='c'):
        datalenth = len(self.data)
        price = list(self.data[item])
        if self.multicode:
            grouped = self.data.groupby(self.code_columns)
            if not hasattr(n, '__iter__'):
                n = [n]
            for i in n:
                histFactor = i-m

                def func1(dataList, n=i, m=m, item=item):
                    ret = list(dataList.sma)[:n]
                    for i in range(n, datalenth):
                        ret.append((m * price[i] + histFactor*ret[i-1])/n)
                    return ret
                self.data['sma'] = grouped[item].rolling(
                    i, min_periods=0).mean().values
                # self.data['sma'] = self.data.groupby(self.code_columns).sma.apply(lambda x:(x-x.shift(-i).replace(np.nan,0).shift(i).replace(np.nan,0))).values
                self.data['sma_%s' % i] = np.concatenate(
                    grouped[[item, 'sma']].apply(func1).values)
        else:
            grouped = self.data.groupby(self.code_columns)
            if not hasattr(n, '__iter__'):
                n = [n]
            for i in n:
                histFactor = i-m

                def func1(dataList, n=i, m=m, item=item):
                    ret = list(dataList.sma)[:n]
                    for i in range(n, datalenth):
                        ret.append((m * price[i] + histFactor*ret[i-1])/n)
                    return ret
                self.data['sma'] = grouped[item].rolling(
                    i, min_periods=0).mean().values
                # self.data['sma'] = self.data.groupby(self.code_columns).sma.apply(lambda x:(x-x.shift(-i).replace(np.nan,0).shift(i).replace(np.nan,0))).values
                self.data['sma_%s' % i] = np.concatenate(
                    grouped[[item, 'sma']].apply(func1).values)
        self.updateColDict()
        return self

    def EMA(self, n=7, item='c'):
        if self.multicode:
            grouped = self.data.groupby(self.code_columns)
            if hasattr(n, '__iter__'):
                for i in n:
                    self.data['ema_%s' % i] = grouped.apply(
                        lambda x: x[item].ewm(span=i, adjust=False).mean()).values[0]
            elif item in ['dif']:
                self.data['dea'] = grouped.apply(
                    lambda x: x[item].ewm(span=n, adjust=False).mean()).values[0]
            else:
                self.data['ema_%s' % n] = grouped.apply(
                    lambda x: x[item].ewm(span=n, adjust=False).mean()).values[0]
        else:
            if hasattr(n, '__iter__'):
                for i in n:
                    self.data['ema_%s' % i] = self.data[item].ewm(
                        span=i, adjust=False).mean()
            elif item in ['dif']:
                self.data['dea'] = self.data[item].ewm(
                    span=n, adjust=False).mean()
            else:
                self.data['ema_%s' % n] = self.data[item].ewm(
                    span=n, adjust=False).mean()
        self.updateColDict()
        return self

    def MACD(self, nslow=26, nfast=12, mid=9, item='c'):
        """
        whether multicode or not,the caculation is same
        """
        self.EMA(n=[nfast, nslow], item=item)
        self.data['dif'] = self.data['ema_' +
                                     str(nfast)]-self.data['ema_'+str(nslow)]
        self.EMA(n=mid, item='dif')
        self.data['macd'] = 2*(self.data.dif-self.data.dea)
        self.updateColDict()
        return self

    def HPTP(self, m=12, n=26, S=9, item='c'):
        if self.multicode:
            grouped = self.data.groupby(self.code_columns)
            zl = grouped.apply(lambda x: ((x[item].ewm(span=m, adjust=False).mean(
            ) - x[item].ewm(span=n, adjust=False).mean()).ewm(span=5, adjust=False)).mean()).values
            if hasattr(zl[0], '__iter__'):
                self.data['主力'] = zl[0]
            else:
                self.data['主力'] = zl

            def func(x): return x.ewm(span=S, adjust=False).mean()
            # 散户 = self.data.groupby('code').agg({'主力':func})
            self.data['散户'] = self.data.groupby('code').zl.apply(func)
        else:
            self.data['主力'] = ((self.data[item].ewm(span=m, adjust=False).mean(
            ) - self.data[item].ewm(span=n, adjust=False).mean()).ewm(span=5, adjust=False)).mean()
            self.data['散户'] = self.data['主力'].ewm(span=S, adjust=False).mean()
        self.updateColDict()
        return self

    def WMA(self, n=30, item='c'):
        if self.multicode:
            grouped = self.data.groupby(self.code_columns)
            if not hasattr(n, '__iter__'):
                n = [n]
            for i in n:
                weights = np.arange(i, 0, -1)  # 产生n到 1的序列
                weights = np.true_divide(weights, weights.sum())
                wma = grouped[item].apply(
                    lambda x: np.convolve(x, weights, mode='full')[:-i+1])
                self.data['wma_%s' % i] = np.concatenate(wma.values)
        else:
            if not hasattr(n, '__iter__'):
                n = [n]
            for i in n:
                weights = np.arange(i, 0, -1)  # 产生n到 1的序列
                weights = np.true_divide(weights, weights.sum())
                self.data['wma_%s' % i] = np.convolve(
                    self.data[item], weights, mode='full')[:-i+1]
        self.updateColDict()
        return self

    def EWMA(self, n=30, item='c'):
        if self.multicode:
            grouped = self.data.groupby(self.code_columns)
            if not hasattr(n, '__iter__'):
                n = [n]
            for i in n:
                weights = np.arange(i, 0, -1)  # 产生n到 1的序列
                weights = np.true_divide(weights, weights.sum())
                wma = grouped[item].apply(
                    lambda x: np.convolve(x, weights, mode='full')[:-i+1])
                self.data['wma_%s' % i] = np.concatenate(wma.values)
        else:
            if not hasattr(n, '__iter__'):
                n = [n]
            for i in n:
                weights = np.arange(i, 0, -1)  # 产生n到 1的序列
                weights = np.true_divide(weights, weights.sum())
                self.data['wma_%s' % i] = np.convolve(
                    self.data[item], weights, mode='full')[:-i+1]
        self.updateColDict()
        return self

    def MIDMA(self):
        self.MA([30, 72])
        self.data['ma_mid'] = (6*self.data['ma_30']+1*self.data['ma_72'])/7
        self.updateColDict()
        return self

    def VOLMA(self, params):
        if not hasattr(params, '__iter__'):
            params = [params]
        self.data.sort_values([self.code_columns, 'date'], inplace=True)
        group = self.data.groupby(self.code_columns)
        for n in params:
            temp = group['volp', 'vol'].rolling(window=n, min_periods=0).sum()
            self.data['volma_%s' % n] = (
                temp.volp/temp.vol).values
        self.updateColDict()
        return self

    def HOLDDAY(self):
        if self.grouped:
            self.data['holdday'] = Cac_holdday(
                self.data, groupcol=self.groupcol)
        else:
            if len(self.code) < 7:
                self.data['holdday'] = Cac_holdday(self.data, groupcol='')
            else:
                self.data['holdday'] = 50
        self.holdday = np.array(self.data.holdday)
        self.updateColDict()
        return self

    def AVOLMA(self):
        if self.grouped:
            if set(['holdday'])-set(self.data.columns):
                self.HOLDDAY()
        else:
            if set(['holdday'])-set(self.data.columns):
                self.HOLDDAY()
        if len(self.code) < 7:
            self.data = AVOLMA(self.data)
            self.avolmaArr = np.array(self.data['avolma'])
        else:
            self.avolmaArr, *x = MA(np.array(self.data.c), 857)
            self.data['avolma'] = self.avolmaArr
        self.updateColDict('avolma')
        return self.avolmaArr

    def ATR(self, n=14):
        if self.multicode:
            tr = pd.DataFrame()
            tr['hl'] = self.data.h-self.data.l
            grouped = self.data.groupby('code')
            tr['hc'] = abs(self.data.h-grouped.c.shift(1)).replace(np.nan, 0)
            tr['lc'] = abs(self.data.l-grouped.c.shift(1)).replace(np.nan, 0)
            self.data['tr'] = tr.max(axis=1)
            if hasattr(n, '__iter__'):
                for i in n:
                    self.data['ATR_'+str(i)] = grouped.tr.rolling(i,
                                                                  min_periods=0).mean().values
            else:
                self.data['ATR_'+str(n)] = grouped.groupby(
                    'code').tr.rolling(n, min_periods=0).mean().values
        else:
            tr = pd.DataFrame()
            tr['hl'] = self.data.h-self.data.l
            tr['hc'] = abs(self.data.h-self.data.c.shift(1)).replace(np.nan, 0)
            tr['lc'] = abs(self.data.l-self.data.c.shift(1)).replace(np.nan, 0)
            self.data['tr'] = tr.max(axis=1)
            if hasattr(n, '__iter__'):
                for i in n:
                    self.data['ATR_'+str(i)] = self.data.tr.rolling(i,
                                                                    min_periods=0).mean()
            else:
                self.data['ATR_'+str(n)] = self.data.tr.rolling(n,
                                                                min_periods=0).mean()
        self.updateColDict()

    def DMI(self, period1=7, period2=7):
        self.indicator.update({'DMIArr': dmi(self.query('c'), self.query(
            'l'), self.query('h'), period1=period1, period2=period2)[-1]})

    def CYF(self, N=13):
        A1 = self.groupbycode.vol.rolling(
            window=N, min_periods=1).sum().values/self.data.ltgb.values
        CYF = 100-(100/(1+A1))
        self.data['cyf_'+str(N)] = CYF
        self.updateColDict()
        return self

    def CYW(self, n=13):
        """
        控盘强度
        """
        VAR1 = self.data.c-self.data.l+0.0000000000001
        VAR2 = self.data.h-self.data.l+0.0000000000001
        VAR3 = self.data.c-self.data.h
        self.data['cyw_'+str(n)] = (VAR1/VAR2+VAR3/VAR2)*self.data.volp
        self.data[self.data.h < self.data.l]['cyw_'+str(n)] = 0
        self.data['cyw_'+str(n)] = self.data.groupby(self.code_columns)['cyw_' +
                                                                        str(n)].rolling(window=n, min_periods=1).sum().values/10000
        self.updateColDict()
        return self

    def CHMO(self, period):
        if self.mulitcode:
            self.data = self.groupbycode.apply(partial(chmo, period=period))
        else:
            chmo(self.data, period=period)
        self.updateColDict()
        return self

    def profilData(self, stocklist):
        df = pd.DataFrame()
        for i in stocklist:
            self.setDataFrameByCode(i)
            df[str(i)] = self.data.c
        self.updateColDict()
        return df

    def rsi(self, n=14):
        prices = self.data.c
        deltas = np.diff(prices)
        seed = deltas[:n+1]
        up = seed[seed >= 0].sum()/n
        down = -seed[seed < 0].sum()/n
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100./(1. + rs)
        for i in range(n, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
                up = (up*(n - 1) + upval)/n
                down = (down*(n - 1) + downval)/n
                rs = up/down
                rsi[i] = 100. - 100./(1. + rs)
        self.rsi = rsi
        self.updateColDict()

    def Cac_Index(self, log=True, weight=' '):
        if (weight in self.data.columns) or (weight == 'ltgb'):
            if 'ltgb' not in self.data.columns:
                self.data.eval('ltgb=vol/hsl', inplace=True)
            if log:
                self.data['流动股本'] = np.log10(self.data[weight])
            else:
                self.data['流动股本'] = self.data[weight]
            weights = self.data.groupby('date')['流动股本'].agg(np.sum)  # 板块股本总量
            # 股本总量=np.log10(流动股本).groupby(by=流动股本.index).agg(np.sum)
            co = self.data.o*self.data['流动股本']  # 板块流动市值总量
            ch = self.data.h*self.data['流动股本']
            cl = self.data.l*self.data['流动股本']
            cc = self.data.c*self.data['流动股本']
            # avgp=self.data.avgp*流动股本
            # cvol=self.data.vol*流动股本
            # 成交额=self.data.amount.groupby('date').sum()#(self.data.volp*流动股本).groupby(by=流动股本.index).agg(np.sum) #板块成交额
            co = co.groupby('date').agg(np.sum)
            ch = ch.groupby('date').agg(np.sum)
            cl = cl.groupby('date').agg(np.sum)
            cc = cc.groupby('date').agg(np.sum)
            # avgp=avgp.groupby('date').agg(np.sum)
            # C=[(i,np.true_divide(o,股本总量),np.true_divide(h,股本总量),np.true_divide(l,股本总量),np.true_divide(c,股本总量)) for i,o,h,l,c in zip(co.index,co,ch,cl,cc)]
            # C=pd.DataFrame(C)
            B = pd.DataFrame()
            B['o'] = np.true_divide(co, weights)
            B['h'] = np.true_divide(ch, weights)
            B['l'] = np.true_divide(cl, weights)
            B['c'] = np.true_divide(cc, weights)
            # B['avgp']=np.true_divide(avgp,weights)
            B['hsl'] = self.data.hsl.groupby('date').mean()
            B['chg'] = self.data.chg.groupby('date').mean()
            B['vol'] = self.data.vol.groupby('date').sum()
            B['volp'] = self.data.volp.groupby('date').sum()
            return B
        else:
            data = self.data.copy()
            data = data[data.chg < 12].copy()
            data = data[data.date > 9*245].copy()
            data.sort_values(['code', 'date'], ascending=True, inplace=True)
            temp = data.groupby('date')[['vol', 'volp']].sum()
            temp1 = data.groupby('code', sort=False).c.shift(
                1).fillna(method='bfill')
            data['h'], data['o'], data['l'] = 100*data['h']/temp1-100, 100*data['o']/temp1 - \
                100, 100 * \
                data['l']/temp1 - \
                100  # Cac_chg(data[['code','h','o','l']],1,grouped=True)
            data = data.groupby('date', as_index=False).mean()
            data[['vol', 'volp']] = temp[['vol', 'volp']]
            data[['h', 'o', 'l', 'c']] = 1000 * \
                data[['h', 'o', 'l', 'chg']].apply(Cac_cumprod_chg)
            data['code'] = 'A'
        self.updateColDict()
        return data

    def Cac_chg(self, days, item='c'):
        """
        n days chg
        """
        if self.mulitcode:
            data = self.groupbycode.c
            self.data['chg_'+str(days)] = Cac_chg(data=data,
                                                  days=days, grouped=True)
        else:
            data = self.data.copy()
            self.data['chg_'+str(days)] = Cac_chg(data=data, days=days)
        self.updateColDict()
        return self

    def Cac_back_chg(self, n):
        """
        backtest n days chg
        """
        data = self.data.groupby('code').c
        x1 = data.shift(-n)
        x0 = data.shift(0)
        self.data['chg_'+str(n)] = 100*(x1-x0)/x0
        # self.data['chg_'+str(n)] = 100*self.data.groupby('code').c.apply(lambda x:x.shift(-n)/x-1)
        self.updateColDict()
        return self

    def get_last(self):
        return self.data.groupby(self.code_columns).agg('last').reset_index()

    def get_recent_ndays(self, n):
        # apply(lambda x:x.tail(n+1)).reset_index(drop=False)
        return self.data.groupby(self.code_columns).apply(lambda x: x[-n:]).reset_index(drop=True)

    def get_recent_ndaysDetail(self, n):
        temp = self.get_recent_ndays(n)
        ret = temp.groupby('code').h.max()
        ret['min_h'] = temp.groupby('code').l.min()
        self.updateColDict()
        return ret

    def Ref(self, n):
        return self.data.groupby(self.code_columns).apply(lambda x: x[-n-1:]).groupby(self.code_columns).agg('first').reset_index(drop=False)

    def get_first(self):
        return self.data.groupby(self.code_columns).agg('first').reset_index()

    def get_first_ndays(self, n):
        return self.data.groupby(self.code_columns).apply(lambda x: x[:n]).reset_index(drop=True)

    def fromDate(self, date):
        return self.data[self.data.date >= date]

    def Nef(self, n):
        return self.data.groupby(self.code_columns).apply(lambda x: x[:n]).reset_index(drop=True).groupby(self.code_columns).agg('last').reset_index()

    def add_zdbl(self):
        self.data['涨跌比率'] = self.data.date.map(zdblDict)
        self.updateColDict()
        return self

    def crosshhv(self):
        # 创n天新高
        self.data['sign'] = self.data.c-self.data.c.shift(1)
        if self.data.loc[self.data.index[-1], 'sign'] < 0:
            self.data.loc[self.data.index[-1], 'sign'] = 0
        else:
            n = 2
            while self.data.loc[self.data.index[-1], 'sign'] >= 0:
                self.data['sign'] = self.data.c - \
                    self.data.c.rolling(window=n, min_periods=0).max()
                n += 1
            self.data.loc[self.data.index[-1], 'sign'] = n-1
        self.data['hhvd'] = np.where(self.data.sign > 0, self.data.sign, 0)
    # def crosshhv(self):
    #     # 创n天新高
    #     arrc = np.array(self.data.c)
    #     arrc0 = arrc[-1]
    #     arrcf = arrc[:-1]
    #     n = 20
    #     def func(x, n):
    #         if arrc0 >= x[-n:]:
    #             return False
    #         else:
    #             return True
    #     while func(arrcf, n):
    #         n0 = 100
    #         while (n-n0) > 1:
    #             m = (n0+n)//2
    #             temp = func(data, m)
    #             if temp < 100:
    #                 n0 = m
    #             elif temp == 100:
    #                 n = m
    #                 break
    #             else:
    #                 n = m
    #         ret = n
    #     return ret

    def upcross(self, item1, item2):
        if not self.multicode:
            self.data[item1+'_upcross_' +
                      item2] = upcross(self.data, item1, item2)
        else:
            self.data[item1+'_upcross_'+item2] = np.concatenate(np.array(self.data.groupby(
                'code', sort=False).apply(partial(upcross, item1=item1, item2=item2))))

    def doublecross(self, item1, item2):
        if not self.multicode:
            self.data[item1+'_dcross_'+item2] = doubleupcrossDay(
                np.where(self.data[item1], self.data[item2]))
        else:
            self.data[item1+'_dcross_' +
                      item2] = np.where(self.data[item1] > self.data[item2], 1, -1)
            temp = self.data.groupby('code', as_index=False, sort=False)[
                item1+'_dcross_'+item2].apply(doubleupcrossDay)
            self.data[item1+'_dcross_'+item2] = np.concatenate(temp.values)

    def dwoncross(self, item1, item2):
        self.data[item1+'_downcross_' +
                  item2] = self.data[item1]-self.data[item2]
        self.data[item1+'_downcross_'+item2] = np.where((self.data[item1+'_downross_'+item2] < 0) & (
            self.data[item1+'_upcross_'+item2].shift(1) > 0), 1, 0)

    def log_return(self, data):
        return np.log(data/data.shift(1))

    def c_return(self):
        b = a[a.code == 601688]
        b.index = b.date
        b.sort_values('date', inplace=True)
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax1.plot(b.c)
        ax2.plot((ta(b).log_return(b.c).rolling(
            60, min_periods=0).std()).shift(-1), color='b')

    def ratio(self, n, item='c', oneStock=True):
        if oneStock:

            def func(y): return sm.OLS(
                y, sm.add_constant(np.arange(n))).fit().params[1]
            self.data[item +
                      '_ratio'] = self.data[item].rolling(n).apply(func).values
        else:

            def func(y): return sm.OLS(
                y, sm.add_constant(np.arange(n))).fit().params[1]
            ret = self.data.groupby(self.code_columns).apply(
                lambda x: x[item].rolling(n).apply(func, raw=True))
            if type(ret) == pd.Series:
                self.data[item+'_ratio'] = ret.values  # 批量
#            else:
#                self.data[item+'_ratio'] = ret.values[0]  #单个
        return self

    def ns(self):
        y = pd.DataFrame()
        index_ = self.sh
        index_.index = index_.date
        y['index_c_ratio'] = index_.ma_5_ratio
        y['index_c'] = index_.c
        self.MA(5)
        self.data.index = self.data.date
        y['c'] = self.data.ma_5
        code = self.data.code[0]
        self.ratio(5)
        y['c_ratio'] = self.data.c_ratio
        y.fillna(method='bfill', inplace=True)
        temp = y[['c', 'index_c']].rolling(20, min_periods=0).corr()
        temp.index.names = list(temp.index.names)[:-1]+['xxx']
        temp.reset_index(inplace=True)
        level_index = len(temp.index.names)-1
        y['corr_index'] = temp[temp.xxx == 'c']['index_c'].values
#
        y['sig1'] = np.where((y.corr_index < 0) & (y.c_ratio > 0), 1, 0)
        y['sig'] = np.where((y['index_c_ratio'] < 0) &
                            (y['c_ratio'] > 0), 1, 0)
        y[['index_c', 'c', 'sig', 'sig1']
          ][-300:].plot(subplots=True, grid=True, figsize=(16, 9))
        return y

    def load_indexData(self):
        self.setDataFrameByCode('000000')
        self.MA(5)
        self.ratio(5, item='ma_5')
        self.sh = self.data
        self.setDataFrameByCode('399001')
        self.ratio(5)
        self.sz = self.data

    def BuyOrSell(self):
        if 'holdday' not in self.data.columns:
            self.AVOLMA()
        cac_return(self.data)
        self.updateColDict()
        return self

    def toMonth(self, code=[]):
        if code:
            self.setDataFrameByCode(code)
        self.period = 'm'
        ret = self.DataDict.get(self.period)
        if ret is None:
            ret = toMonth(self.DataDict['d'])
            self.DataDict.update({'m': ret})
        return ret

    def toWeek(self, code=[]):
        if code:
            self.setDataFrameByCode(code)
        self.period = 'w'
        ret = self.DataDict.get(self.period)
        if ret is None:
            ret = toWeek(self.DataDict['d'])
            self.DataDict.update({'w': ret})
        return ret

    def add_Cw(self, cwdata):
        cond = [np.argmax(self.date[self.date <= i]) for i in cwdata.date]
        data = np.zeros_like(self.c)
        data[:] = np.nan
        data[cond] = cwdata
        return data

    def pattern1(self):
        # 东方通信
        y = 100*np.max(self.refs('c', 50)) / \
            np.min(self.refs('c', 50))-100  # 100
        self.AVOLMA()
        z = np.array(self.data.c - self.data.avolma)[-10:]
        cond1 = np.mean(self.refs('hsl', 50)) < 2*np.mean(self.refs('hsl', 5))
        cond2 = len(np.argwhere(z > 0)) > 9  # 近10天收盘价高于成本均线
        if cond1 and cond2:
            return y

    def pattern2(self):
        self.dayArr = self.dayArr[:-19, :]
        y = 100*np.max(self.refs('c', 100))/np.min(self.refs('c', 100))-100
        self.TSI()
        maxMask = np.argmax(self.tsiArr[-100:])
        minMask = np.argmin(self.tsiArr[-100:])
        fallDownChg = 100*self.ref('c', minMask)/self.ref('c', maxMask)-100
        fallDownTsi = 100 * \
            self.tsiArr[-100:][minMask]/self.tsiArr[-100:][maxMask]
        return y, fallDownChg, fallDownTsi


def volma250(cls):
    return np.true_divide(rolling_sum(cls.volp, 250), rolling_sum(cls.vol, 250))
# 计算新股上市数量
# histData.groupby('date').code.unique()
# prei = list(x.values[0])
# ret = []
# for i in x.values:
#    temp = list(set(prei)-set(i))
#    ret.append(temp)
#    prei = list(set(prei+list(i)))


def fillStockData(data):
    data = data[data.c > 0]
    data['isTrade'] = True
    z = np.zeros(((inttoday-np.int(data.date.iloc[0])+1), data.shape[1]))
    z[:] = np.nan
    _data = pd.DataFrame(z, columns=data.columns, index=range(
        np.int(data.date.iloc[0]), int(inttoday+1)))
    _data['isTrade'] = False
    _data.update(data)
    del data
    del z
    return _data.fillna(method='ffill')


if __name__ == '__main__':
    taarr = TA_arr()
    code = '300713'
    code = '300593'
    code = '000001'
    taarr.set_data(code)
    taarr.AVOLMA()
    taarr.data['deg'] = taarr.data.rolling(
        5, min_periods=5).avolma.apply(degrees)
    data = taarr.data
    f = crossDay(np.where(taarr.data.c-taarr.data.avolma > 0, 1, -1))
    ret = [0]
    for i in f:
        if i < -1:
            ret.append(-1)
        elif i > 1:
            ret.append(1)
        elif i == 0 and ret[-1] > 0:
            ret.append(ret[-1]+1)
        elif i == 0 and ret[-1] < 0:
            ret.append(ret[-1]-1)
        else:
            ret += [i]
    data['crossday'] = ret[1:]
    if len(data) > 100:
        n = 5
        data[f'最大涨幅_{n}日'] = 100*np.max(rolling_window(
            taarr.query('c')[::-1], n), axis=1)[::-1]/taarr.query('c')-100
        data[f'最大跌幅_{n}日'] = 100*np.min(rolling_window(
            taarr.query('c')[::-1], n), axis=1)[::-1]/taarr.query('c')-100
        data[f'最大涨幅_前{n}日'] = 100*np.nanmin(rolling_window(
            taarr.query('c'), n), axis=1)/taarr.query('c')-100
        data[f'最大跌幅_前{n}日'] = 100 * \
            np.min(rolling_window(taarr.query('c'), n),
                   axis=1)/taarr.query('c')-100
        data['target'] = np.where(data[f'最大涨幅_{n}日'] > 20, 1, 0)
        data['target'] = (data['target'].shift(1) - data['target']).shift(-1)
        taarr.data['最大回撤率'] = taarr.data.c.rolling(10, min_periods=0).apply(
            lambda x: MaxDrawdown(np.array(x)), raw=True)
        data[data.deg > 55].最大涨幅_5日.mean()
        data[data.deg > 55].最大跌幅_5日.mean()
    taarr.data.index = taarr.data.index.astype(str)
    taarr.data.c.plt()
#    from SystemDir import datadir,configure_dir,getpath
#    hdf_file = pd.HDFStore(getpath('ntesCsv'))
#    histData = hdf_file.select('ntes',auto_close=True)
#    histData = hdf_file.select('ntes',where="code == 1",auto_close=True)
#    try:
#        taarr = TA_arr(histData)
#    except:
#        from load_histData import histData
#        taarr = TA_arr(histData)
#    colDict = {}
#    [colDict.update({col:idx}) for idx,col in enumerate(histData.columns)]
    # plt.close('all')
#    x.setDataFrameByCode('300104')
#    x.AVOLMA()
#    x1=TA()
#    x1.setDataFrame(x.monthData())
#    x1.HPTP(item='c')
#    x1.data['y'] = x1.data['主力']#-x1.data['散户']
#    x1.data.reset_index(inplace=True,drop=True)
#    temp = x1.data[['c','y']].rolling(5,min_periods=0).corr()
#    temp.index.names=list(temp.index.names)[:-1]+['xxx']
#    temp.reset_index(inplace=True)
#    level_index = len(temp.index.names)-1
#    x1.ratio(5,item='c')
#    x1.ratio(5,item='主力')
#    x1.data['corr'] = temp[temp.xxx=='y'].c.values
#    #x1.data[['c','y','corr']].plot(grid=True,figsize=(16,9),marker='.',subplots=True)
#    x1.data['sig'] = np.where((x1.data.c_ratio<0) & (x1.data.主力_ratio>0),1,0)
#    x1.data['sig'] = np.where((x1.data.c_ratio>0) & (x1.data.主力_ratio<0),-1,x1.data.sig)
#    x1.data[['c','sig']].plot(grid=True,figsize=(16,9),marker='.',subplots=True)
#    x.ns()
#    #x1['x']=[x1[i][0] for i in range(len(x1)) if (np.divmod(i,2)[1]>0)]
#    # x.MIDMA()
#    # x.data[x.data.date>'2000'][['c','ma_mid','ma_20']].plot(figsize=(25,15),grid=True)
# find stong sell price
#    ret = []
#    cp=x.data[-1:].c.values[0]
#    for n in range(5,len(x.data)+1,5):
#        x.VOLMA(n)
#        y=x.data[-1:]['volma_'+str(n)].values[0]
#        if (y>cp) & (((y-cp)/cp)<0.1):
#            ret.append(n)
    # find out the recent transaction days
# taarr.set_data('1399006')
# x = toWeek(taarr.data)
# x['ffq']=1
# taarr.set_data(x)
# taarr.EMA(13)
# taarr.EMA(8)
# taarr.EMA(5)
# taarr.data.index = range(len(taarr.data))
# taarr.data[['ema_5','ema_8']][-200:].plt(subplots=False)
# taarr.data[['ema_8','ema_21']].plt(subplots=False)
# taarr.data[['ema_8','ema_21']][-200:].plt(subplots=False)
# taarr.data[['ema_8','ema_13']][-200:].plt(subplots=False)
# taarr.data[['ema_5','ema_13']][-200:].plt(subplots=False)
# taarr.data[['c']][-200:].plt(subplots=False)
# ret = []
# for i in getStockList_cninfo():
#     try:
#         tmp = dmi_wk(i)
#         if tmp:
#             ret.append(tmp)
#         else:
#             pass
#     except Exception as e:
#         print(e)
#         print(i)


def dmi_wk(code='603926'):
    taarr.set_data(code)
    x = toWeek(taarr.data)
    y = dmi(np.array(x.c), np.array(x.l), np.array(x.h))[-1]
    ret = dict(zip(['pdi', 'ndi', 'adx', 'adxr'], y[-1]))
    z = y[:, 0]-y[:, 1]
    crossday_dmi = len(z) - np.argwhere(z < 0)[-1][-1]-1
    if crossday_dmi:
        total_hsl = x[-crossday_dmi:].hsl.sum()
        zf = 100*x[-crossday_dmi:].c.max()/x[-crossday_dmi:].c.min()-100
        ret.update({'code': code, 'hsl': total_hsl,
                   'zf': zf, 'day': crossday_dmi})
    else:
        ret.update({'code': code})
    return ret
# 周dmi:adx>90,pdi<ndi pdi<10 可能见底
#     adx>90,pdi>ndi ndi<10 可能见顶
