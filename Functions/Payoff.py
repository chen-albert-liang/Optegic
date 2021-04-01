import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
from Functions.OptionBasics import OptionPricing
import Functions.OptionPricingModels as OP


class OptionPayOffs(OptionPricing):
    """
    Payoff analysis doesn't need exit date/ end date.  end_date_ here is used as expiration.
    Named this way only to be consistent with parent class
    """

    def __init__(self,  ticker_, strike_, start_date_, end_date_, option_type_, action_):
        super(OptionPayOffs, self).__init__(ticker_, start_date_, end_date_, option_type_)

        self.strike = strike_
        self.end_date = start_date_.date()
        self.expiry = end_date_.date()  # For payoff analysis end_date_ acts as expiration day for time value calcs
        self.toe = (self.expiry - self.start_date).days
        self.action = action_
        self.payoff_expiration = pd.DataFrame()
        self.payoff_current = pd.DataFrame()
        self.option_price = []
        self.breakeven = []
        self.probability_of_profit = []
        self.spot_plot = np.arange(np.mean(self.strike) * 0.75, np.mean(self.strike) * 1.35)
        # self.implied_volatility = pd.DataFrame()

    def initialize_payoff_variables(self):
        self._get_underlying_price()
        self._get_volatility()
        self._set_current_option_price()
        self._set_payoff_current()
        self._set_payoff_expiry()
        self._set_breakeven()
        self._set_probability_of_profit()

    def _set_current_option_price(self):

        """
        Using the latest underlying and volatility data to calculate the current option price
        Returns
        -------

        """
        i = 0
        self.option_price = []
        for _ in self.action:
            leg_price = OP.european_vanilla_option(self.underlying_price_truncated_['close'][0], self.strike[i],
                                                   self.toe, self.implied_volatility.values[0, i], 0.01,
                                                   self.option_type[i])
            self.option_price.append(leg_price)
            i += 1

    def _set_payoff_expiry(self):
        """
        Calculate payoff at expiration

        Returns
        -------

        """
        i = 0
        for _ in self.action:
            if self.option_type == 'C' and self.action == 'L':
                payoff_expiration = np.maximum(self.spot_plot - self.strike[i], 0) - self.option_price[i]
            if self.option_type == 'C' and self.action == 'S':
                payoff_expiration = np.minimum(self.strike[i] - self.spot_plot, 0) + self.option_price[i]
            if self.option_type == 'P' and self.action == 'L':
                payoff_expiration = np.maximum(self.strike[i] - self.spot_plot, 0) - self.option_price[i]
            if self.option_type == 'P' and self.action == 'S':
                payoff_expiration = np.minimum(self.spot_plot - self.strike[i], 0) + self.option_price[i]
            self.payoff_expiration = self.payoff_expiration.join(payoff_expiration)
            i += 1

    def _set_payoff_current(self):
        """
        Calculate payoff as of right now

        Returns
        -------

        """
        i = 0
        for _ in self.action:
            payoff_current_incl_cost = OP.european_vanilla_option(self.spot_plot, self.strike[i], self.toe,
                                                                  self.implied_volatility.values[0, i], 0.01,
                                                                  self.option_type[i])
            if self.action[i] == 'L':
                payoff_current = payoff_current_incl_cost - self.option_price[i]
            if self.action[i] == 'S':
                payoff_current = self.option_price[i] - payoff_current_incl_cost
            self.payoff_current = self.payoff_current.join(payoff_current)
            i += 1

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
            if self.option_type[i] == 'C' and self.action[i] == 'L':
                probability_of_below_strike = norm.cdf(
                    np.log(self.strike[i] / self.underlying_price_truncated_.values[0, 0]) / self.implied_volatility.values[0, i])
                probability_of_profit = 1-probability_of_below_strike
            if self.option_type[i] == 'C' and self.action[i] == 'S':
                probability_of_below_strike = norm.cdf(
                    np.log(self.strike[i] / self.underlying_price_truncated_.values[0, 0]) / self.implied_volatility.values[0, i])
                probability_of_profit = probability_of_below_strike
            if self.option_type[i] == 'P' and self.action[i] == 'L':
                probability_of_below_strike = norm.cdf(
                    np.log(self.strike[i] / self.underlying_price_truncated_.values[0, 0]) / self.implied_volatility.values[0, i])
                probability_of_profit = probability_of_below_strike
            if self.option_type[i] == 'P' and self.action[i] == 'S':
                probability_of_below_strike = norm.cdf(
                    np.log(self.strike[i] / self.underlying_price_truncated_.values[0, 0]) / self.implied_volatility.values[0, i])
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
            if self.option_type[i] == 'C' and self.action[i] == 'L':
                breakeven = self.strike[i] + self.option_price[i]
            if self.option_type[i] == 'C' and self.action[i] == 'S':
                breakeven = self.strike[i] + self.option_price[i]
            if self.option_type[i] == 'P' and self.action[i] == 'L':
                breakeven = self.strike[i] - self.option_price[i]
            if self.option_type[i] == 'P' and self.action[i] == 'S':
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

