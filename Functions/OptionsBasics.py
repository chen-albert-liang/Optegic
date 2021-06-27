import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
from Functions.UnderlyingBasics import MarketPrices
import Functions.OptionPricingModels as OP
from DataQuery.Query import get_option_chains


class OptionBasics(MarketPrices):
    """
    Payoff analysis doesn't need exit date/ end date.  end_date_ here is used as expiration.
    Named this way only to be consistent with parent class
    """

    def __init__(self,  ticker_, strike_, start_date_, expiration_date_, option_type_, action_):
        super(OptionBasics, self).__init__(ticker_, start_date_, expiration_date_, option_type_)

        self.strike = strike_
        self.start_date = start_date_
        self.expiration_dates = pd.to_datetime(expiration_date_)
        self.option_type = option_type_
        self.toe = (self.expiration_dates - self.start_date).days
        self.action = action_
        self.payoff_expiration = pd.DataFrame()
        self.payoff_current = pd.DataFrame()
        self.chain = pd.DataFrame()
        self.option_price = []
        self.iv = []
        self.breakeven = []
        self.probability_of_profit = []
        self.spot_plot = np.arange(np.mean(self.strike) * 0.75, np.mean(self.strike) * 1.35, 0.5)

    def initialize_payoff_variables(self):
        self._get_underlying_price()
        self._get_current_option_price()
        self._set_payoff_current()
        self._set_payoff_expiry()
        self._set_breakeven()
        self._set_probability_of_profit()

    def _get_current_option_price(self):

        """
        Pulled directly from option chain
        Returns
        -------

        """
        i = 0
        for _ in self.action:
            self.chain = get_option_chains(self.ticker, self.expiration_dates[i])
            chain_option_type = self.chain[self.chain['option_type'] == self.option_type[i]]
            leg_info = chain_option_type[chain_option_type['strike'] == self.strike[i]]

            if self.action[i] == 'L':
                leg_price = leg_info['ask'].values[0]
            else:
                leg_price = leg_info['bid'].values[0]

            self.option_price.append(leg_price)

            # Approach 1: choose IV associate with the leg
            # self.iv.append(leg_info['mid_iv'].values[0])

            # Approach 2: choose IV for ATM
            self.iv.append(chain_option_type[chain_option_type['mid_iv'] > 0]['mid_iv'].min())
            i += 1

    def _set_payoff_expiry(self):
        """
        Calculate payoff at expiration

        Returns
        -------

        """
        i = 0
        for _ in self.action:
            if self.option_type[i] == 'call' and self.action[i] == 'L':
                payoff_expiration = np.maximum(self.spot_plot - self.strike[i], 0) - self.option_price[i]
            if self.option_type[i] == 'call' and self.action[i] == 'S':
                payoff_expiration = np.minimum(self.strike[i] - self.spot_plot, 0) + self.option_price[i]
            if self.option_type[i] == 'put' and self.action[i] == 'L':
                payoff_expiration = np.maximum(self.strike[i] - self.spot_plot, 0) - self.option_price[i]
            if self.option_type[i] == 'put' and self.action[i] == 'S':
                payoff_expiration = np.minimum(self.spot_plot - self.strike[i], 0) + self.option_price[i]

            payoff_expiration_df = pd.DataFrame(data=payoff_expiration, columns=['Payoff Leg-'+str(i+1)])
            if self.payoff_expiration.empty:
                self.payoff_expiration = payoff_expiration_df
            else:
                self.payoff_expiration = self.payoff_expiration.join(payoff_expiration_df)
            i += 1

        self.payoff_expiration['Payoff-Expiration'] = self.payoff_expiration.sum(axis=1)

    def _set_payoff_current(self):
        """
        Calculate payoff as of right now

        Returns
        -------

        """
        i = 0
        for _ in self.action:

            payoff_current_incl_cost = OP.european_vanilla_option(self.spot_plot, self.strike[i], self.toe[i],
                                                                  self.iv[i], 0.01, self.option_type[i])
            if self.action[i] == 'L':
                payoff_current = payoff_current_incl_cost - self.option_price[i]
            else:
                payoff_current = self.option_price[i] - payoff_current_incl_cost

            payoff_current_df = pd.DataFrame(payoff_current, columns=['Payoff Leg-'+str(i+1)])

            if self.payoff_current.empty:
                self.payoff_current = payoff_current_df
            else:
                self.payoff_current = self.payoff_current.join(payoff_current_df)
            i += 1

        self.payoff_current['Payoff-Current'] = self.payoff_current.sum(axis=1)

    def _set_probability_of_profit(self):
        """
        Calculate probability of profit
        !!！  This needs more work because the payoff calculated below did not consider the upfront debit/credit

        Returns
        -------
        Probability of profit
        """
        i = 0
        for _ in self.action:
            if self.option_type[i] == 'call' and self.action[i] == 'L':
                probability_of_below_strike = norm.cdf(
                    np.log((self.strike[i] + self.option_price[i]) / self.underlying_price['close'][0]) / self.iv[i])
                probability_of_profit = 1-probability_of_below_strike
            if self.option_type[i] == 'call' and self.action[i] == 'S':
                probability_of_below_strike = norm.cdf(
                    np.log((self.strike[i] + self.option_price[i]) / self.underlying_price['close'][0]) / self.iv[i])
                probability_of_profit = probability_of_below_strike
            if self.option_type[i] == 'put' and self.action[i] == 'L':
                probability_of_below_strike = norm.cdf(
                    np.log((self.strike[i] - self.option_price[i]) / self.underlying_price['close'][0]) / self.iv[i])
                probability_of_profit = probability_of_below_strike
            if self.option_type[i] == 'put' and self.action[i] == 'S':
                probability_of_below_strike = norm.cdf(
                    np.log((self.strike[i] - self.option_price[i]) / self.underlying_price['close'][0]) / self.iv[i])
                probability_of_profit = 1 - probability_of_below_strike
            self.probability_of_profit.append(probability_of_profit)
            i += 1

    def _set_breakeven(self):
        """
        Calculate break even points

        Returns
        -------
        Breakeven prices
        """
        i = 0
        for _ in self.action:
            if self.option_type[i] == 'call':
                breakeven = self.strike[i] + self.option_price[i]
            if self.option_type[i] == 'put':
                breakeven = self.strike[i] - self.option_price[i]
            self.breakeven.append(breakeven)
            i += 1

    def plot_payoff(self):
        """
        Payoff plotting

        Returns
        -------

        """
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.spot_plot,  self.payoff_expiration['Payoff-Expiration'], 'b', label='Expiration Day')
        ax1.plot(self.spot_plot, self.payoff_current['Payoff-Current'], 'r', label='Entry Day')
        ax1.axhline(0, color='k', linestyle=':')

        axis_ymin, axis_ymax = ax1.get_ylim()
        yaxis_breakeven = -axis_ymin/(axis_ymax-axis_ymin)

        i = 0
        for _ in self.breakeven:
            ax1.axvline(self.breakeven[i], ymin=0, ymax=yaxis_breakeven, color='k', linestyle=':')
            i += 1

        ax1.legend(loc='best')
        ax1.set_xlabel("Spot Price ($)")
        ax1.set_ylabel("Payoff ($)")
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        plt.title('Probability of Profit = ' + "{:.1%}".format(self.probability_of_profit[0]))

