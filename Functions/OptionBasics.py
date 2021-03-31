from DataQuery.Query import get_underlying_price, get_treasury_rate, get_volatility, get_expiration_dates
from Functions import OptionPricingModels as OP
import pandas as pd
import numpy as np
import logging
from scipy.stats import norm
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from mpl_axes_aligner import align


class OptionPricing(object):
    """
    Instantiate option object for data query.

    Inputs:
        ticker
        start_date
        end_date
        option_type
    Outputs:

    """
    LOOK_BACK_WINDOW = 252

    def __init__(self, ticker, start_date, end_date, option_type='C', period_type='year', frequency_type='daily',
                 frequency='1', dividend=0.0):
        """
        Parameters
        ----------
        ticker
        expiration_date
        """
        # Specified by user
        self.ticker = ticker
        self.start_date = start_date.date()
        self.end_date = end_date.date()
        self.option_type = option_type

        # Default parameters for data query
        self.period_type = period_type
        self.frequency_type = frequency_type
        self.frequency = frequency
        self.dividend = dividend or 0

        # Queried
        self.vix = pd.DataFrame()
        self.expiration_dates = pd.DataFrame()

        # Calculated
        self.trading_days = pd.DataFrame()

    def initialize_variables(self):
        self._get_expiration_dates()

    def _get_expiration_dates(self):
        self.expiration_dates = get_expiration_dates(self.start_date, self.end_date)

    def _get_risk_free_rate(self):
        """
        Get 3-month treasury bill rate from Quandl
        for the given period

        Returns
        -------
        Risk free rate in Dataframe
        """
        logging.info("Fetching Risk Free Rate")
        self.risk_free_rate_unpad = get_treasury_rate(self.start_date, self.end_date)
        self.risk_free_rate = self.trading_days.join(self.risk_free_rate_unpad, how='left')
        self.risk_free_rate['rf'] = self.risk_free_rate['rf'].interpolate()

    def _get_underlying_price(self):
        """
        Get underlying prices for given sticker
        Get extra 2 years of data for HV and HV rank calculation.  Currently not included.

        Returns
        -------
        Underlying price, including open, close, high, and low of the day
        """
        underlying_price_raw = get_underlying_price(self.ticker, self.start_date, self.end_date,
                                                    self.period_type, self.frequency_type, self.frequency)
        self.underlying_price_truncated_ = self.get_trimmed_history(underlying_price_raw, self.start_date,
                                                                    self.end_date)

    def _get_vix(self):
        """
        Get underlying prices for given sticker

        potentially get 1 additional year to calculate IV rank
        Returns
        -------
        Underlying price, including open, close, high, and low of the day
        """
        vix_raw = get_underlying_price('VIX', self.start_date, self.end_date, self.period_type, self.frequency_type,
                                       self.frequency)
        self.vix = self.get_trimmed_history(vix_raw, self.start_date, self.end_date)

    def _get_volatility(self):
        """
        Use quandl API to fetch IV, HV data at multiple periods (10, 20, etc...)

        Returns
        -------

        """
        implied_volatility_raw, historic_volatility_queried_raw = get_volatility([], [], [], self.option_type)
        self.implied_volatility = self.get_trimmed_history(implied_volatility_raw, self.start_date, self.end_date)

    @staticmethod
    def get_trimmed_history(data, start_date, end_date):
        """
        Truncate the underlying price history to the given time window (remove extra history for volatility calcs)

        -------
        """
        data_truncated = data.truncate(start_date, end_date)
        return data_truncated

    def _get_trading_days(self):
        """
        Get eligible trading days during the specified time window

        Returns
        -------

        """
        self.trading_days = pd.DataFrame(self.underlying_price_truncated_['datetime'])
        self.trading_days['Date'] = pd.to_datetime(
            self.trading_days['datetime'])  # Matching format with risk free rate dataframe

        self.trading_days.drop(columns='datetime', inplace=True)
        # self.trading_days.set_index('Date', inplace=True)


