from DataQuery.Query import get_underlying_price, get_treasury_rate, get_expiration_dates, get_option_chains
import pandas as pd
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


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

    def __init__(self, ticker, start_date, end_date, option_type='C',
                 frequency='daily', dividend=0.0):
        """
        Parameters
        ----------
        ticker
        expiration_date
        """
        # Specified by user
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

        # Default parameters for data query
        self.frequency = frequency
        self.dividend = dividend or 0

        # Queried
        self.vix = pd.DataFrame()


    def initialize_variables(self):
        self._get_expiration_dates()
        self._get_underlying_price()
        # self._get_volatility()

    def _get_expiration_dates(self):
        self.expiration_dates, self.strikes = get_expiration_dates(self.ticker)

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
        Get underlying prices for given ticker
        Returns
        -------
        Underlying price, including open, close, high, and low of the day
        """
        self.underlying_price = get_underlying_price(self.ticker, self.start_date, self.end_date, self.frequency)

    def _get_vix(self):
        """
        Get underlying prices for given ticker

        potentially get 1 additional year to calculate IV rank
        Returns
        -------
        Underlying price, including open, close, high, and low of the day
        """
        self.vix = get_underlying_price('VIX', self.start_date, self.end_date, self.frequency)

    def _get_option_chain(self):
        """
        Get option chain for given ticker and expiration

        Returns
        -------

        """

    # def _set_iv_rank(self):
    #     """
    #     Calculate IV rank using quandl example data
    #     Returns
    #     -------
    #
    #     """
    #     pct_rank = lambda x: pd.Series(x).rank(pct=True).iloc[-1]
    #     self.IV_rank = pd.DataFrame(self.implied_volatility_raw.rolling(252)['IV'].apply(pct_rank))
    #     self.IV_rank = self.IV_rank.rename(columns={'IV': 'IV Rank'}).dropna()


    def plot_price_history(self):
        """
        Two scales for each instrument

        Returns
        -------

        """

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.underlying_price.index,  self.underlying_price['close'], 'g', label=self.ticker)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Price ($)")
        fig.autofmt_xdate()
        ax1.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
        plt.title(self.ticker + ' Historical Price')