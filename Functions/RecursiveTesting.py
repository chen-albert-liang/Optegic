import pandas as pd
from Functions.Backtest import OptionBackTesting


class GetRecursiveBackTesting(OptionBackTesting):

    def select_testing_period(self):
        return calendar

    def select_entrance_vix_criteria(self):
        return vix_criteria

    def select_entrance_underlying_criteria(self):
        # Gap up, gap down, etc
        return enter_underlying

    def select_exit_underlying_criteria(self):
        # Gap up, gap down, etc
        return exit_underlying

    def select_entrance_iv_criteria(self):
        return iv_criteria

    def select_entrance_time(self):
        return enter_time

    def select_exit_time(self):
        return exit_time

    def select_entrance_delta(self):
        return enter_delta

    def select_exit_delta(self):
        return exit_delta

    def calc_date_to_expiry(self):
        dte_seeker = pd.merge(self.trading_days, self.expiry, on='Year-Month', how='left')
        dte_seeker['DTE'] = (pd.to_datetime(dte_seeker['Expiration Date']) - pd.to_datetime(dte_seeker['Date'])).dt.days
        dte_seeker.dropna(inplace=True)

    def