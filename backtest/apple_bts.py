import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np

aapl_raw_data = pd.read_csv('C:/Users/chena/Desktop/Trading/StrategicOptions/backtest/aapl_backtest.csv')

aapl_put_data = aapl_raw_data[['ticker', 'stkpx', 'expirdate', 'yte', 'strike', 'transact_date', 'transact_pbidpx',
                               'transact_pvalue', 'transact_paskpx',  'pbidpx', 'pvalue', 'paskpx', 'delta', 'gamma',
                               'theta', 'vega', 'rho', 'phi', 'trade_date']]

aapl_put_data['PeriodPnL'] = aapl_put_data['transact_pvalue'] - aapl_put_data['pvalue']

figure(figsize=(10,6), dpi=80)
aapl_put_data['Date'] = pd.to_datetime(aapl_put_data['trade_date'])

ax = plt.gca()
ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y'))
plt.plot(aapl_put_data['Date'], aapl_put_data['PeriodPnL'])
plt.axhline(y=0, color='r', linestyle=':')

aapl_put_data['Loss100'] = (aapl_put_data['PeriodPnL'] + 1.0*aapl_put_data['transact_pvalue'])<=0

aapl_put_data['LossDate'] = aapl_put_data['Loss100']*aapl_put_data['trade_date']


stop_loss_dates_finder = aapl_put_data[['expirdate','Loss100','LossDate']]
stop_loss_dates_finder = stop_loss_dates_finder[stop_loss_dates_finder['Loss100']==True]
stop_loss_dates = stop_loss_dates_finder.groupby('expirdate').agg({'LossDate':np.min}).reset_index(drop=False)
stop_loss_dates = stop_loss_dates.rename(columns={'LossDate':'MinLossDate'})
stop_loss_dates

appl_portfolio = pd.merge(aapl_put_data, stop_loss_dates, on=['expirdate'], how='left')
appl_portfolio['stopLoss'] = appl_portfolio['Date']>=appl_portfolio['MinLossDate']
portfolio = appl_portfolio[appl_portfolio['stopLoss']==False]

portfolio_period_end = portfolio.groupby(['expirdate'])['PeriodPnL'].last().reset_index(drop=False)
portfolio_period_end['TotalPnL'] = portfolio_period_end['PeriodPnL'].cumsum()

# portfolio_period_end.to_csv('C:/Users/chena/Desktop/Trading/StrategicOptions/backtest/aaapl_backtest_result.csv')
aapl_put_data['Date'] = pd.to_datetime(aapl_put_data['trade_date'])

figure(figsize=(10,6), dpi=80)
ax2 = plt.gca()
ax2.xaxis.set_major_locator(matplotlib.dates.YearLocator())
ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y'))

plt.plot(pd.to_datetime(portfolio_period_end['expirdate']),portfolio_period_end['TotalPnL']*100)