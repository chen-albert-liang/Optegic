import pandas as pd
from Functions.Backtest import OptionBackTesting


class GetRecursiveBackTesting(OptionBackTesting):

    def set_testing_period(self):
        return calendar

    def set_entrance_vix_criteria(self):
        return vix_criteria

    def set_entrance_underlying_price_criteria(self):
        # Gap up, gap down, etc
        return exit_underlying

    def set_entrance_iv_criteria(self):
        return iv_criteria

    def set_entrance_dte(self):
        return enter_time

    def set_exit_dte(self):
        return exit_time

    def set_entrance_delta(self):
        return enter_delta

    def set_exit_delta(self):
        return exit_delta

    def set_limit_order(self):
        max_profit = []
        return max_profit

    def set_stop_order(self):
        max_loss = []
        return max_loss

    def _buying_power_requirement(self):
        bpr = []
        return bpr

    def calc_date_to_expiry(self):
        dte_seeker = pd.merge(self.trading_days, self.expiry, on='Year-Month', how='left')
        dte_seeker['DTE'] = (pd.to_datetime(dte_seeker['Expiration Date']) - pd.to_datetime(dte_seeker['Date'])).dt.days
        dte_seeker.dropna(inplace=True)

