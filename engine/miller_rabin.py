"""Miller-Rabin Primality Test Engine.

Supports arbitrary-precision BigInts (up to 1024 bits and beyond),
deterministic 64-bit verification, fast pre-checks, Carmichael number resilience,
and cryptographic-grade probabilistic confidence calculation.
"""

import math
import secrets
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .modular_arithmetic import decompose_n_minus_one, mod_exp, get_integer_metrics
from .small_primes import fast_precheck

# Proven deterministic base set for all n < 2^64 (approx 1.84 x 10^19)
# Source: Jim Sinclair / Pomerance, Selfridge, Wagstaff / Bleichenbacher
DETERMINISTIC_BASES_64: List[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]


@dataclass
class RoundTrace:
    """Diagnostic trace for a single Miller-Rabin test round."""
    round_index: int
    base_a: str
    initial_x: str
    passed: bool
    reason: str


@dataclass
class PrimalityResult:
    """Comprehensive primality determination result."""
    number: str
    is_prime: bool
    result: str  # "Prime" or "Composite"
    confidence_level: str  # e.g. "99.9999999999999999999999%" or "100.00% (Deterministic)"
    confidence_formula: str  # e.g. "1 - 4^(-40) >= 1 - 2^(-80)"
    error_probability: str  # e.g. "8.2718e-25" or "0.0"
    bit_length: int
    decimal_length: int
    execution_time_ns: int
    execution_time_us: float
    execution_time_ms: float
    rounds_completed: int
    method: str  # "Deterministic Miller-Rabin", "Probabilistic Miller-Rabin", "Small Prime Pre-check", etc.
    deterministic: bool
    s: Optional[int] = None
    d: Optional[str] = None
    witness: Optional[str] = None
    carmichael_number: bool = False
    traces: List[Dict[str, Any]] = field(default_factory=list)


def calculate_confidence_strings(k: int, is_deterministic: bool) -> tuple[str, str, str]:
    """Calculate human-readable confidence percentage, formula, and error bound.

    Args:
        k: Number of Miller-Rabin iterations.
        is_deterministic: Whether deterministic proof was applied.

    Returns:
        tuple of (confidence_str, formula_str, error_prob_str).
    """
    if is_deterministic:
        return "100.0000% (Deterministic Proof)", "Deterministic Base Set Coverage", "0.0"

    # Error probability is at most 4^(-k) = 2^(-2k)
    # For k=40, 4^-40 ≈ 8.2718061e-25
    error_prob_float = 4.0 ** (-k) if k < 300 else 0.0
    error_prob_str = f"{error_prob_float:.4e}" if error_prob_float > 0 else f"< 10^(-{int(k * 0.602)})"
    
    # Generate 99.999... representation
    nines_count = int(k * 0.602)  # log10(4) ≈ 0.60206
    if nines_count <= 2:
        confidence_str = f"{(1 - (4 ** -k)) * 100:.4f}%"
    else:
        # Display high precision confidence string
        num_decimals = min(nines_count + 2, 24)
        ninety_nines = "9" * min(num_decimals, 20)
        confidence_str = f"99.{ninety_nines}%"

    formula_str = f"1 - 4^(-{k}) = 1 - 2^(-{2*k})"
    return confidence_str, formula_str, error_prob_str


