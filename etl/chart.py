import robin_stocks
import os
import json
import math
from datetime import datetime

def round_num(number):
    return round(number * 2) / 2

def login():
    login = robin_stocks.login(os.environ['RH_USER'], os.environ['RH_PW'])
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
        close_price = round(float(kv['close_price']), 2)
        # high = round(float(kv['high_price']), 2)
        if close_price < summary['low'][1]:
            summary['low'] = (i, close_price)
        if close_price > summary['high'][1]:
            summary['high'] = (i, close_price)

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
    chl[low[0]] = 'low: {}'.format(round(low[1], 2))
    pct_chg =  round(round(high[1]/summary['first']*100, 2)-100.0, 2)
    chl[high[0]] = 'high: {}\\n{}%'.format(high[1], pct_chg)
    print(low)
    print(high)
    if low[0] > 4 and high[0] > 4:
        chl[2] = str(summary['first'])
    if low[0] < len(chl)-4 and high[0] < len(chl)-4:
        chl[-1] = str(summary['last'])

    # axis bounds
    lower_bound = math.floor(summary['low'][1])
    upper_bound = math.ceil(summary['high'][1])

    chart_url = "https://image-charts.com/chart?cht=lc&chxt=x,y&chxl=0:|{}&chd=a:{}&chl={}&chco=76A4FB&chls=2.5&chs=720x240&chxr=1,{},{}&chlps=offset,5|align,left|clip,true".\
        format('|'.join(xl), ','.join(chd), '|'.join(chl), lower_bound, upper_bound)
    print(chart_url)

if __name__ == '__main__':
    login()