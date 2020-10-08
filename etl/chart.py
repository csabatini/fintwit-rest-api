import robin_stocks
import os
import json
import math
from datetime import datetime

def login():
    login = robin_stocks.login(os.environ['RH_USER'], os.environ['RH_PW'])
    # deposits = sum(float(x['amount']) for x in robin_stocks.get_bank_transfers()
        # if (x['direction'] == 'deposit') and (x['state'] == 'completed'))
    data = robin_stocks.stocks.get_stock_historicals("GAN", span='week', bounds='regular')
    summary = {}
    summary['first'] = data[0]['close_price']
    summary['last'] = data[-1]['close_price']
    summary['low'] = (-1, math.inf)
    summary['high'] = (-1, 0.0)

    for i, kv in enumerate(data):
        begins_at = kv['begins_at']
        low = float(kv['low_price'])
        high = float(kv['high_price'])
        if low < summary['low'][1]:
            summary['low'] = (i, low)
        if high > summary['high'][1]:
            summary['high'] = (i, high)
        date = datetime.strptime(begins_at, '%Y-%m-%dT%H:%M:%SZ')
        fmt_date = '{}/{}'.format(date.month, date.day)
        print(fmt_date)
    # print(json.dumps(summary))
    # print(data)

if __name__ == '__main__':
    login()