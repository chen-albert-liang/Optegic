from DataQuery.Query import get_expiration_dates
from Functions.OptionBasics import OptionBasics as OB
from Functions.visualization import option_visualization as OV
import pandas as pd


class OptionBackTesting(OB):

    def __init__(self, ticker, strike, expiry_, start_date_, end_date_, option_type, action):
        super(OptionBackTesting, self).__init__(ticker, strike, expiry_, start_date_, end_date_, option_type, action)
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

    def get_VIX_price(self):
        vix = self.get_VIX_price()
        return vix

    def generate_data(self):
        """

        """
        underlying_price_ = self.underlying_price_truncated_  # Truncated for extra data to calc volatility
        underlying_price_.reset_index(drop=False, inplace=True)
        underlying_price_['Date'] = pd.to_datetime(underlying_price_['Date']).dt.date
        underlying_price_.set_index('Date', inplace=True)

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
                 strike_, expiry_, entry_date_, exit_date, lb_, ub_, option_type_, action_):

        super(BackTestingVisualization, self).__init__(trading_days_, option_price_, underlying_price_, option_return_,
                                                       underlying_return_, iv_, strike_, expiry_, entry_date_, exit_date,
                                                       lb_, ub_, option_type_, action_)

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
