import pandas as pd
from DataQuery.Query import get_expiration_dates
from Functions.OptionBasics import OptionPricing, OptionPayOffs, OptionBackTesting
from Functions.visualization import PayOffVisualization, PnLVisualization


class GetExpiration(OptionPricing):
    def __init__(self, ticker_, start_date_, end_date_, option_type_):
        super(GetExpiration, self).__init__(ticker_, start_date_, end_date_, option_type_)
        self.initialize_variables()


class GetPayOff(OptionPayOffs):
    def __init__(self, ticker_, strike_, start_date_, expiry_, option_type_, action_):
        super(GetPayOff, self).__init__(ticker_, strike_, start_date_, expiry_, option_type_, action_)
        self.initialize_option_variables()







class PayOffVisualization(PayOffVisualization):

    def __init__(self, exp_payoff_, cur_payoff_, breakeven_, probability_of_profit_, spot_prices_):
        super(PayOffVisualization, self).__init__(exp_payoff_, cur_payoff_, breakeven_, probability_of_profit_,
                                                  spot_prices_)


class PnLVisualization(PnLVisualization):
    def __init__(self, trading_days_, option_price_, underlying_price_, option_return_, underlying_return_,
                 implied_volatility_):
        super(PnLVisualization, self).__init__(trading_days_, option_price_, underlying_price_, option_return_,
                                               underlying_return_, implied_volatility_)


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

