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


