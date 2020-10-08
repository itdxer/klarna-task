CATEGORICAL_FEATURES = [
    "merchant_category",
    "merchant_group",
    "name_in_email",
]
NUMERICAL_FEATURES = [
    "account_amount_added_12_24m",
    "account_days_in_dc_12_24m",
    "account_days_in_rem_12_24m",
    "account_days_in_term_12_24m",
    "account_incoming_debt_vs_paid_0_24m",
    "account_status",
    "account_worst_status_0_3m",
    "account_worst_status_12_24m",
    "account_worst_status_3_6m",
    "account_worst_status_6_12m",
    "age",
    "avg_payment_span_0_12m",
    "avg_payment_span_0_3m",
    "max_paid_inv_0_12m",
    "max_paid_inv_0_24m",
    "num_active_div_by_paid_inv_0_12m",
    "num_active_inv",
    "num_arch_dc_0_12m",
    "num_arch_dc_12_24m",
    "num_arch_ok_0_12m",
    "num_arch_ok_12_24m",
    "num_arch_rem_0_12m",
    "num_unpaid_bills",
    "status_last_archived_0_24m",
    "status_2nd_last_archived_0_24m",
    "status_3rd_last_archived_0_24m",
    "status_max_archived_0_6_months",
    "status_max_archived_0_12_months",
    "status_max_archived_0_24_months",
    "recovery_debt",
    "sum_capital_paid_account_0_12m",
    "sum_capital_paid_account_12_24m",
    "sum_paid_inv_0_12m",
    "time_hours",
    "worst_status_active_inv",
]
# Features which won't be used during the training
OTHER_FEATURES = [
    "has_paid",
    "num_arch_written_off_0_12m",
    "num_arch_written_off_12_24m",
    "uuid",
    "default",
]
MODEL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
VALID_FEATURES = MODEL_FEATURES + OTHER_FEATURES

# Sanity check: making sure that the same feature doesn't appear multiple times in the list
assert len(set(VALID_FEATURES)) == len(VALID_FEATURES)
