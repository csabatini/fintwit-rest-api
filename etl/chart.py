import robin_stocks
import os

def login():
    login = robin_stocks.login(os.environ['RH_USER'], os.environ['RH_PW'])
    # deposits = sum(float(x['amount']) for x in robin_stocks.get_bank_transfers()
        # if (x['direction'] == 'deposit') and (x['state'] == 'completed'))
    data = robin_stocks.stocks.get_stock_historicals("GAN", span='week', bounds='regular')
    print(data)

if __name__ == '__main__':
    login()