import numpy as np
from scipy.stats import norm
from typing import Dict, Any, Union
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

class OptionPricingInput(BaseModel):
    S: float = Field(..., description="Spot price of the underlying asset.")
    K: float = Field(..., description="Strike price of the option.")
    T: float = Field(..., description="Time to expiration in years.")
    r: float = Field(..., description="Risk-free interest rate (decimal).")
    sigma: float = Field(..., description="Volatility of the underlying asset (decimal).")
    flag: str = Field(..., description="Option type: 'c' for Call, 'p' for Put.")

class OptionsMathToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="options_math", **kwargs)
        self.register(self.calculate_black_scholes)
        self.register(self.calculate_greeks)

    def _d1(self, S, K, T, r, sigma):
        # Handle edge cases
        if sigma <= 0 or S <= 0 or K <= 0:
            return 0
        return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    def _d2(self, d1, T, sigma):
        return d1 - sigma * np.sqrt(T)

    def calculate_black_scholes(self, S: float, K: float, T: float, r: float, sigma: float, flag: str) -> float:
        """
        Calculates the Black-Scholes price for a call or put option.
        Champion: Logic adapted from `vollib` (pure python implementation).
        Handles edge cases where T <= 0 (intrinsic value) or sigma <= 0 (intrinsic value).
        """
        intrinsic_val_c = max(0, S - K)
        intrinsic_val_p = max(0, K - S)

        if T <= 0:
            return intrinsic_val_c if flag == 'c' else intrinsic_val_p

        if sigma <= 0:
            # If volatility is zero, the option is worth its intrinsic value discounted (conceptually),
            # but usually just intrinsic is a safe fallback for "expired or deterministic".
            # Technically BSM with sigma=0 is tricky, but intrinsic is the practical floor.
            return intrinsic_val_c if flag == 'c' else intrinsic_val_p

        if S <= 0:
            return 0 if flag == 'c' else max(0, K * np.exp(-r * T)) # Put worth PV(K) if S=0

        d1 = self._d1(S, K, T, r, sigma)
        d2 = self._d2(d1, T, sigma)

        if flag == 'c':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif flag == 'p':
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            raise ValueError("Flag must be 'c' or 'p'")

        return float(price)

    def calculate_greeks(self, input: OptionPricingInput) -> Dict[str, float]:
        """
        Calculates Option Greeks (Delta, Gamma, Theta, Vega, Rho).
        Champion: Logic adapted from `vollib`.

        Note on Units:
        - Theta: Daily decay (annualized theta / 365).
        - Vega: Change in price for a 1% change in volatility (raw vega / 100).
        """
        S, K, T, r, sigma, flag = input.S, input.K, input.T, input.r, input.sigma, input.flag

        if T <= 0 or sigma <= 0 or S <= 0:
             # Return zero Greeks for expired/invalid state (simplified)
             return {
                 "price": self.calculate_black_scholes(S, K, T, r, sigma, flag),
                 "delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0
             }

        d1 = self._d1(S, K, T, r, sigma)
        d2 = self._d2(d1, T, sigma)

        pdf_d1 = norm.pdf(d1)
        cdf_d1 = norm.cdf(d1)
        cdf_d2 = norm.cdf(d2)
        cdf_neg_d1 = norm.cdf(-d1)
        cdf_neg_d2 = norm.cdf(-d2)

        # Gamma (Same for Call and Put)
        gamma = pdf_d1 / (S * sigma * np.sqrt(T))

        # Vega (Same for Call and Put) - Scaled for 1% vol change
        vega = (S * pdf_d1 * np.sqrt(T)) * 0.01

        if flag == 'c':
            delta = cdf_d1
            theta_annual = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(T))
                     - r * K * np.exp(-r * T) * cdf_d2)
            theta = theta_annual / 365.0
            rho = (K * T * np.exp(-r * T) * cdf_d2) * 0.01
        elif flag == 'p':
            delta = cdf_d1 - 1
            theta_annual = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(T))
                     + r * K * np.exp(-r * T) * cdf_neg_d2)
            theta = theta_annual / 365.0
            rho = (- K * T * np.exp(-r * T) * cdf_neg_d2) * 0.01
        else:
             raise ValueError("Flag must be 'c' or 'p'")

        return {
            "price": self.calculate_black_scholes(S, K, T, r, sigma, flag),
            "delta": float(delta),
            "gamma": float(gamma),
            "theta": float(theta),
            "vega": float(vega),
            "rho": float(rho)
        }
