from DataQuery.Query import get_underlying_price, get_treasury_rate, get_volatility, get_expiration_dates
import pandas as pd
import logging


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
            self.implied_volatility = self.implied_volatility.join(implied_volatility)
            print(self.implied_volatility)
            print(self.implied_volatility.values[0, i])
            # self.implied_volatility = self.get_trimmed_history(implied_volatility_raw, self.start_date, self.end_date)
            i += 1

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
