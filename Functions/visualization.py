import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from mpl_axes_aligner import align


# Create Class plot_template !!!
class PayOffVisualization(object):
    """
    Payoff Visualization
    """
    def __init__(self, exp_payoff, cur_payoff, breakeven, probability_of_profit, spot_prices):
        self.exp_payoff = exp_payoff
        self.cur_payoff = cur_payoff
        self.breakeven = breakeven
        self.probability_of_profit = probability_of_profit
        self.spot_plot = spot_prices

    def plot_payoff(self):
        """
        Payoff plotting

        Returns
        -------

        """
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.spot_plot,  self.exp_payoff, 'b', label='Expiration Day')
        ax1.plot(self.spot_plot, self.cur_payoff, 'r', label='Entry Day')
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


class PnLVisualization(object):
    """
    Visulize the difference between underyling and option returns
    """

    def __init__(self, trading_days, option_price, underlying_price, option_return, underlying_return,
                 implied_volatility):
        self.trading_days = trading_days.index
        self.option_price = option_price
        self.underlying_price = underlying_price
        self.option_return = option_return * 100  # Multiply by 100 for pct. plot purpose
        self.underlying_return = underlying_return * 100  # Multiply by 100 for pct. plot purpose
        self.implied_volatility = implied_volatility

    # def plot_payoff_table(self):
    #     return

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
        ax1.axhline(0, color='k', linestyle=':')
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

        # Align y-axes
        org1 = 0.0  # Origin of first axis
        org2 = 0.0  # Origin of second axis
        pos = 0.5  # Position the two origins are aligned
        align.yaxes(ax1, org1, ax2, org2, pos)
        plt.tight_layout()
        plt.title('Holding Period Return')


    # def plot_option_drawdown(self):
    #     fig, ax = plt.subplots()
    #     ax_option, ax_underlying = ax.plot(self.trading_days, self.option_drawdown, 'r-^', self.trading_days,
    #                                        self.underlying_drawdown, 'b-o')
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.legend((ax_option, ax_underlying), ('Option Price', 'Underlying Price'))
    #     ax.yaxis.set_major_formatter(mtick.PercentFormatter())