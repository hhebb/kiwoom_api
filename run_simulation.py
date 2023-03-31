import preprocess
import helper
import trader

SIG_TRANS = 0
SIG_LOB = 1


def get_signal(trans, lob, strategy):
    """
    generate buy signals.
    this is unified interface.
    because strategies are diverse
    """

    signal, sig_type = strategy(trans, lob)
    return signal, sig_type


def sample_strategy(trans, lob):
    vpin = preprocess.get_trans_vpin(trans, max_capa=1000)
    signal = vpin[vpin["vpin"] > 0.3]["trans_idx"]
    sig_type = SIG_TRANS
    return signal, sig_type


def simulate(trans, lob, signal, sig_type):
    """
    only measure the results.
    """

    if sig_type == SIG_TRANS:
        orders = []

        for tr_idx, tr in enumerate(trans):
            if tr_idx in signal:
                in_price = abs(trans.iloc[tr_idx]["price"])
                order = trader.Order("", "", in_price, tr_idx, 1)
                orders.append(order)

            to_remove = []
            for o_id, o in enumerate(orders):
                result = o.trailing_stop(abs(trans.iloc[tr_idx]["price"]))
                if result == "stop":
                    # record_result(o)
                    print(abs(o.in_price), abs(o.out_price))
                    to_remove.append(o_id)

            orders = [order for order in orders if order not in to_remove]

    elif sig_type == SIG_LOB:
        pass

    return


if __name__ == "__main__":
    conn, cursor = helper.get_connection()
    pr = preprocess.Preprocess()
    trans_table_names = pr.get_trans_tables_names()
    lob_table_names = pr.get_order_tables_names()

    for name in trans_table_names:
        try:
            print(name)
            trans = pr.get_table_df(name)
            lob = pr.get_table_df(lob_table_names[30])

            signal, sig_type = get_signal(trans, lob, sample_strategy)
            simulate(trans, lob, signal, sig_type)
        except:
            pass
