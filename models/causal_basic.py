import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

def prop_scores(customer_age,revenue,channel_hit,sales,df):
    log_reg = LogisticRegression().fit(df[['customer_age', 'revenue']], df['channel_hit'])
    df['propensity_score'] = log_reg.predict_proba(df[['customer_age', 'revenue']])[:, 1]
    df['weight'] = np.where(df['channel_hit'] == 1,
                        1 / df['propensity_score'],
                        1 / (1 - df['propensity_score']))
    ATE_weighted = np.average(df[df['channel_hit'] == 1]['sales'], weights=df[df['channel_hit'] == 1]['weight']) - \
               np.average(df[df['channel_hit'] == 0]['sales'], weights=df[df['channel_hit'] == 0]['weight'])
    
    return ATE_weighted, df


def matching(customer_age,revenue,channel_hit,sales,df):
    # propensity scores
    log_reg = LogisticRegression().fit(df[['customer_age', 'revenue']], df['channel_hit'])
    df['propensity_score'] = log_reg.predict_proba(df[['customer_age', 'revenue']])[:, 1]

    # matching
    treated = df[df['channel_hit'] == 1]
    control = df[df['channel_hit'] == 0]
    matcher = NearestNeighbors(n_neighbors=1).fit(control[['propensity_score']])
    matched_indices = matcher.kneighbors(treated[['propensity_score']], return_distance=False).flatten()
    matched_control = control.iloc[matched_indices]

    # Ate
    ATE_matched = treated['sales'].mean() - matched_control['sales'].mean()
    return ATE_matched,df

def rcm_simple(df):
    # Estimate ATE with simple diff in means
    treated_group = df[df['channel_hit'] == 1]
    control_group = df[df['channel_hit'] == 0]

    ATE = treated_group['sales'].mean() - control_group['sales'].mean()
    return ATE, df


def simulate():
    N = 1000

    np.random.seed(42)
    customer_age = np.random.randint(0, 15, N)
    revenue = np.random.randint(20000, 100000, N)
    probability_channel_hit = 0.2 + 0.5 * (revenue > 50000)

    channel_hit = np.random.binomial(n=1, p=probability_channel_hit)

    baseline_sales_probability = 0.1 + 0.05 * (revenue > 50000)
    incremental_sales_due_to_channel = 0.3
    sales = np.random.binomial(n=1, p=baseline_sales_probability + channel_hit * incremental_sales_due_to_channel)

    df = pd.DataFrame({'customer_age': customer_age, 'revenue': revenue, 'channel_hit': channel_hit, 'sales': sales})

    ate_prp,_ = prop_scores(customer_age,revenue,channel_hit,sales,df)
    ate_match,_ = matching(customer_age,revenue,channel_hit,sales,df)
    ate_rch,_ = rcm_simple(df)
    print(ate_prp,ate_match,ate_rch)
    
simulate()
