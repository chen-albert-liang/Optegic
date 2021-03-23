import pandas as pd
import numpy as np
import datetime
# from OptionPricingModels import european_vanilla_option

from OptionBasics import OptionBasics as OB

class EuropeanOptionPL(OB):
    """
    Get data, set up option strategy and calculate P&L
    1. S&P long call:
        a. On Jan 4. 2021 buy S&P
            i. Different expiry: Feb., May., Sept., Jan.22
            ii. Different strikes:  ITM, ATM, OTM

        b. Plot value on the daily basis
        c. Daily return, drawdown
        d. Cumulative return vs. buy&hold


    2. S&P short put:
        a. On Jan 4. 2021 buy S&P
            i. Different expiry: Feb., May., Sept., Jan.22
            ii. Different strikes:  ITM, ATM, OTM

        b. Plot value on the daily basis
        c. Daily return, drawdown
        d. Cumulative return vs. buy&hold

    """

    def __init__(self,ticker, strike, start_date, end_date):
        super(EuropeanOptionPL, self).__init__(ticker, strike, start_date, end_date)
        self.initialize_variables()

    def generate_data(self):
        # rf = self.risk_free_rate
        hv = self.hist_vol
        hvr= self.HV_rank
        exp_date = self.expiration_dates
        return hv, hvr, exp_date

    def choose_option_strike(self):

    def choose_option_expiry(self):
        

# if __name__ == '__main__':
data = EuropeanOptionPL('TSLA', 100, datetime.datetime(2020, 8, 31), datetime.datetime(2021, 3, 15))

hv, hvr, exp_date = data.generate_data()