def miller_rabin_test(
    n: int,
    iterations: int = 40,
    use_custom_modpow: bool = False,
    deterministic_for_small: bool = True,
    max_traces_to_keep: int = 10,
) -> PrimalityResult:
    """Execute the Miller-Rabin primality test on an arbitrary-precision integer n.

    Args:
        n: The integer to test (can be up to 1024+ bits).
        iterations: Number of randomized Miller-Rabin rounds (k). Default 40.
        use_custom_modpow: If True, uses the custom square-and-multiply algorithm.
        deterministic_for_small: If True, uses deterministic bases for n < 2^64.
        max_traces_to_keep: Maximum number of round details to keep in trace output.

    Returns:
        PrimalityResult containing primality verdict, execution time, confidence metrics,
        decomposition values, and witness details (if composite).
    """
    start_ns = time.perf_counter_ns()
    metrics = get_integer_metrics(n)
    bit_len = metrics["bit_length"]
    dec_len = metrics["decimal_length"]
    num_str = str(n)

    # 1. Fast Path Pre-checks (Edge cases, Even numbers, First 100 small primes)
    is_prime_pre, reason_pre, witness_pre = fast_precheck(n)
    if is_prime_pre is not None:
        elapsed_ns = time.perf_counter_ns() - start_ns
        is_p = is_prime_pre
        conf_str = "100.0000% (Deterministic)" if is_p else "100.00% (Definite Composite)"
        return PrimalityResult(
            number=num_str,
            is_prime=is_p,
            result="Prime" if is_p else "Composite",
            confidence_level=conf_str,
            confidence_formula="Small Prime Sieve Pre-check",
            error_probability="0.0",
            bit_length=bit_len,
            decimal_length=dec_len,
            execution_time_ns=elapsed_ns,
            execution_time_us=round(elapsed_ns / 1_000.0, 3),
            execution_time_ms=round(elapsed_ns / 1_000_000.0, 4),
            rounds_completed=0,
            method="Small Prime Pre-check",
            deterministic=True,
            s=None,
            d=None,
            witness=str(witness_pre) if witness_pre is not None else None,
            carmichael_number=False,
            traces=[{
                "round_index": 0,
                "base_a": "N/A",
                "initial_x": "N/A",
                "passed": is_p,
                "reason": reason_pre,
            }],
        )

    # 2. Decompose n - 1 into 2^s * d with d odd
    s, d = decompose_n_minus_one(n)
    d_str = str(d)

    # 3. Determine testing strategy: Deterministic (if n < 2^64) or Randomized Probabilistic
    is_deterministic = deterministic_for_small and (bit_len <= 64)
    if is_deterministic:
        # Filter bases strictly less than n
        bases_to_test = [b for b in DETERMINISTIC_BASES_64 if b < n]
        total_rounds = len(bases_to_test)
        method_name = "Deterministic Miller-Rabin (64-bit)"
    else:
        total_rounds = max(1, iterations)
        method_name = f"Probabilistic Miller-Rabin ({total_rounds} rounds)"

    rounds_completed = 0
    traces: List[Dict[str, Any]] = []
    witness_found: Optional[int] = None
    is_composite = False
    tested_bases_set = set()

    for r_idx in range(total_rounds):
        if is_deterministic:
            a = bases_to_test[r_idx]
        else:
            # Pick a cryptographically secure random base a in [2, n - 2]
            # Avoid picking duplicate bases if possible
            for _ in range(20):
                a = secrets.randbelow(n - 3) + 2
                if a not in tested_bases_set:
                    break
            tested_bases_set.add(a)

        rounds_completed += 1

        # Compute x = a^d mod n
        x = mod_exp(a, d, n, use_custom=use_custom_modpow)
        initial_x = x

        round_passed = False
        round_reason = ""

        # Condition 1: a^d = 1 (mod n) or a^d = -1 (mod n)
        if x == 1 or x == n - 1:
            round_passed = True
            round_reason = "Base passed condition: x == 1 or x == n-1"
        else:
            # Condition 2: repeat squaring s - 1 times
            for step in range(1, s):
                x = mod_exp(x, 2, n, use_custom=use_custom_modpow)
                if x == n - 1:
                    round_passed = True
                    round_reason = f"Base passed squaring step {step}/{s-1}: x == n-1"
                    break
                if x == 1:
                    # Non-trivial square root of 1 found modulo n -> definitely composite
                    round_passed = False
                    round_reason = f"Non-trivial square root of 1 found at step {step}"
                    break

            if not round_passed and not round_reason:
                round_reason = "Completed all s-1 squarings without reaching n-1"

        if len(traces) < max_traces_to_keep:
            traces.append({
                "round_index": rounds_completed,
                "base_a": str(a),
                "initial_x": str(initial_x) if len(str(initial_x)) <= 80 else str(initial_x)[:40] + "..." + str(initial_x)[-38:],
                "passed": round_passed,
                "reason": round_reason,
            })

        if not round_passed:
            is_composite = True
            witness_found = a
            break

    elapsed_ns = time.perf_counter_ns() - start_ns

    # Check if number was a Carmichael number (e.g., 561, 1105, 1729, 2465, 2821, 6601, 8911)
    # Carmichael numbers pass Fermat test a^(n-1) = 1 (mod n) for all gcd(a,n)=1,
    # but Miller-Rabin catches them!
    is_carmichael = False
    if is_composite and witness_found is not None:
        # Check if it satisfies Fermat test for witness base
        fermat_val = mod_exp(witness_found, n - 1, n, use_custom=False)
        if fermat_val == 1 and math.gcd(witness_found, n) == 1:
            is_carmichael = True

    is_prime_result = not is_composite
    conf_str, formula_str, error_prob_str = calculate_confidence_strings(
        rounds_completed, is_deterministic and is_prime_result
    )

    if not is_prime_result:
        conf_str = "100.00% (Definite Composite)"
        formula_str = "Miller-Rabin Witness Discovered"
        error_prob_str = "0.0"

    return PrimalityResult(
        number=num_str,
        is_prime=is_prime_result,
        result="Prime" if is_prime_result else "Composite",
        confidence_level=conf_str,
        confidence_formula=formula_str,
        error_probability=error_prob_str,
        bit_length=bit_len,
        decimal_length=dec_len,
        execution_time_ns=elapsed_ns,
        execution_time_us=round(elapsed_ns / 1_000.0, 3),
        execution_time_ms=round(elapsed_ns / 1_000_000.0, 4),
        rounds_completed=rounds_completed,
        method=method_name,
        deterministic=is_deterministic and is_prime_result,
        s=s,
        d=d_str if len(d_str) <= 120 else d_str[:60] + "..." + d_str[-58:],
        witness=str(witness_found) if witness_found is not None else None,
        carmichael_number=is_carmichael,
        traces=traces,
    )
