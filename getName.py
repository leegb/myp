# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')



def getName(code):
    return 'x1'




# from webData.cninfo import stockshortname
# #from webData.zscodeClient import zscodeClient
# from Jrj.quotes_jrj import quotes_jrj
# from basefunc import int2str
# from tools.dateClient import dateClient as dateClient
# from tools.pandas_util import pd
# from dbConstant import jrjDayDB, dateDB
# _temp = pd.DataFrame(jrjDayDB.collection.find(
#     {'date': dateClient().lastTradedate()['intdate']}))
# i = dateDB.collection.count_documents({})-1
# while len(_temp) == 0:
#     try:
#         i -= 1
#         _temp = pd.DataFrame(jrjDayDB.collection.find(
#             {'date': dateDB.collection.find_one({'seq': i, 'trade': True})['intdate']}))
#     except:
#         break
# code2nameDict = {}  # zscodeClient().code2name
# #_temp =  int2str(quotes_jrj().parse())
# if len(_temp):
#     code2nameDict.update(dict(zip(_temp['code'], _temp['name'])))
# _temp = pd.DataFrame(stockshortname().db.collection.find(
#     {'ZQJC': {'$nin': [None]}}, {'ZQJC', 'code'}))
# if len(_temp):
#     code2nameDict.update(dict(zip(_temp['code'], _temp['ZQJC'])))

# def getName(code):
#     name = code2nameDict.get(code)
#     if name:
#         return name
#     else:
#         return 'xxxxxx'