class OptionPayOffs(OptionPricing):
    """
    Instantiate option object
    """
    def __init__(self,  ticker_, strike_, start_date_, end_date_, option_type_, action_):
        super(OptionPayOffs, self).__init__(ticker_, start_date_, end_date_, option_type_)

        self.strike = strike_
        self.start_date = start_date_.date()
        self.end_date = end_date_.date()
        self.expiry = end_date_.date()  # For payoff analysis end_date_ acts as expiration day for time value calcs
        self.toe = (self.expiry - self.start_date).days
        self.action = action_
        self.payoff_expiration = pd.DataFrame()
        self.payoff_current = pd.DataFrame()
        self.option_price = None
        self.breakeven = None
        self.probability_of_profit = None
        self.spot_plot = np.arange(self.strike * 0.75, self.strike * 1.25)

    def initialize_payoff_variables(self):
        self._get_underlying_price()
        self._get_volatility()
        self._set_current_option_price()
        self._set_payoff_current()
        self._set_payoff_expiry()
        self._set_breakeven()
        self._set_probability_of_profit()

    def _set_current_option_price(self):
        self.option_price = OP.european_vanilla_option(self.underlying_price_truncated_['close'][0], self.strike,
                                                       self.toe, self.implied_volatility.values[0, 0], 0.01,
                                                       self.option_type)

    def _set_payoff_expiry(self):
        """
        Calculate payoff at expiration

        Returns
        -------

        """
        if self.option_type == 'C' and self.action == 'L':
            self.payoff_expiration = np.maximum(self.spot_plot - self.strike, 0) - self.option_price

        if self.option_type == 'C' and self.action == 'S':
            self.payoff_expiration = np.minimum(self.strike - self.spot_plot, 0) + self.option_price

        if self.option_type == 'P' and self.action == 'L':
            self.payoff_expiration = np.maximum(self.strike - self.spot_plot, 0) - self.option_price

        if self.option_type == 'P' and self.action == 'S':
            self.payoff_expiration = np.minimum(self.spot_plot - self.strike, 0) + self.option_price

    def _set_payoff_current(self):
        """
        Calculate payoff as of right now

        Returns
        -------

        """
        payoff_current_incl_cost = OP.european_vanilla_option(self.spot_plot, self.strike, self.toe,
                                                              self.implied_volatility.values[0, 0], 0.01,
                                                              self.option_type)
        if self.action == 'L':
            self.payoff_current = payoff_current_incl_cost - self.option_price

        if self.action == 'S':
            self.payoff_current = self.option_price - payoff_current_incl_cost

    def _set_probability_of_profit(self):
        """
        Calculate probability of profit
        !!！  This needs more work because the payoff calculated below did not consider the upfront debit/credit

        Returns
        -------
        Probability of profit
        """
        if self.option_type == 'C' and self.action == 'L':
            probability_of_below_strike = norm.cdf(
                np.log(self.strike / self.underlying_price_truncated_.values[0, 0]) / self.implied_volatility.values[0, 0])
            self.probability_of_profit = 1-probability_of_below_strike

        if self.option_type == 'C' and self.action == 'S':
            probability_of_below_strike = norm.cdf(
                np.log(self.strike / self.underlying_price_truncated_.values[0, 0]) / self.implied_volatility.values[0, 0])
            self.probability_of_profit = probability_of_below_strike

        if self.option_type == 'P' and self.action == 'L':
            probability_of_below_strike = norm.cdf(
                np.log(self.strike / self.underlying_price_truncated_.values[0, 0]) / self.implied_volatility.values[0, 0])
            self.probability_of_profit = probability_of_below_strike

        if self.option_type == 'P' and self.action == 'S':
            probability_of_below_strike = norm.cdf(
                np.log(self.strike / self.underlying_price_truncated_.values[0, 0]) / self.implied_volatility.values[0, 0])
            self.probability_of_profit = 1 - probability_of_below_strike

    def _set_breakeven(self):
        """
        Calculate break even points

        Returns
        -------
        Breakeven prices
        """
        if self.option_type == 'C' and self.action == 'L':
            self.breakeven = self.strike + self.option_price

        if self.option_type == 'C' and self.action == 'S':
            self.breakeven = self.strike + self.option_price

        if self.option_type == 'P' and self.action == 'L':
            self.breakeven = self.strike - self.option_price

        if self.option_type == 'P' and self.action == 'S':
            self.breakeven = self.strike - self.option_price

    def plot_payoff(self):
        """
        Payoff plotting

        Returns
        -------

        """
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.spot_plot,  self.payoff_expiration, 'b', label='Expiration Day')
        ax1.plot(self.spot_plot, self.payoff_current, 'r', label='Entry Day')
        ax1.axhline(0, color='k', linestyle=':')

        axis_ymin, axis_ymax = ax1.get_ylim()
        yaxis_breakeven = -axis_ymin/(axis_ymax-axis_ymin)
        ax1.axvline(self.breakeven, ymin=0, ymax=yaxis_breakeven, color='k', linestyle=':')
        ax1.legend(loc='best')
        ax1.set_xlabel("Spot Price ($)")
        ax1.set_ylabel("Payoff ($)")
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        plt.title('Probability of Profit = ' + "{:.1%}".format(self.probability_of_profit))


