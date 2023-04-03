from PyQt5.QAxContainer import *
import pythoncom
import queue

class Kiwoom:
    def __init__(self):
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.login = False
        self.tr = False
        self.tr_queue = queue.Queue()
        self.tr_data = dict()


    def OnReceiveTrData(self, screen, rqname, trcode, record, next):
        self.tr = True

        rows = self.GetRepeatCnt(trcode, record) 
        if rows == 0:
            rows = 1

        if rqname == 'ex':
            data = self.GetCommDataEx(trcode, rqname)
        else:
            data = []
            for row in range(rows):
                vol = self.GetCommData(trcode, rqname, row, "거래량")
                open = self.GetCommData(trcode, rqname, row, "시가")
                high  = self.GetCommData(trcode, rqname, row, "고가")
                close  = self.GetCommData(trcode, rqname, row, "종가")
                low  = self.GetCommData(trcode, rqname, row, "저가")
                data.append([open, high, low, close, vol])

        self.tr_queue.put((data, next))


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