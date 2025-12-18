
def is_large_trade(amount_in: float, **kwargs) -> bool:
    """
    Checks if a trade amount is considered large.
    """
    print(f"PREDICATE: Checking if trade amount {amount_in} is large.")
    return amount_in > 1000
