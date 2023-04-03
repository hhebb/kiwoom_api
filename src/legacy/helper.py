import pymysql

order_col_names = ['id', 'time',
                   'ask_1', 'ask_1_amt', 'bid_1', 'bid_1_amt', 'ask_2', 'ask_2_amt', 'bid_2', 'bid_2_amt',
                   'ask_3', 'ask_3_amt', 'bid_3', 'bid_3_amt', 'ask_4', 'ask_4_amt', 'bid_4', 'bid_4_amt',
                   'ask_5', 'ask_5_amt', 'bid_5', 'bid_5_amt']
order_col_names_2 = ['id', 'time',
                      'ask_1', 'ask_1_amt', 'ask_1_before', 'bid_1', 'bid_1_amt', 'bid_1_before',
                      'ask_2', 'ask_2_amt', 'ask_2_before', 'bid_2', 'bid_2_amt', 'bid_2_before',
                      'ask_3', 'ask_3_amt', 'ask_3_before', 'bid_3', 'bid_3_amt', 'bid_3_before',
                      'ask_4', 'ask_4_amt', 'ask_4_before', 'bid_4', 'bid_4_amt', 'bid_4_before',
                      'ask_5', 'ask_5_amt', 'ask_5_before', 'bid_5', 'bid_5_amt', 'bid_5_before']
trans_col_names = ['id', 'time', 'price', 'amount']

code_list = ['001770', '002290', '002690', '005670', '008370', '008470', '009140', '010420', '010640', '011420'] + \
            ['005930', '005380', '066570']
fid_list = ['20',  # 체결 시간
                         '10',  # 현재가
                         '15',  # 거래량
                         '228',  # 체결강도
                         '21',  # 호가 시간

                         '41',  # 매도 호가 1
                         '61',  # 매도 호가 1 수량
                         '81',  # 매도 호가 1 직전 대비
                         '51',  # 매수 호가 1
                         '71',  # 매수 호가 1 수량
                         '91',  # 매수 호가 1 직전 대비

                         '42',  # 매도 호가 2
                         '62',  # 매도 호가 2 수량
                         '82',  # 매도 호가 2 직전 대비
                         '52',  # 매수 호가 2
                         '72',  # 매수 호가 2 수량
                         '92',  # 매수 호가 2 직전 대비

                         '43',  # 매도 호가 3
                         '63',  # 매도 호가 3 수량
                         '83',  # 매도 호가 3 직전 대비
                         '53',  # 매수 호가 3
                         '73',  # 매수 호가 3 수량
                         '93',  # 매수 호가 3 직전 대비

                         '44',  # 매도 호가 4
                         '64',  # 매도 호가 4 수량
                         '84',  # 매도 호가 4 직전 대비
                         '54',  # 매수 호가 4
                         '74',  # 매수 호가 4 수량
                         '94',  # 매수 호가 4 직전 대비

                         '45',  # 매도 호가 5
                         '65',  # 매도 호가 5 수량
                         '85',  # 매도 호가 5 직전 대비
                         '55',  # 매수 호가 5
                         '75',  # 매수 호가 5 수량
                         '95',  # 매수 호가 5 직전 대비

                         # '27',  # 우선 매수 호가
                         # '28',  # 우선 매수 호가
                         ]

# SQL
def get_create_query(table_1, table_2):
    create_trans_query = f'''CREATE TABLE {table_1} (
                            id int NOT NULL PRIMARY KEY,
                            time datetime,
                            price int(255),
                            amount int(255)
                            )
                            '''

    create_order_query = f'''CREATE TABLE {table_2} (
                            id int NOT NULL PRIMARY KEY,
                            time datetime,
                            ask_1 int(255),
                            ask_1_amt int(255),
                            ask_1_before int(255),
                            bid_1 int(255),
                            bid_1_amt int(255),
                            bid_1_before int(255),
                            ask_2 int(255),
                            ask_2_amt int(255),
                            ask_2_before int(255),
                            bid_2 int(255),
                            bid_2_amt int(255),
                            bid_2_before int(255),
                            ask_3 int(255),
                            ask_3_amt int(255),
                            ask_3_before int(255),
                            bid_3 int(255),
                            bid_3_amt int(255),
                            bid_3_before int(255),
                            ask_4 int(255),
                            ask_4_amt int(255),
                            ask_4_before int(255),
                            bid_4 int(255),
                            bid_4_amt int(255),
                            bid_4_before int(255),
                            ask_5 int(255),
                            ask_5_amt int(255),
                            ask_5_before int(255),
                            bid_5 int(255),
                            bid_5_amt int(255),
                            bid_5_before int(255)
                            )
                            '''
    return create_trans_query, create_order_query

def get_insert_trans_query(table):
    q = f'''INSERT INTO {table} (id, time, price, amount) VALUES (%s, %s, %s, %s)'''

    return q


def get_insert_order_query(table):
    q = f'''INSERT INTO {table} (id, time, 
            ask_1, ask_1_amt, ask_1_before, bid_1, bid_1_amt, bid_1_before, 
            ask_2, ask_2_amt, ask_2_before, bid_2, bid_2_amt, bid_2_before, 
            ask_3, ask_3_amt, ask_3_before, bid_3, bid_3_amt, bid_3_before, 
            ask_4, ask_4_amt, ask_4_before, bid_4, bid_4_amt, bid_4_before, 
            ask_5, ask_5_amt, ask_5_before, bid_5, bid_5_amt, bid_5_before) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

    return q


def get_connection():
    conn = pymysql.connect(host='localhost',
                    user='root',
                    password='0000',
                    database='kiwoom')
    cursor = conn.cursor()

    return conn, cursor


def formatter_screen(n):
    l = len(str(n))
    k = 4-l
    form = k*'0' + str(n)
    return form