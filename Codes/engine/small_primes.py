"""Small Primes Lookup Table and Fast Pre-Checks.

Contains precomputed small primes and sieve pre-filtering to instantly classify
trivial edge cases and eliminate composites before running Miller-Rabin.
"""

from typing import Optional, Tuple, List

# The first 100 prime numbers (2 through 541)
FIRST_100_PRIMES: List[int] = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
    233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
    283, 293, 307, 311, 313, 317, 331, 337, 347, 349,
    353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
    419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
    467, 479, 487, 491, 499, 503, 509, 521, 523, 541
]

FIRST_100_PRIMES_SET = set(FIRST_100_PRIMES)


def fast_precheck(n: int) -> Tuple[Optional[bool], Optional[str], Optional[int]]:
    """Execute rapid deterministic pre-checks on integer n.

    Filters trivial non-primes (<= 1), even numbers, and composites divisible
    by any of the first 100 small primes.

    Args:
        n: Integer to test.

    Returns:
        A tuple of (is_prime, method_or_reason, witness):
            - If primality is conclusively determined:
                (True, "Small Prime Lookup", None) or
                (False, "Trivial / Divisible by <p>", witness_p)
            - If inconclusive (passes pre-check and requires Miller-Rabin):
                (None, None, None)
    """
    if n <= 1:
        return False, f"Values <= 1 are not prime by definition (n={n})", None

    if n in FIRST_100_PRIMES_SET:
        return True, "Definite Prime (Found in Precomputed Small Primes Table)", None

    if n % 2 == 0:
        return False, "Composite (Even integer > 2, divisible by 2)", 2

    # Check divisibility against the remaining small primes
    for p in FIRST_100_PRIMES[1:]:  # skip 2 since already checked
        if n % p == 0:
            return False, f"Composite (Divisible by small prime {p})", p

    # Inconclusive - requires Miller-Rabin test
    return None, None, None
