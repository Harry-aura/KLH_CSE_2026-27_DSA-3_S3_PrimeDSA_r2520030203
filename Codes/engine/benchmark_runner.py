"""Benchmark Runner: Miller-Rabin vs Standard Trial Division.

Evaluates performance across bit lengths from 16-bit to 1024-bit, demonstrating
the exponential O(2^(b/2)) complexity of trial division versus the polynomial
O(k * b^3) complexity of Miller-Rabin.
"""

import math
import time
from typing import Dict, List, Any, Optional

from .modular_arithmetic import decompose_n_minus_one, mod_exp
from .miller_rabin import miller_rabin_test
from .prime_generator import generate_probable_prime


def trial_division(
    n: int,
    max_steps: int = 200_000,
    timeout_sec: float = 0.05,
) -> Dict[str, Any]:
    """Execute standard trial division up to sqrt(n) with step capping and timeout protection.

    Args:
        n: The integer to test.
        max_steps: Maximum trial divisors to evaluate before capping.
        timeout_sec: Maximum execution time allowed before aborting.

    Returns:
        Dictionary containing primality determination, elapsed time, and completion status.
    """
    start_ns = time.perf_counter_ns()
    if n <= 1:
        return {"is_prime": False, "witness": None, "completed": True, "time_ms": (time.perf_counter_ns() - start_ns) / 1e6}
    if n in (2, 3):
        return {"is_prime": True, "witness": None, "completed": True, "time_ms": (time.perf_counter_ns() - start_ns) / 1e6}
    if n % 2 == 0:
        return {"is_prime": False, "witness": 2, "completed": True, "time_ms": (time.perf_counter_ns() - start_ns) / 1e6}
    if n % 3 == 0:
        return {"is_prime": False, "witness": 3, "completed": True, "time_ms": (time.perf_counter_ns() - start_ns) / 1e6}

    # Capped integer square root
    # For very large numbers, avoid full exact sqrt calculation if it overflows standard float
    try:
        limit = math.isqrt(n)
    except OverflowError:
        limit = 1 << ((n.bit_length() + 1) // 2)

    d = 5
    diff = 2
    steps = 0
    timeout_ns = int(timeout_sec * 1e9)

    while d <= limit:
        if n % d == 0:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1e6
            return {"is_prime": False, "witness": d, "completed": True, "time_ms": round(elapsed_ms, 4)}

        d += diff
        diff = 6 - diff
        steps += 1

        if steps >= max_steps or (time.perf_counter_ns() - start_ns) >= timeout_ns:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1e6
            # Projected theoretical time for full sqrt(n)
            total_operations_needed = max(1, limit // 3)
            projected_time_ms = elapsed_ms * (total_operations_needed / max(1, steps))
            return {
                "is_prime": None,
                "witness": None,
                "completed": False,
                "time_ms": round(elapsed_ms, 4),
                "steps_evaluated": steps,
                "projected_time_ms": projected_time_ms,
                "reason": "Exceeded safe time/step threshold (Trial Division O(sqrt(n)) infeasible)",
            }

    elapsed_ms = (time.perf_counter_ns() - start_ns) / 1e6
    return {"is_prime": True, "witness": None, "completed": True, "time_ms": round(elapsed_ms, 4)}


# Benchmark curated prime sample dataset for instant reproducible comparisons
BENCHMARK_PRIMES = {
    16: 65521,
    24: 16777213,
    32: 4294967291,
    48: 281474976710597,
    64: 18446744073709551557,
    128: 340282366920938463463374607431768211297,
    256: 115792089237316195423570985008687907853269984665640564039457584007913129639747,
    512: (1 << 521) - 1,  # 521-bit Mersenne prime
    1024: (1 << 1024) - 105,  # Known 1024-bit prime
}


def run_benchmark_comparison(iterations: int = 40) -> Dict[str, Any]:
    """Execute comparative benchmark between Miller-Rabin and Trial Division across bit lengths.

    Args:
        iterations: Number of Miller-Rabin iterations.

    Returns:
        Dictionary containing comparative performance metrics, chart series, and complexity notes.
    """
    bit_lengths = [16, 24, 32, 48, 64, 128, 256, 512, 1024]
    results: List[Dict[str, Any]] = []

    for b in bit_lengths:
        prime_val = BENCHMARK_PRIMES.get(b)
        if prime_val is None:
            prime_val, _, _, _ = generate_probable_prime(b, iterations=10)

        # Run Miller-Rabin (multiple runs for tiny numbers to ensure precision)
        mr_res = miller_rabin_test(prime_val, iterations=iterations, use_custom_modpow=False)
        mr_time_ms = mr_res.execution_time_ms

        # Run Trial Division
        td_res = trial_division(prime_val, max_steps=100_000, timeout_sec=0.03)
        td_time_ms = td_res["time_ms"]
        td_completed = td_res["completed"]
        projected_td_ms = td_res.get("projected_time_ms", td_time_ms)

        speedup = round(projected_td_ms / max(0.0001, mr_time_ms), 2) if mr_time_ms > 0 else 1.0

        results.append({
            "bit_length": b,
            "sample_prime_preview": str(prime_val) if len(str(prime_val)) <= 25 else str(prime_val)[:12] + "..." + str(prime_val)[-10:],
            "miller_rabin_time_ms": mr_time_ms,
            "miller_rabin_time_us": mr_res.execution_time_us,
            "trial_division_time_ms": td_time_ms,
            "trial_division_completed": td_completed,
            "trial_division_projected_ms": round(projected_td_ms, 2) if not td_completed else td_time_ms,
            "speedup_factor": speedup,
            "status": "Verified Prime" if mr_res.is_prime else "Composite",
        })

    return {
        "iterations": iterations,
        "results": results,
        "complexity_analysis": {
            "miller_rabin": "O(k * log^3(n)) = O(k * b^3) [Polynomial Time - Feasible for > 1024 bits]",
            "trial_division": "O(sqrt(n)) = O(2^(b/2)) [Exponential Time - Intractable beyond 64 bits]",
        },
    }
