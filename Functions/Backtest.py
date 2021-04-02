import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from mpl_axes_aligner import align
from Functions.OptionBasics import OptionPricing
import Functions.OptionPricingModels as OP


class OptionBackTesting(OptionPricing):
    """
    Instantiate option object
    """
    LOOK_BACK_WINDOW = 252

    def __init__(self,  ticker_, strike_, expiry_, start_date_, end_date_, option_type_, action_):
        super(OptionBackTesting, self).__init__(ticker_, start_date_, end_date_, option_type_)

        self.strike = strike_
        self.expiry = expiry_.date() if expiry_ else end_date_.date()
        self.toe = (self.expiry - self.start_date).days
        self.action = action_
        self.implied_volatility_raw = pd.DataFrame()
        self.implied_volatility_truncated_ = pd.DataFrame()

        # Instantiate and will be calculated
        self.strategy_summary = pd.DataFrame()
        self.strat_sum_for_stats = []
        self.option_price = pd.DataFrame()
        self.option_holding_period_return = pd.DataFrame()
        self.underlying_holding_period_return = pd.DataFrame()
        self.trading_days = pd.DataFrame()

    def initialize_backtesting_variables(self):
        self._get_trading_days()
        self._get_underlying_price()
        self._get_volatility()
        self._set_option_price()
        self._set_option_holding_period_return()
        self._set_underlying_holding_period_return()
        self._set_strategy_summary()

    def _set_time_to_expiration(self):
        """
        Calculate time to expire for each day

        Returns
        -------

        """
        self.time_to_expiration = self.trading_days
        self.time_to_expiration['Time to Expire'] = (self.expiry - self.time_to_expiration['Date']).dt.days
        self.time_to_expiration.set_index('Date', inplace=True)

    def _set_option_price(self):
        """
        Calculate option price history given changes in spot, volatility, and date

        Returns
        -------

        """
        # self.underlying_price_truncated_ = self.get_trimmed_history(self._underlying_price, self.start_date,
        #                                                             self.end_date)
        self._set_time_to_expiration()
        # self._set_risk_free_rate()
        i = 0
        for _ in self.action:
            leg_price = OP.european_vanilla_option(self.underlying_price_truncated_['close'], self.strike[i],
                                                   self.toe, self.implied_volatility_truncated_.values[:, i], 0.01,
                                                   self.option_type[i])            
            if self.action[i]=='L':
                leg_value = leg_price
            else:
                leg_value = -1 * leg_price

            leg_value_df = pd.DataFrame(data=leg_value).rename(columns={'close':'Option Price Leg-'+str(i+1)})

            if self.option_price.empty:
                self.option_price = leg_value_df
            else:
                self.option_price = self.option_price.join(leg_value_df)
            i += 1

        self.option_price['Strategy Value'] = self.option_price.sum(axis=1)

    def _set_option_holding_period_return(self):
        """
        Calculate holding period return on daily basis

        Returns
        -------

        """

        if self.option_price['Strategy Value'][0] >= 0:
            option_holding_period_return = self.option_price['Strategy Value'][:] / self.option_price['Strategy Value'][0] - 1
        else:
            option_holding_period_return = 1 - self.option_price['Strategy Value'][:] / self.option_price['Strategy Value'][0]

        self.option_holding_period_return = pd.DataFrame(data=option_holding_period_return).rename(
            columns={'Strategy Value': 'Strategy Return'})

    def _set_underlying_holding_period_return(self):
        """
        Calculate holding period return on daily basis

        Returns
        -------

        """
        self.underlying_holding_period_return['close'] = self.underlying_price_truncated_['close'] / \
                                                         self.underlying_price_truncated_['close'][0] - 1

    def _set_strategy_summary(self):
        """
        Strategy synthesis

        Returns
        -------

        """
        duration = (self.end_date - self.start_date).days
        cost = 100 * self.option_price['Strategy Value'][0]
        residual = 100 * self.option_price['Strategy Value'][-1]
        # if self.option_price['Strategy Value'][0] >= 0:
        pnl = residual - cost
        roc = pnl / abs(cost)
        # else:
        #     pnl = cost - residual
        #     roc = 1 - residual / cost

        pnl_per_day = pnl / duration
        win = pnl > 0
        self.strategy_summary = pd.DataFrame([[self.start_date, "${:.2f}".format(cost), self.end_date, duration,
                                               "${:.2f}".format(residual), "${:.2f}".format(pnl),
                                               "${:.2f}".format(pnl_per_day), "{:.1%}".format(roc), win]], columns=
                                               ['Entry Date', 'Cost Basis', 'Exit Date', 'Holding Period (Days)',
                                                'Residual Value', 'P&L', 'PnL/Day', 'ROC', 'Win'])

        self.strat_sum_for_stats = [self.start_date, cost, self.end_date, duration, residual, pnl, pnl_per_day, roc, win]

    def plot_price_history(self):
        """
        Two scales for each instrument

        Returns
        -------

        """
        fig, ax1 = plt.subplots(2, figsize=(12, 6))
        ax1[0].plot(self.trading_days.index, self.option_price['Strategy Value'], 'r-^', label='Option')
        ax2 = ax1[0].twinx()
        ax2.plot(self.trading_days.index, self.underlying_price_truncated_['close'], 'b-o', label='Underlying')
        ax1[0].legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax1[0].spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1[0].set_xlabel("Date")
        ax1[0].set_ylabel("Strategy Value")
        ax2.set_ylabel("Underlying Price")
        ax1[1].plot(self.trading_days.index, self.implied_volatility_truncated_, 'b-', label='Implied Volatility')
        ax1[1].set_xlabel("Date")
        ax1[1].set_ylabel("Implied Volatility (Call)")
        ax1[1].legend(loc="upper right")
        ax1[1].spines['top'].set_visible(False)
        ax1[1].spines['right'].set_visible(False)
        plt.title('Price and IV Move')

    def plot_option_pnl(self):
        """
        Plot holding period return

        Returns
        -------

        """
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.trading_days.index,  self.option_holding_period_return['Strategy Return'] * 100, 'r-^', label='Option')
        ax1.axhline(0, color='k', linestyle=':')
        ax2 = ax1.twinx()
        ax2.plot(self.trading_days.index, self.underlying_holding_period_return * 100, 'b-o', label='Underlying')
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax1.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Option P&L")
        ax2.set_ylabel("Underlying P&L")
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

        # Align y-axes
        org1 = 0.0  # Origin of first axis
        org2 = 0.0  # Origin of second axis
        pos = 0.5  # Position the two origins are aligned
        align.yaxes(ax1, org1, ax2, org2, pos)
        plt.tight_layout()
        plt.title('Holding Period Return')

