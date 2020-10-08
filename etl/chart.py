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
    summary['first'] = round(float(data[0]['close_price']), 2)
    summary['last'] = round(float(data[-1]['close_price']), 2)
    summary['low'] = (-1, math.inf)
    summary['high'] = (-1, 0.0)
    summary['last_xl'] = None
    xl = []
    last_xl = None
    chd = []
    chl = []

    for i, kv in enumerate(data):
        begins_at = kv['begins_at']
        low = float(kv['low_price'])
        high = float(kv['high_price'])
        if low < summary['low'][1]:
            summary['low'] = (i, low)
        if high > summary['high'][1]:
            summary['high'] = (i, high)

        # axis label
        date = datetime.strptime(begins_at, '%Y-%m-%dT%H:%M:%SZ')
        fmt_date = '{}/{}'.format(date.month, date.day)
        xl.append(fmt_date if i == 0 or last_xl != fmt_date else '')
        last_xl = fmt_date
        # data points 
        chd.append(kv['close_price'])
        chl.append('')

    # data point labels 
    low = summary['low']
    high = summary['high']
    chl[low[0]] = str(round(low[1], 2))
    chl[high[0]] = str(round(high[1], 2))
    if low[0] > 4:
        chl[2] = str(summary['first'])
    chl[-1] = str(summary['last'])

    # axis bounds
    lower_bound = (math.floor(summary['low'][1] * 0.95))
    upper_bound = (math.floor(summary['high'][1] * 1.05))

    chart_url = "https://image-charts.com/chart?cht=lc&chxt=x,y&chxl=0:|{}&chd=a:{}&chl={}&chco=76A4FB&chls=2.5&chs=480x240&chxr=1,{},{}&chlps=offset,5|align,left".\
        format('|'.join(xl), ','.join(chd), '|'.join(chl), lower_bound, upper_bound)
    print(chart_url)

if __name__ == '__main__':
    login()