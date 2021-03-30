from DataQuery.Query import get_underlying_price, get_treasury_rate, get_volatility
from Functions import OptionPricingModels as OP
import pandas as pd
import numpy as np
import logging


class OptionBasics(object):
    """
    Instantiate option object
    """
    LOOK_BACK_WINDOW = 252

    def __init__(self, ticker, strike, expiry, start_date, end_date, option_type, action, period_type='year',
                 frequency_type='daily', frequency='1', dividend=0.0):

        """

        Parameters
        ----------
        ticker
        expiration_date
        strike
        dividend
        """
        # Specified by user
        self.ticker = ticker
        self.strike = strike
        self.start_date = start_date
        self.end_date = end_date
        self.option_type = option_type
        self.action = action
        self.expiry = expiry.date() if expiry else end_date.date()

        # Underlying data query, default values
        self.period_type = period_type
        self.frequency_type = frequency_type
        self.frequency = frequency
        self.dividend = dividend or 0


        # Queried
        self._underlying_price = pd.DataFrame()
        self.underlying_price_truncated_ = pd.DataFrame()
        self.risk_free_rate = pd.DataFrame()
        self.implied_volatility = pd.DataFrame()

        # Calculated
        self.time_to_expiration = pd.DataFrame()
        self.historic_volatility = pd.DataFrame()
        self.historic_volatility_queried = pd.DataFrame()
        self.historic_volatility_truncated_ = pd.DataFrame()
        self.HV_rank = pd.DataFrame()
        self.implied_volatility_truncated_ = pd.DataFrame()
        self.IV_rank = pd.DataFrame()
        self.option_price = pd.DataFrame()
        self.option_holding_period_return = pd.DataFrame()
        self.underlying_holding_period_return = pd.DataFrame()
        self.trading_days = pd.DataFrame()

    def initialize_variables(self):
        # self._set_risk_free_rate()
        self._set_historical_volatility()
        self._set_HV_rank()
        self._get_volatility()
        self._set_IV_rank()
        self._set_option_price()
        self._set_option_holding_period_return()
        self._set_underlying_holding_period_return()
        self._get_trimmed_history()
        self._get_trading_days()
        self._set_time_to_expiration()

    def _get_underlying_price(self):
        """
        Get underlying prices for given sticker

        potentially get 1 additional year to calculate IV rank
        Returns
        -------
        Underlying price, including open, close, high, and low of the day
        """
        self._underlying_price = get_underlying_price(self.ticker, self.start_date, self.end_date,
                                                      self.period_type, self.frequency_type, self.frequency)

    def get_VIX_price(self):
        """
        Get underlying prices for given sticker

        potentially get 1 additional year to calculate IV rank
        Returns
        -------
        Underlying price, including open, close, high, and low of the day
        """
        vix_price = get_underlying_price('VIX', self.start_date, self.end_date,
                                                      self.period_type, self.frequency_type, self.frequency)
        return vix_price

    def _set_historical_volatility(self):
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

    def _get_volatility(self):
        """
        Use quandl API to fetch IV, HV data at multiple periods (10, 20, etc...)

        Returns
        -------

        """
        self.implied_volatility, self.historic_volatility_queried = get_volatility([],[],[],'C')

    def _get_trimmed_history(self):
        """
        Truncate the underlying price history to the given time window (remove extra history for volatility calcs)

        -------
        """
        self.underlying_price_truncated_ = self._underlying_price.truncate(self.start_date.date(), self.end_date.date())
        self.historic_volatility_truncated_ = self.historic_volatility.truncate(self.start_date.date(),
                                                                                self.end_date.date())
        self.historic_volatility_queried_truncated_ = self.historic_volatility_queried.truncate(self.start_date.date(),
                                                                                                self.end_date.date())
        self.implied_volatility_truncated_ = self.implied_volatility.truncate(self.start_date.date(),
                                                                              self.end_date.date())

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

    def _set_time_to_expiration(self):
        """
        Calculate time to expire for each day

        Returns
        -------

        """
        self.time_to_expiration = self.underlying_price_truncated_.reset_index(drop=False)[['Date']]
        self.time_to_expiration['Time to Expire'] = (self.expiry - self.time_to_expiration['Date']).dt.days
        self.time_to_expiration.set_index('Date', inplace=True)

    def _set_risk_free_rate(self):
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

    def _set_option_price(self):
        """
        Calculate option price history given changes in spot, volatility, and date

        Returns
        -------

        """
        self._set_historical_volatility()
        self._get_trimmed_history()
        self._get_trading_days()
        self._set_time_to_expiration()
        # self._set_risk_free_rate()
        self.option_price = OP.european_vanilla_option(self.underlying_price_truncated_['close'], self.strike,
                                                       self.time_to_expiration['Time to Expire'],
                                                       self.implied_volatility_truncated_['IV'],
                                                       0.01, self.option_type)
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
        self.underlying_holding_period_return['close'] = self.underlying_price_truncated_['close'] / self.underlying_price_truncated_['close'][0] - 1


    def _set_HV_rank(self):
        """
        Calculate HV rank using calculated historical volatility data
        Returns
        -------

        """
        pct_rank = lambda x: pd.Series(x).rank(pct=True).iloc[-1]
        self.HV_rank = pd.DataFrame(self.historic_volatility.rolling(252)['Hist Vol'].apply(pct_rank))
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