class OptionBackTesting(OptionPricing):
    """
    Instantiate option object
    """
    LOOK_BACK_WINDOW = 252

    def __init__(self,  ticker_, strike_, start_date_, end_date_, option_type_, action_, expiry_):
        super(OptionBackTesting, self).__init__(ticker_, start_date_, end_date_, option_type_)

        self.strike = strike_
        self.start_date = start_date_.date()
        self.end_date = end_date_.date()
        self.expiry = expiry_.date() if expiry_ else end_date_.date()
        self.toe = (self.expiry - self.start_date).days
        self.option_type = option_type_
        self.action = action_

        # Instantiate and will be calculated
        self.strategy_summary = pd.DataFrame()
        self.option_price = pd.DataFrame()
        self.option_holding_period_return = pd.DataFrame()
        self.underlying_holding_period_return = pd.DataFrame()

    def initialize_backtesting_variables(self):
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
        self.time_to_expiration = self.underlying_price_truncated_.reset_index(drop=False)[['Date']]
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
        self.implied_volatility_truncated_ = self.get_trimmed_history(self.implied_volatility, self.start_date,
                                                                      self.end_date)
        self._get_trading_days()
        self._set_time_to_expiration()
        # self._set_risk_free_rate()
        self.option_price = OP.european_vanilla_option(self.underlying_price_truncated_['close'], self.strike,
                                                       self.time_to_expiration['Time to Expire'],
                                                       self.implied_volatility_truncated_['IV'], 0.01, self.option_type)
        # self.risk_free_rate['rf'], option=self.option_type)

    def _set_option_holding_period_return(self):
        """
        Calculate holding period return on daily basis

        Returns
        -------

        """
        if self.action == 'L':
            self.option_holding_period_return = self.option_price / self.option_price[0] - 1

        if self.action == 'S':
            self.option_holding_period_return = 1 - self.option_price / self.option_price[0]

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
        cost = 100 * self.option_price[0]
        residual = 100 * self.option_price[-1]
        if self.action == 'L':
            pnl = residual - cost
            roc = residual / cost - 1

        if self.action == 'S':
            pnl = cost - residual
            roc = 1 - residual / cost

        pnl_per_day = pnl / duration
        win = roc > 0
        self.strategy_summary = pd.DataFrame([[self.start_date, "${:.2f}".format(cost), self.end_date, duration,
                                               "${:.2f}".format(residual), "${:.2f}".format(pnl),
                                               "${:.2f}".format(pnl_per_day), "{:.1%}".format(roc), win]],
                                             columns=['Entry Date', 'Cost Basis', 'Exit Date', 'Holding Period (Days)',
                                                      'Residual Value', 'P&L', 'PnL/Day', 'ROC', 'Win'])


    def plot_price_history(self):
        """
        Two scales for each instrument

        Returns
        -------

        """
        fig, ax1 = plt.subplots(2, figsize=(12, 6))
        ax1[0].plot(self.trading_days, self.option_price, 'r-^', label='Option')
        ax2 = ax1[0].twinx()
        ax2.plot(self.trading_days, self.underlying_price_truncated_['close'], 'b-o', label='Underlying')
        ax1[0].legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax1[0].spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1[0].set_xlabel("Date")
        ax1[0].set_ylabel("Option Price")
        ax2.set_ylabel("Underlying Price")
        ax1[1].plot(self.trading_days, self.implied_volatility_truncated_, 'b-', label='Implied Volatility')
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
        ax1.plot(self.trading_days,  self.option_holding_period_return * 100, 'r-^', label='Option')
        ax1.axhline(0, color='k', linestyle=':')
        ax2 = ax1.twinx()
        ax2.plot(self.trading_days, self.underlying_holding_period_return * 100, 'b-o', label='Underlying')
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