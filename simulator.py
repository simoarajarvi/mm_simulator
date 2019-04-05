import random
import numpy as np
from sklearn.linear_model import LinearRegression
import seaborn as sns
import locale
import seaborn as sns
import matplotlib.pyplot as plt



class MarketingMonth:
    def __init__(self, month, channel_budgets, channel_flags, sales, adjust_mm_logic):
        self.month = month
        self.channel_budgets = channel_budgets
        self.channel_flags = channel_flags
        self.sales = sales
        self.adjust_mm_logic = adjust_mm_logic

    def print(self):
        print(f"Month: {self.month}")
        print(f"Channel Budgets: {self.channel_budgets}")
        print(f"Channel Flags: {self.channel_flags}")
        print(f"Sales: {self.sales}\n")

def adjust_mm_default(mm_list, channels, current_month, total_budget):
    channel_to_increase = mm_list[-1].channel_flags[0][0]
    adjustment = total_budget * 0.10
    adjusted_budgets = {ch: mm_list[-1].channel_budgets[ch] - adjustment / (len(channels) - 1) if ch != channel_to_increase else mm_list[-1].channel_budgets[ch] + adjustment for ch in channels}
    return {ch: max(0, budget) for ch, budget in adjusted_budgets.items()}

def adjust_mm_regression(mm_list, channels, current_month, total_budget):
    if current_month < 3:
        return adjust_mm_default(mm_list, channels, current_month, total_budget)
    
    X = [list(mm.channel_budgets.values()) for mm in mm_list]
    y = [mm.sales for mm in mm_list]

    reg = LinearRegression().fit(X, y)
    coefs = reg.coef_

    total_adjustment = sum(abs(coef) for coef in coefs)
    adjusted_budgets = {channel: max(0, budget + (budget * coef / total_adjustment)) for channel, budget, coef in zip(channels, mm_list[-1].channel_budgets.values(), coefs)}
    return adjusted_budgets

def simulate_month(month, channels, channel_correlations, base_month_sales, num_sales_events, total_budget, previous_mm_list, adjust_function):
    channel_budgets = adjust_function(previous_mm_list, channels, month, total_budget) if previous_mm_list else {ch: total_budget / len(channels) for ch in channels}
    
    sales_from_channels = sum(channel_budgets[channel] * channel_correlations[channel] for channel in channels)
    sales = base_month_sales + sales_from_channels
    sales = sales * random.uniform(0.8, 1.2)

    channel_flags_list = [random.sample(channels, k=random.randint(1, len(channels))) for _ in range(num_sales_events)]

    return MarketingMonth(month, channel_budgets, channel_flags_list, sales, adjust_function.__name__)


def plot_budgets(all_mm_lists, channels):
    sns.set_theme(style="whitegrid")
    
    # Setting up the grid.
    fig, axs = plt.subplots(2, len(all_mm_lists), figsize=(10 * len(all_mm_lists), 10))
    
    # Plotting individual budget charts on the first row.
    for idx, mm_list in enumerate(all_mm_lists):
        for channel in channels:
            total_sales = sum([mm.sales for mm in mm_list])
            channel_budgets = [mm.channel_budgets[channel] for mm in mm_list]
            axs[0, idx].plot([mm.month for mm in mm_list], channel_budgets, label=channel)
            axs[0, idx].set_title(f"Monthly Channel Budgets - {mm_list[0].adjust_mm_logic} - Total Sales: ${round(total_sales/1000)}K")
            axs[0, idx].set_ylabel('Budget in $')
            axs[0, idx].set_xlabel('Month')
            axs[0, idx].legend()
            axs[0, idx].get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))

    
    for i in range(1, len(all_mm_lists)):
        fig.delaxes(axs[1, i])

    plt.tight_layout()
    plt.show()


def main(start_month, end_month, channels, channel_correlations, monthly_budget, base_month_sales,num_sales_events):
    all_mm_lists = []
    adjust_functions = [adjust_mm_default, adjust_mm_regression]

    for adjust_function in adjust_functions:
        mm_list = []
        for month in range(start_month, end_month + 1):
            mm = simulate_month(month, channels, channel_correlations, base_month_sales, num_sales_events, monthly_budget, mm_list, adjust_function)
            mm_list.append(mm)
        all_mm_lists.append(mm_list)
    
    plot_budgets(all_mm_lists, channels)

if __name__ == "__main__":
    main(1, 24,channels=['channel_1', 'channel_2', 'channel_3', 'channel_4'],channel_correlations={'channel_1': 0.6, 'channel_2': 0.1, 'channel_3': 0.3, 'channel_4': 0.15}, monthly_budget=10000, base_month_sales=12000, num_sales_events=5)

