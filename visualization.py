import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import OptionPricingModels as OP
# Create Class plot_template !!!

class option_visualization(object):
    """
    Visulize the difference between underyling and option returns
    """

    def __init__(self, trading_days, option_price, underlying_price, option_return, underlying_return,
                 implied_volatility, strike, expiry, entry_date, lb, ub, option_type, resolution=1):
        self.trading_days = trading_days.index
        self.option_price = option_price
        self.underlying_price = underlying_price
        self.option_return = option_return * 100 # Multiply by 100 for pct. plot purpose
        self.underlying_return = underlying_return * 100 # Multiply by 100 for pct. plot purpose
        self.implied_volatility = implied_volatility
        self.option_type = option_type

        if strike:
            self.spot = np.arange(lb, ub+1, resolution)
            self.strike = strike
            self.payoff = pd.DataFrame()
            self.toe = (expiry - entry_date).days

    # def plot_payoff_table(self):
    #     return

    def _expiry_payoff_calc(self):
        """
        Calculate payoff at expiration

        Returns
        -------

        """
        if self.option_type == 'C':
            payoff_exp = np.maximum(self.spot - self.strike, 0)
        if self.option_type == 'P':
            payoff_exp = np.maximum(self.strike - self.spot, 0)
        return payoff_exp

    def _current_payoff_calc(self):
        """
        Calculate payoff as of right now

        Returns
        -------

        """
        payoff_current = OP.european_vanilla_option(self.spot, self.strike, self.toe,
                                                    self.implied_volatility.values[0,0], 0.01, option=self.option_type)
        return payoff_current

    def plot_payoff(self):
        """
        Payoff plotting

        Returns
        -------

        """
        exp_payoff = self._expiry_payoff_calc()
        cur_payoff = self._current_payoff_calc()

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.spot,  exp_payoff, 'b', label='At Expiry')
        ax1.plot(self.spot, cur_payoff, 'r', label='Current')
        ax1.set_xlabel("Spot Price ($)")
        ax1.set_ylabel("Payoff ($)")
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        plt.title('Option Payoff')

    def plot_price_history(self):
        """
        Two scales for each instrument

        Returns
        -------

        """
        fig, ax1 = plt.subplots(2, figsize=(12, 6))
        ax1[0].plot(self.trading_days, self.option_price, 'r-^', label='Option')
        ax2 = ax1[0].twinx()
        ax2.plot(self.trading_days, self.underlying_price['close'], 'b-o', label='Underlying')
        ax1[0].legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax1[0].spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1[0].set_xlabel("Date")
        ax1[0].set_ylabel("Option Price")
        ax2.set_ylabel("Underlying Price")
        ax1[1].plot(self.trading_days, self.implied_volatility, 'b-', label='Implied Volatility')
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
        ax1.plot(self.trading_days,  self.option_return, 'r-^', label='Option')
        ax2 = ax1.twinx()
        ax2.plot(self.trading_days, self.underlying_return, 'b-o', label='Underlying')
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax1.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Option P&L")
        ax2.set_ylabel("Underlying P&L")
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
        plt.title('Holding Period Return')

    #
    # def plot_option_drawdown(self):
    #     fig, ax = plt.subplots()
    #     ax_option, ax_underlying = ax.plot(self.trading_days, self.option_drawdown, 'r-^', self.trading_days,
    #                                        self.underlying_drawdown, 'b-o')
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.legend((ax_option, ax_underlying), ('Option Price', 'Underlying Price'))
    #     ax.yaxis.set_major_formatter(mtick.PercentFormatter())