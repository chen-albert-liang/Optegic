import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from DataQuery.Query import get_underlying_price


def sharpe_ratio_cal(daily_price):
    daily_return = daily_price.pct_change(1)
    sharpe_ratio = daily_return.mean()/daily_return.std()
    return sharpe_ratio


raw_data = pd.read_csv('C:/Users/chena/Desktop/Trading/StrategicOptions/backtest/nkp backtest result.csv')
raw_data = raw_data.sort_values(['ticker','expirdate'])
tickers_all = raw_data['ticker'].unique().tolist()
removal = ['SQQQ', 'UVXY', 'VXX']

for ele in removal:
    tickers_all.remove(ele)

tickers_all = ['SPY']

# pp = PdfPages("C:/Users/chena/Desktop/Trading/StrategicOptions/backtest/performance-naked put selling.pdf")
# matplotlib.use('Agg')


for tik in tickers_all:
    ticker_data = raw_data[raw_data['ticker']==tik]
    hist = get_underlying_price(tik, ticker_data.trade_date.values[0], ticker_data.trade_date.values[-1]).reset_index(drop=False)
    # hist['pnl'] = (hist.close - hist.close.values[0])*100
    # stock_sharpe = sharpe_ratio_cal(hist['close'])
    # option_sharpe = sharpe_ratio_cal(ticker_data['pvalue'])
    # # ax = plt.gca()
    # fig, ax = plt.subplots(figsize=(15,8))
    # ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
    # ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y'))
    # ax.yaxis.set_major_formatter('${x:1.0f}')
    #
    # ax.spines['right'].set_visible(False)
    # ax.spines['top'].set_visible(False)
    #
    # ax.plot(pd.to_datetime(hist['Date']), hist['pnl'], 'b')
    # ax.plot(pd.to_datetime(ticker_data['expirdate']), ticker_data['cumulative_pnl'] * 100, 'orange', marker='o', markersize=5)
    #
    # plt.legend(['Stock Sharpe Ratio = ' + str(round(stock_sharpe,2)), 'Option Sharpe Ratio = ' + str(round(option_sharpe, 2))], loc='upper left', fontsize=15)
    # plt.title(tik+' pnl, number of option trades = ' + str(len(ticker_data)), fontsize=20)
    # pp.savefig()

# pp.close()

spy_hist = hist
spy_hist['close2close'] = spy_hist['close'].pct_change(1)*100

ax = spy_hist['close2close'].plot.hist(bins=500, alpha=1)

spy_hist['close2close_2d'] = spy_hist['close'].pct_change(2)*100
ax2 = spy_hist['close2close_2d'].plot.hist(bins=500, alpha=1)

spy_hist['close2close'].mean(), spy_hist['close2close'].std()
spy_hist['close2close_2d'].mean(), spy_hist['close2close_2d'].std()