from DataQuery.Query import get_underlying_price, get_treasury_rate, get_volatility, get_expiration_dates, get_trading_dates
import pandas as pd
import logging
import matplotlib.pyplot as plt


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

    def initialize_variables(self):
        self._get_trading_days()
        self._get_expiration_dates()
        self._get_underlying_price()
        # self._get_volatility()

    def _get_trading_days(self):
        """
        Get eligible trading days during the specified time window

        Returns
        -------

        """
        self.trading_days = get_trading_dates(self.start_date, self.end_date)

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
        self.underlying_price_raw = get_underlying_price(self.ticker, self.start_date, self.end_date,
                                                         self.period_type, self.frequency_type, self.frequency)
        self.underlying_price_truncated_ = self.get_trimmed_history(self.underlying_price_raw, self.start_date,
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
        i = 0
        for _ in self.option_type:
            implied_volatility, historic_volatility_queried_raw = get_volatility([], [], [], self.option_type[i])
            implied_volatility.rename(columns={'IV': 'IV'+str(i)}, inplace=True)
            if self.implied_volatility_raw.empty:
                self.implied_volatility_raw = implied_volatility
            else:
                self.implied_volatility_raw = self.implied_volatility_raw.join(implied_volatility)
            i += 1
        self.implied_volatility_truncated_ = self.get_trimmed_history(self.implied_volatility_raw, self.start_date,
                                                                      self.end_date)

    def _set_iv_rank(self):
        """
        Calculate IV rank using quandl example data
        Returns
        -------

        """
        pct_rank = lambda x: pd.Series(x).rank(pct=True).iloc[-1]
        self.IV_rank = pd.DataFrame(self.implied_volatility_raw.rolling(252)['IV'].apply(pct_rank))
        self.IV_rank = self.IV_rank.rename(columns={'IV': 'IV Rank'}).dropna()

    @staticmethod
    def get_trimmed_history(data, start_date, end_date):
        """
        Truncate the underlying price history to the given time window (remove extra history for volatility calcs)

        -------
        """
        data_truncated = data.truncate(start_date, end_date)
        return data_truncated

    def plot_price_history(self):
        """
        Two scales for each instrument

        Returns
        -------

        """
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.trading_days['Date'],  self.underlying_price_truncated_['close'], 'b', label=self.ticker)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Price ($)")
        plt.title(self.ticker + ' Historical Price (As of 2017-12-31)')