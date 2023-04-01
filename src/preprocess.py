import pandas as pd
import helper


# for trans
def get_trans_vpin(trans_df, max_capa=20000, window=5):
    """
        maybe need cut out by time (0900~1520)
        proxy of PIN, volatility
    """

    amounts = trans_df["amount"]
    cur_i, buy, sell, b_cnt, s_cnt = 1, 0, 0, 0, 0
    buckets = []

    # vol buckets
    while len(trans_df) > cur_i:
        if amounts[cur_i] >= 0:
            buy += amounts[cur_i]
            b_cnt += 1
        else:
            sell += amounts[cur_i]
            s_cnt += 1

        if buy + (-sell) >= max_capa:
            buckets.append((cur_i, buy, sell, b_cnt, s_cnt))
            buy, sell, b_cnt, s_cnt = 0, 0, 0, 0
        cur_i += 1

    vol_buckets = pd.DataFrame(buckets)
    vol_buckets.columns = ["trans_idx", "buy", "sell", "buy_cnt", "sell_cnt"]

    # vpin
    #     vpin = abs(vol_buckets['buy'].rolling(window).sum() + vol_buckets['sell'].rolling(window).sum()) / (max_capa * window)
    vpin = abs(vol_buckets["buy"] + vol_buckets["sell"]) / (
        vol_buckets["buy"] - vol_buckets["sell"]
    )
    vol_buckets["vpin"] = vpin

    return vol_buckets


# for order
def get_sobi(df: pd.DataFrame):
    """
    params:
        df: dataframe

    return:
        mid_vwap: mid_vwap
        mid_price: mid_price

    """
    vol_ask = (
        df[f"ask_1_amt"]
        + df[f"ask_2_amt"]
        + df[f"ask_3_amt"]
        + df[f"ask_4_amt"]
        + df[f"ask_5_amt"]
    )
    vol_bid = (
        df[f"bid_1_amt"]
        + df[f"bid_2_amt"]
        + df[f"bid_3_amt"]
        + df[f"bid_4_amt"]
        + df[f"bid_5_amt"]
    )

    tmp_ask = [abs(df[f"ask_{i}"] * df[f"ask_{i}_amt"]) for i in range(1, 6)]
    tmp_bid = [abs(df[f"bid_{i}"] * df[f"bid_{i}_amt"]) for i in range(1, 6)]

    total_ask = tmp_ask[0] + tmp_ask[1] + tmp_ask[2] + tmp_ask[3] + tmp_ask[4]
    total_bid = tmp_bid[0] + tmp_bid[1] + tmp_bid[2] + tmp_bid[3] + tmp_bid[4]

    ask_vwap = total_ask / vol_ask
    bid_vwap = total_bid / vol_bid

    mid_vwap = (ask_vwap + bid_vwap) / 2
    mid_price = (
        abs(df["ask_1"]) * df["ask_1_amt"] + abs(df["bid_1"]) * df["bid_1_amt"]
    ) / (df["bid_1_amt"] + df["ask_1_amt"])

    df["mid_vwap"] = mid_vwap
    df["mid_price"] = mid_price

    return df


# for candle
class Preprocess:
    def __init__(self):
        self._conn, self._cur = helper.get_connection()

    def get_dbs(self):
        q = """SHOW DATABASES"""
        self._cur.execute(q)
        res = self._cur.fetchall()

        return [r[0] for r in res]

    def get_table_names(self):
        q = """SHOW TABLES"""
        self._cur.execute(q)
        tables = self._cur.fetchall()

        return [t[0] for t in tables]

    def read_table_by_info(self, date, table_type, code):
        q = f"""SELECT * FROM {date}_{table_type}_{code}"""
        self._cur.execute(q)
        rows = self._cur.fetchall()

        return rows

    def read_table_by_name(self, table_name):
        q = f"""SELECT * FROM {table_name}"""
        self._cur.execute(q)
        rows = self._cur.fetchall()

        return rows

    def extract_combinations(self, tables):
        combi = []
        for col in zip(*[table.split("_") for table in tables]):
            combi.append(set(col))

        return combi

    def get_order_tables_names(self):
        tables = self.get_table_names()

        return [t for t in tables if "order" in t]

    def get_trans_tables_names(self):
        tables = self.get_table_names()

        return [t for t in tables if "trans" in t]

    def get_table_df(self, table_name):
        rows = self.read_table_by_name(table_name)
        df = pd.DataFrame(rows)
        if "order" in table_name:
            try:
                if len(df.columns) == len(helper.order_col_names):
                    df.columns = helper.order_col_names
                else:
                    df.columns = helper.order_col_names_2
                df.drop(columns="id", inplace=True)
            except:
                pass

        elif "trans" in table_name:
            try:
                df.columns = helper.trans_col_names
                df.drop(columns="id", inplace=True)
            except:
                pass

        return df

    def get_datas(self, opt):
        trs = self.get_trans_tables_names()
        ods = self.get_order_tables_names()

        for tr in trs:
            table = self.get_table_df(tr)
            # print(table.head())

        for od in ods:
            table = self.get_table_df(od)
            # print(table.head())
