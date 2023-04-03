from .base_exhange import Exchange
from PyQt5.QAxContainer import *
import pythoncom
import queue
import time

class KiwoomExchange(Exchange):
    def __init__(self):
        super().__init__()
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.login = False
        self.tr = False
        self.tr_queue = queue.Queue()
        self.tr_data = dict()

    def connect(self):
        self.CommConnect
    

    def set_preference(self, preference):
        self.prefernce = preference

    def get_data(self):
        # decode self.prefernce
        # self.prefernce.items
        # self.prefernce.data_type
        # self.prefernce.range
        # self.prefernce.period

        for code in list(5):
            while True:
                self.SetInputValue("종목코드", code)
                self.SetInputValue("기준일자", "20050612")
                self.SetInputValue("수정주가구분", "0")
                self.CommRqData("ex", "opt10081", next, "0101")
                tr_data, remain = self.tr_queue.get()
                time.sleep(1)

                if remain == '2':
                    next = 2
                    self.tr = True
                else:
                    break
                
                if True: # collector 가 쌓을 수 있는 양이 되었을 때 yield
                    yield tr_data
            

    #####################################################
    # API dependent

    def CommConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        while self.login is False:
            pythoncom.PumpWaitingMessages()

    def OnEventConnect(self, code):
        self.login = True
        print("login is done", code)

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