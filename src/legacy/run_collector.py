import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from datetime import datetime
import pymysql.cursors
import logging

import trader
import kwapi
import preprocess
import helper


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real")
        self.setGeometry(300, 300, 300, 400)

        # logging
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler('log/trader.log', mode='w', encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # field
        self.conditions = dict() # 저장할 실시간 검색 레코드
        self._cursor = None
        self.today = None
        self._db_login()
        self.tables = self._create_tables()
        self.counters = {table: 0 for table in self.tables}
        self.trader = trader.ConditionTrader(logger=self.logger)

        # UI
        btn = QPushButton("구독", self)
        btn.move(20, 20)
        btn.clicked.connect(self._on_clicked_real_reg)

        btn2 = QPushButton("해지", self)
        btn2.move(180, 20)
        btn2.clicked.connect(self._on_clicked_disconnect_real_data)

        btn_cond_load = QPushButton("condition down")
        btn_cond_list = QPushButton("condition list")
        btn_cond_req = QPushButton("condition send")
        btn_cond_stop = QPushButton("condition stop")
        btn_test = QPushButton("test")

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(btn)
        layout.addWidget(btn2)
        layout.addWidget(btn_cond_load)
        layout.addWidget(btn_cond_list)
        layout.addWidget(btn_cond_req)
        layout.addWidget(btn_cond_stop)
        layout.addWidget(btn_test)
        self.setCentralWidget(widget)

        # UI event handler
        btn_cond_load.clicked.connect(self._on_clicked_condition_load)
        btn_cond_list.clicked.connect(self._on_clicked_condition_name_list)
        btn_cond_req.clicked.connect(self._on_clicked_send_condition)
        btn_cond_stop.clicked.connect(self._on_clicked_send_condition_stop)
        btn_test.clicked.connect(self._on_clicked_test)

        # ocx event handler
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self._on_login)
        self.ocx.OnReceiveTrData.connect(self._on_get_tr_data)
        self.ocx.OnReceiveRealData.connect(self._on_get_real_data)
        self.ocx.OnReceiveConditionVer.connect(self._on_load_condition)
        self.ocx.OnReceiveRealCondition.connect(self._on_get_real_condition)

        # 2초 후에 로그인 진행
        QTimer.singleShot(2000, lambda: kwapi.comm_connect(self.ocx))

    ###
    def _create_conn(self):
        conn = pymysql.connect(host='localhost',
                               user='root',
                               password='0000',
                               database='kiwoom')
        return conn

    def _db_login(self):
        setattr(self, '_conn', self._create_conn())
        setattr(self, '_cursor', self._conn.cursor())

    def _create_tables(self):
        now = datetime.now()
        date = datetime.strftime(now, '%Y%m%d')
        self.today = date
        tables = []
        for code in helper.code_list:
            table_per_code = self._create_single_table(date, code)
            tables.extend(table_per_code)

        return tables

    def _create_single_table(self, date, code):
        table_1 = f'{date}_trans_{code}'
        table_2 = f'{date}_order_{code}'
        trans_query, order_query = helper.get_create_query(table_1, table_2)
        try:
            self._cursor.execute(trans_query)
            self._cursor.execute(order_query)
        except:
            print(f'table {table_1}, {table_2}is already exist.')

        getattr(self, '_conn', self._create_conn()).commit()

        return [table_1, table_2]

    '''
    others
    '''


    '''
    handler functions
    '''

    def _on_login(self, err_code):
        if err_code == 0:
            self.statusBar().showMessage("login 완료")
            self.logger.info('login')

    def _on_get_tr_data(self, screen, rqname, trcode, record, next):
        price = kwapi.get_comm_data(self.ocx, trcode, rqname, 0, '현재가')
        code = kwapi.get_comm_data(self.ocx, trcode, rqname, 0, '종목코드')
        self.trader.update_price(code, price)
        self.logger.info(f'clear order {code} {price}')

    def _on_get_real_data(self, code, real_type, data):
        if real_type == '주식체결':
            price = kwapi.get_comm_real_data(self.ocx, code, 10)
            price = abs(int(price))
            self.trader.update_price(code, price)

        # elif real_type == '주식체결':
        #     table = f'{self.today}_trans_{code}'
        #     self.counters[table] += 1
        #     time = kwapi.get_comm_real_data(self.ocx, code, 20)
        #     date = datetime.now().strftime("%Y-%m-%d ")
        #     time = datetime.strptime(date + time, "%Y-%m-%d %H%M%S")

        #     tr_price = kwapi.get_comm_real_data(self.ocx, code, 10)
        #     tr_vol = kwapi.get_comm_real_data(self.ocx, code, 15)
        #     # tr_force = kwapi.get_comm_real_data(code, 228)

        #     q = helper.get_insert_trans_query(table)
        #     self._cursor.execute(q, (self.counters[table], time, tr_price, tr_vol))
        #     self._conn.commit()

        # elif real_type == '주식호가잔량':
        #     table = f'{self.today}_order_{code}'
        #     self.counters[table] += 1
        #     time = kwapi.get_comm_real_data(self.ocx, code, 21)
        #     date = datetime.now().strftime("%Y-%m-%d ")
        #     time = datetime.strptime(date + time, "%Y-%m-%d %H%M%S")

        #     ask_1 = kwapi.get_comm_real_data(self.ocx, code, 41)
        #     ask_1_amount = kwapi.get_comm_real_data(self.ocx, code, 61)
        #     ask_1_before = kwapi.get_comm_real_data(self.ocx, code, 81)
        #     bid_1 = kwapi.get_comm_real_data(self.ocx, code, 51)
        #     bid_1_amount = kwapi.get_comm_real_data(self.ocx, code, 71)
        #     bid_1_before = kwapi.get_comm_real_data(self.ocx, code, 91)

        #     ask_2 = kwapi.get_comm_real_data(self.ocx, code, 42)
        #     ask_2_amount = kwapi.get_comm_real_data(self.ocx, code, 62)
        #     ask_2_before = kwapi.get_comm_real_data(self.ocx, code, 82)
        #     bid_2 = kwapi.get_comm_real_data(self.ocx, code, 52)
        #     bid_2_amount = kwapi.get_comm_real_data(self.ocx, code, 72)
        #     bid_2_before = kwapi.get_comm_real_data(self.ocx, code, 92)

        #     ask_3 = kwapi.get_comm_real_data(self.ocx, code, 43)
        #     ask_3_amount = kwapi.get_comm_real_data(self.ocx, code, 63)
        #     ask_3_before = kwapi.get_comm_real_data(self.ocx, code, 83)
        #     bid_3 = kwapi.get_comm_real_data(self.ocx, code, 53)
        #     bid_3_amount = kwapi.get_comm_real_data(self.ocx, code, 73)
        #     bid_3_before = kwapi.get_comm_real_data(self.ocx, code, 93)

        #     ask_4 = kwapi.get_comm_real_data(self.ocx, code, 44)
        #     ask_4_amount = kwapi.get_comm_real_data(self.ocx, code, 64)
        #     ask_4_before = kwapi.get_comm_real_data(self.ocx, code, 84)
        #     bid_4 = kwapi.get_comm_real_data(self.ocx, code, 54)
        #     bid_4_amount = kwapi.get_comm_real_data(self.ocx, code, 74)
        #     bid_4_before = kwapi.get_comm_real_data(self.ocx, code, 94)

        #     ask_5 = kwapi.get_comm_real_data(self.ocx, code, 45)
        #     ask_5_amount = kwapi.get_comm_real_data(self.ocx, code, 65)
        #     ask_5_before = kwapi.get_comm_real_data(self.ocx, code, 85)
        #     bid_5 = kwapi.get_comm_real_data(self.ocx, code, 55)
        #     bid_5_amount = kwapi.get_comm_real_data(self.ocx, code, 75)
        #     bid_5_before = kwapi.get_comm_real_data(self.ocx, code, 95)

        #     q = helper.get_insert_order_query(table)

        #     self._cursor.execute(q, (self.counters[table], time,
        #                             ask_1, ask_1_amount, ask_1_before, bid_1, bid_1_amount, bid_1_before,
        #                             ask_2, ask_2_amount, ask_2_before, bid_2, bid_2_amount, bid_2_before,
        #                             ask_3, ask_3_amount, ask_3_before, bid_3, bid_3_amount, bid_3_before,
        #                             ask_4, ask_4_amount, ask_4_before, bid_4, bid_4_amount, bid_4_before,
        #                             ask_5, ask_5_amount, ask_5_before, bid_5, bid_5_amount, bid_5_before))
        #     self._conn.commit()

    def _on_load_condition(self, ret, msg):
        self.logger.info(f'condition load - {ret, msg}')

    def _on_get_real_condition(self, code, type, cond_name, cond_index):
        # 실시간 조건 만족할 때 수신
        # self.logger.info(f'get condition watch - {code, type, cond_name, cond_index}')
        self.trader.add_order(code, type, cond_name)
        order_id = self.trader.get_order_tag() # formatting 해야함?
        form = helper.formatter_screen(order_id)
        kwapi.set_real_reg(self.ocx, form, code, '10', 0) # 현재가

    def _on_clicked_real_reg(self):
        kwapi.set_real_reg(self.ocx, '1000', ';'.join(helper.code_list), ';'.join(helper.fid_list), 0)
        self.statusBar().showMessage('실시간 요청 완료')

    def _on_clicked_disconnect_real_data(self):
        kwapi.disconnect_real_data(self.ocx, '1000')
        self.statusBar().showMessage('실시간 구독 해지')

    def _on_clicked_condition_load(self):
        kwapi.get_condition_load(self.ocx)
        self.statusBar().showMessage('검색식 로드')

    def _on_clicked_condition_name_list(self):
        self.conditions = kwapi.get_condition_name_list(self.ocx)

    def _on_clicked_send_condition(self):
        # 검색식 최대 10 개 까지
        for con_i, con_name in self.conditions.items():
            kwapi.send_condition(self.ocx, '100', con_name, con_i, 1)

        self.trader.set_ocx(self.ocx)
        self.trader.start()
        self.statusBar().showMessage('검색식 실시간 감시')

    def _on_clicked_send_condition_stop(self):
        for con_i, con_name in self.conditions.items():
            kwapi.send_condition_stop(self.ocx, "100", con_name, con_i)
        self.statusBar().showMessage(f'검색식 감시 중지')

    def _on_clicked_test(self):
        for code in ['119860', '066620', '036640']:
            kwapi.set_input_value(self.ocx, '종목코드', code)
            kwapi.comm_rq_data(self.ocx, 'opt10001', 'opt10001', 0, '2222')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
