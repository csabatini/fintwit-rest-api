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
    summary['last_xl'] = None
    xl = []
    last_xl = None

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
        xl.append(fmt_date if i == 0 or last_xl != fmt_date else '')
        last_xl = fmt_date
    # print(json.dumps(summary))
    # print(data)
    print('|'.join(xl))

    chart_url = "https://image-charts.com/chart?cht=lc&chxt=x,y&chxl=0:|10/1||||||10/2||||||10/5||||||10/6||||||10/7||||&chd=a:16.330000,16.390000,16.170000,16.240000,16.135000,15.970000,16.190000,15.980000,16.070000,16.005000,16.125000,16.200000,18.650000,18.115000,18.390000,18.435000,18.410000,18.200000,18.150000,18.000000,18.150000,18.190000,17.980000,17.580000,17.730000,17.608400,17.650000,17.630000&chl=||16.33||||||||||18.65|||||||||||||||17.68&chco=76A4FB&chls=2.0&chs=480x240&chxr=1,15,20&chlps=offset,5|align,left"

if __name__ == '__main__':
    login()