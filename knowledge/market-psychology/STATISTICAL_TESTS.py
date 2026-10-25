#!/usr/bin/env python3
"""Minimal reproducible statistics for experiment outputs."""
from __future__ import annotations
import math, random
from statistics import mean, stdev

def max_drawdown(returns):
    wealth = 1.0
    peak = 1.0
    worst = 0.0
    for r in returns:
        wealth *= 1 + r
        peak = max(peak, wealth)
        worst = min(worst, wealth / peak - 1)
    return worst

def annualized_return(returns, periods_per_year=12):
    if not returns:
        return float("nan")
    wealth = math.prod(1 + r for r in returns)
    return wealth ** (periods_per_year / len(returns)) - 1

def bootstrap_mean_ci(values, repetitions=10000, seed=280624):
    rng = random.Random(seed)
    samples = []
    for _ in range(repetitions):
        draw = [values[rng.randrange(len(values))] for _ in values]
        samples.append(mean(draw))
    samples.sort()
    return samples[int(.025 * len(samples))], samples[int(.975 * len(samples))]

def summarize(returns, periods_per_year=12):
    return {
        "n": len(returns),
        "mean": mean(returns) if returns else float("nan"),
        "volatility": stdev(returns) if len(returns) > 1 else float("nan"),
        "annualized_return": annualized_return(returns, periods_per_year),
        "max_drawdown": max_drawdown(returns),
        "bootstrap_mean_95": bootstrap_mean_ci(returns) if returns else (float("nan"), float("nan")),
    }
