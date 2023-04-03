import time
import kwapi
from PyQt5.QtCore import QThread
import csv
import datetime
import helper


class Order:
    def __init__(self, order_id, con_id, code, in_price, in_time, rate):
        self.order_id = order_id # 식별자
        self.con_id = con_id
        self.code = code
        self.in_price = in_price
        self.in_time = in_time
        self.trail = in_price
        self.stop_rate = rate
        self.out_price = None

    def trailing_stop(self, cur):
        if self.trail < cur:
            # print("up", self.trail, cur)
            self.trail = cur
        elif self.trail * (1 - 0.01 * self.stop_rate) > cur:
            self.out_price = cur
            return "stop"
        else:
            return "hold"


class ConditionTrader(QThread):
    def __init__(self, logger=None):
        super(QThread, self).__init__()
        self.order_tag = 1 # order 의 식별자
        self.total_orders = dict()
        self.stop_rate = 3
        self.ocx = None
        self.watch_list = set()
        self.current_prices = dict()
        self._today = datetime.datetime.today().date()
        self._logger = logger

    def get_order_tag(self):
        return self.order_tag

    def set_ocx(self, ocx):
        if not self.ocx:
            self.ocx = ocx

        # self.ocx.OnReceiveTrData.connect(self._on_receive_tr_data)

    def update_price(self, code, price):
        to_remove = list()
        for o_id, order in self.total_orders.items():
            if order.code == code:
                if not order.in_price:
                    order.in_price = price
                    order.trail = price
                else:
                    result = order.trailing_stop(price)
                    if result == 'stop':
                        # record
                        to_remove.append(o_id)
                        self.record_result(order)
                        
                    elif result == 'hold':
                        pass

        # split alive, dead orders
        to_remove_orders = dict()
        remain_orders = dict()
        for o_id, order in self.total_orders.items():
            if o_id in to_remove:
                to_remove_orders[o_id] = order
            else:
                remain_orders[o_id] = order
        self.total_orders = remain_orders
        avail_codes = set([order.code for order in self.total_orders.values()])

        # hard kill orders, undescribe
        hard_remove_id = list()
        for o_id, order in to_remove_orders.items():
            if order.code not in avail_codes:
                hard_remove_id.append(o_id)
        [kwapi.disconnect_real_data(self.ocx, helper.formatter_screen(o_id)) for o_id in hard_remove_id]


    def record_result(self, order):
        # csv 코드 재사용하기
        with open(f"trade_result/result_{self._today}.csv", "a", encoding="utf-8", newline="") as f:
            wr = csv.writer(f)
            wr.writerow([order.order_id, order.con_id, order.code, order.in_price, order.out_price])
            f.close()
        if self._logger:
            self._logger.info(f"end order - {order.con_id} - {order.code} - {order.in_price} {order.out_price} total: {len(self.total_orders)}")

    def is_valid_order(self, code, con_id):
        for o_id, order in self.total_orders.items():
            if con_id == order.con_id and code == order.code:
                return False
        return True

    def find_del_order(self, code, con_id):
        for o in self.pending_orders:
            if o.code == code and o.con_id == con_id:
                return o

    def add_order(self, code, type, con_id):
        """
        """
        if type == 'I':
            # add
            if self.is_valid_order(code, con_id):
                self._logger.info(f'added {code}')
                order = Order(self.order_tag, con_id, code, None, None, self.stop_rate)
                self.total_orders[self.order_tag] = order
                self.order_tag += 1

    """
        handler
    """

    """
        other
    """

    def clear_orders(self):
        while self.total_orders:
            key, order = self.total_orders.popitem()
            kwapi.disconnect_real_data(self.ocx, helper.formatter_screen(order.order_id))
            kwapi.set_input_value(self.ocx, '종목코드', order.code)
            kwapi.comm_rq_data(self.ocx, 'opt10001', 'opt10001', 0, '0101')
            self.record_result(order)


    def run(self):
        while True:
            # 15 시 05 분 되면 모두 청산
            if datetime.datetime.now().time() > datetime.time(hour=10, minute=30):
                self.clear_orders()
                break

            time.sleep(10)
