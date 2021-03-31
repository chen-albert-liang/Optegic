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
        self.initialize_payoff_variables()


class GetBackTesting(OptionBackTesting):
    def __init__(self, ticker_, strike_, start_date_, end_date_, option_type_, action_, expiry_):
        super(GetBackTesting, self).__init__(ticker_, strike_, start_date_, end_date_, option_type_, action_, expiry_)
        self.initialize_backtesting_variables()

#
# class VizPayOff(PayOffVisualization):
#     def __init__(self, payoff_expiration_, payoff_current_, breakeven_, probability_of_profit_, spot_prices_):
#         super(VizPayOff, self).__init__(payoff_expiration_, payoff_current_, breakeven_, probability_of_profit_,
#                                         spot_prices_)
#         self.plot_payoff()

# class VizPnL(PnLVisualization):
#     def __init__(self, ticker_, strike_, start_date_, end_date_, option_type_, action_, expiry_):
#         super(VizPnL, self).__init__(ticker_, strike_, start_date_, end_date_, option_type_, action_, expiry_)


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

