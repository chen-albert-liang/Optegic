from DataQuery.Query import get_expiration_dates
from OptionBasics import OptionBasics as OB
from visualization import option_visualization as OV
import pandas as pd


class OptionBackTesting(OB):

    def __init__(self, ticker, strike, expiry_, start_date_, end_date_, option_type):
        super(OptionBackTesting, self).__init__(ticker, strike, expiry_, start_date_, end_date_, option_type)
        if strike:
            self.initialize_variables()
        self.expiration_dates = pd.DataFrame()  # Monthlies, oversimplified, 3rd Friday of each month

    def set_expiration_calendar(self):
        """
        Identify the expration dates in the given duration
        Add VIX open/close !!!!!!!!!

        Returns
        -------

        Returns
        -------

        """
        expiration_dates = get_expiration_dates(self.start_date, self.end_date)
        return expiration_dates

    def generate_data(self):
        """

        """
        underlying_price_ = self.underlying_price_truncated_  # Truncated for extra data to calc volatility
        hv_ = self.historic_volatility_truncated_
        iv_ = self.implied_volatility_truncated_
        # hvr = self.HV_rank
        # exp_calendar = self.expiration_dates
        # rf_rate = self.risk_free_rate
        option_price_ = self.option_price
        option_return_ = self.option_holding_period_return
        underlying_return_ = self.underlying_holding_period_return
        trading_days_ = self.trading_days
        return option_price_, option_return_, underlying_price_, underlying_return_, trading_days_, iv_, hv_


class BackTestingVisualization(OV):
    def __init__(self, trading_days_, option_price_, underlying_price_, option_return_, underlying_return_, iv_,
                 strike_, expiry_, entry_date_, lb_, ub_, option_type_):

        super(BackTestingVisualization, self).__init__(trading_days_, option_price_, underlying_price_, option_return_,
                                                       underlying_return_, iv_, strike_, expiry_, entry_date_, lb_,
                                                       ub_, option_type_)

# start_date = datetime.datetime(2017, 1, 1)
# end_date =  datetime.datetime(2017, 6, 30)
#
# data = OptionBackTesting('MSFT', [], start_date, end_date, [], 'C')
# expiry = data.set_expiration_calendar()
#
# entry_date = datetime.datetime(2017, 3, 29)
# exit_date = datetime.datetime(2017, 5, 19)
#
# data = OptionBackTesting('MSFT', 40, entry_date, exit_date, [], 'C')
#
# option_price, option_return, underlying_price, underlying_return, trading_days, iv, hv = data.generate_data()
#
# viz = BackTestingVisualization(trading_days, option_price, underlying_price, option_return, underlying_return, iv)
# viz.plot_price_history()
# viz.plot_option_pnl()

#
# class OptionViz(OV):
#     def __init__(self, ticker, date, strike, spot, IV, daily_pnl, option_price):
#         super(OptionViz, self).__init__(ticker, date, strike, spot, IV, daily_pnl, option_price)
#
#     def

#
# start_date = datetime.datetime(2010, 1, 1)
# end_date =  datetime.datetime(2021, 3, 17)
#
#
# data = OptionBackTesting('MSFT', 100, start_date, end_date)
# P_hist, hv, hvr, exp_calendar, rf_rate = data.generate_data()
#
# P_hist_truncated = P_hist.truncate(start_date.date(), end_date.date())
# hv_truncated = hv.truncate(start_date.date(), end_date.date())
# hvr_truncated = hvr.truncate(start_date.date(), end_date.date())
# rf_truncated = rf_rate.truncate(start_date.date(), end_date.date())
# P_hist_truncated['return'] = P_hist_truncated['close'] / P_hist_truncated['close'].shift(1)-1
#
# int_data = P_hist_truncated.join(hv_truncated).join(hvr_truncated).join(rf_truncated)
#
# int_data.to_csv('MSFT int_data_2010_20210317.csv')
# exp_calendar.to_csv('Expiration Calendar(2010_20210317).csv')


# 
# exp_calendar = pd.read_csv('Expiration Calendar(2010_20210317).csv')
# exp_calendar['Expiration Date'] = pd.to_datetime(exp_calendar['Business Day']).dt.date
# exp_calendar = exp_calendar.drop(columns=['Unnamed: 0', 'Business Day'])
# 
# int_data = pd.read_csv('MSFT int_data_2010_20210317.csv').drop(columns=['datetime'])
# int_data['Date'] = pd.to_datetime(int_data['Date']).dt.date
# int_data.set_index('Date', inplace=True)
# int_data['rf'] = int_data['rf'].interpolate()
# 
# entry_date = datetime.datetime(2020, 6, 1) # Monday
# exp_date =  datetime.datetime(2020, 12, 18)
# 
# contract_period = int_data.truncate(entry_date.date(), exp_date.date())
# contract_period['expiration date'] = exp_date.date()
# contract_period = contract_period.reset_index(drop=False)
# contract_period['Time to Expire'] = (contract_period['expiration date'] - contract_period['Date']).dt.days
# 
# contract_period['Option Price'] = european_vanilla_option(contract_period['close'], 200, contract_period['Time to Expire'], contract_period['Hist Vol'], contract_period['rf'], option='C')
# contract_period['Option Return'] = contract_period['Option Price']/contract_period['Option Price'].shift(1)
# 

"""
    Get data, set up option strategy and calculate P&L
    S&P long call:
        a. On Jan 4. 2021 buy S&P
            i. Different expiry: Feb., May., Sept., Jan.22
            ii. Different strikes:  ITM, ATM, OTM

        b. Plot value on the daily basis
        c. Daily return, drawdown
        d. Cumulative return vs. buy&hold
    
    Exit criteria:
        a. 50% return, or
        b. 7 biz day prior to expiration 
    """
# 
# def naked_short_put_test():
#     return []
#     """
#     2. S&P short put:
#         a. On Jan 4. 2021 buy S&P
#             i. Different expiry: Feb., May., Sept., Jan.22
#             ii. Different strikes:  ITM, ATM, OTM
# 
#         b. Plot value on the daily basis
#         c. Daily return, drawdown
#         d. Cumulative return vs. buy&hold    
#     Returns
#     -------
# 
#     """"""
