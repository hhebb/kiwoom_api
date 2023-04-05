from .base_exhange import Exchange
from PyQt5.QAxContainer import *
import pythoncom
import queue
import time
import pandas as pd

class KiwoomExchange(Exchange):
    def __init__(self):
        super().__init__()
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.login = False
        self.tr = False
        self.tr_queue = queue.Queue() # buffer
        # self.tr_data = dict()

    def connect(self):
        self.CommConnect()
    

    def set_preference(self, preference):
        self.preference = preference

    def get_data(self):
        # 마지막 처리 필요

        # decode self.preference
        # self.preference.items
        # self.preference.data_type
        # self.preference.range
        # self.preference.period
        self.start_date = self.preference.range[0]
        self.end_date = self.preference.range[1]
        self.cur_date = self.start_date
        
        buffer = list()

        for code in list(5):
            while True:
                self.SetInputValue("종목코드", code)
                self.SetInputValue("기준일자", "20050612")
                self.SetInputValue("수정주가구분", "0")
                self.CommRqData("ex", "opt10081", next, "0101")
                # tr_data, remain = self.tr_queue.get()
                time.sleep(1)

                # self.tr_queue.put(tr_data)
                while self.tr_queue[0].date != self.cur_date:
                    price, remain = self.tr_queue.get()
                    buffer.append(price)
                
                if len(buffer) > 0:
                    pd.DataFrame() # to dataframe
                    yield buffer
                    buffer = list()
                    self.cur_date = self.tr_queue[0].date

                # no more data, no more loop
                if remain == '2':
                    next = 2
                    self.tr = True
                else:
                    break
                

    #####################################################
    # API dependent

    def CommConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        while self.login is False:
            pythoncom.PumpWaitingMessages()

    def OnEventConnect(self, code):
        self.login = True
        print("login is done", code)

    def OnReceiveTrData(self, screen, rqname, trcode, record, next):
        # rqname 에 ex 붙여서 통째로 받는 방법도 만들어놓기
        print(screen, rqname, trcode, record, next)
        self.tr = True

        name = self.GetCommData(trcode, rqname, 0, "종목명")
        per = self.GetCommData(trcode, rqname, 0, "PER")
        pbr = self.GetCommData(trcode, rqname, 0, "PBR")

        data = (name, per, pbr)
        self.tr_data[trcode] = data
        self.tr_queue.put((data, next))

    def GetCodeListByMarket(self, market):
        ret = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market)
        codes = ret.split(';')[:-1]
        return codes

    def GetMasterCodeName(self, code):
        ret = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        return ret

    def SetInputValue(self, id, value):
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)

    def CommRqData(self, rqname, trcode, next, screen):
        self.tr = False
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen)
        while self.tr is False:
            pythoncom.PumpWaitingMessages()

    def GetCommData(self, trcode, rqname, index, item):
        data = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, index, item)
        return data.strip()
    
    def GetCommDataEx(self, trcode, rqname):
        data = self.ocx.dynamicCall("GetCommDataEx(QString, QString)", trcode, rqname)
        return data


    def GetRepeatCnt(self, trcode, record):
        data = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, record)
        return data        