# class StrategyPerformance(object):
#
#     def __init__(self, ticker, strike, expiry, start_date, end_date, option_type, action):
#         self.ticker = ticker
#         self.spot_plot = pd.DataFrame()
#         self.strike = strike
#         self.option_type = option_type
#         self.action = action
#
#         self.option_price = pd.DataFrame()
#         self.option_holding_period_return = pd.DataFrame()
#         self.breakeven = pd.DataFrame()
#         self.pop = []  # Probability of profit
#         self.payoff_current = pd.DataFrame()
#         self.payoff_expiry = pd.DataFrame()
#         self.strategy_summary = pd.DataFrame()
#
#         i = 0
#         for _ in action:
#             leg_performance = OptionPricing(self.ticker, strike[i], expiry[i], start_date, end_date, option_type[i],
#                                             action[i])   # Currently set all legs simultaneously, easily changable
#             self.option_price = self.option_price.join(leg_performance.option_price)
#             self.option_holding_period_return = self.option_holding_period_return.join(
#                 leg_performance.option_holding_period_return)
#             self.breakeven.append(leg_performance.breakeven)
#             self.pop.append(leg_performance.probability_of_profit)
#             self.payoff_current = self.payoff_current.join(leg_performance.payoff_current)
#             self.payoff_expiry = self.payoff_expiry.join(leg_performance.payoff_expiry)
#             self.strategy_summary = self.strategy_summary.append(leg_performance.strategy_summary)
#             i += 1
#
#         self.implied_volatility_truncated_ = leg_performance.implied_volatility_truncated_
#         self.underlying_price_truncated = leg_performance.underlying_price_truncated_
#         self.underlying_holding_period_return = leg_performance.underlying_holding_period_return


#### Temporarily not used
def _set_historical_volatility_old(self):
    """
    Calculate historic volatility using underlying price history
    Returns
    -------
    """
    self._get_underlying_price()
    self._underlying_price['log_return'] = np.log(
        self._underlying_price['close'] / self._underlying_price['close'].shift(1))
    d_std = self._underlying_price.rolling(252)['log_return'].std()
    std = d_std * 252 ** 0.5
    self.historic_volatility = pd.DataFrame(data={'Hist Vol':std})
    self.historic_volatility = self.historic_volatility.dropna().reset_index(drop=False)
    self.historic_volatility = self.historic_volatility.set_index("Date")

def _set_HV_rank(self):
    """
    Calculate HV rank using calculated historical volatility data
    Returns
    -------

    """
    pct_rank = lambda x: pd.Series(x).rank(pct=True).iloc[-1]
    self.HV_rank = pd.DataFrame(self.historic_volatility_.rolling(252)['Hist Vol'].apply(pct_rank))
    self.HV_rank = self.HV_rank.rename(columns={'Hist Vol':'HV Rank'}).dropna()

def _set_IV_rank(self):
    """
    Calculate IV rank using quandl example data
    Returns
    -------

    """
    pct_rank = lambda x: pd.Series(x).rank(pct=True).iloc[-1]
    self.IV_rank = pd.DataFrame(self.implied_volatility.rolling(252)['IV'].apply(pct_rank))
    self.IV_rank = self.IV_rank.rename(columns={'IV':'IV Rank'}).dropna()

    # def _set_IV_Lewis(self):
    # def _set_gaps(self):
    #     """
    #     Check gap up/down at opening
    #     Returns
    #     -------
    #
    #     """
    #     self._get_underlying_price()
    #     self.__underlying_price.set_index("Date", inplace=True)
    #     self.__underlying_price['gap up'] = (self.__underlying_price['open'] / self.__underlying_price['high'].shift(
    #         1)) > 1
    #     self.__underlying_price['gap down'] = (self.__underlying_price['open'] / self.__underlying_price['low'].shift(
    #         1)) < 1
    #
    #
    # def _set_underlying_cumulative_return(self):
    #     """
    #     Calculate cumulative return on daily basis
    #
    #     Returns
    #     -------
    #
    #     """
    #     self._set_underlying_pnl()
    #     self.underlying_cumulative_return = self.underlying_pnl.cumsum()

    # def _set_underlying_drawdown(self):
    #     """
    #     Underlying drawdown calc
    #
    #     Returns
    #     -------
    #
    #     """
    #     self._set_underlying_cumulative_return()
    #     _cum_max = self.underlying_cumulative_return.cummax()
    #     self.underlying_drawdown = self.underlying_cumulative_return - _cum_max