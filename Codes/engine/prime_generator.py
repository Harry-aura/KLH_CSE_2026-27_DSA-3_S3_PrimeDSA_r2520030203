"""Cryptographic-grade Arbitrary-Precision Prime Number Generator.

Generates random probable primes with configurable bit lengths (e.g. 128, 256, 512, 1024 bits)
using cryptographically secure random bits, small-prime sieve filtering, and Miller-Rabin validation.
"""

import secrets
import time
from typing import Tuple

from .small_primes import FIRST_100_PRIMES
from .miller_rabin import miller_rabin_test, PrimalityResult


def generate_probable_prime(
    bit_length: int = 1024,
    iterations: int = 40,
) -> Tuple[int, int, float, PrimalityResult]:
    """Generate a random cryptographically strong probable prime of the specified bit length.

    Args:
        bit_length: Desired bit length (e.g. 16, 64, 128, 256, 512, 1024). Minimum 3.
        iterations: Number of Miller-Rabin iterations for verification.

    Returns:
        A tuple of (prime_integer, candidates_tested, generation_time_ms, validation_result).

    Raises:
        ValueError: If bit_length < 2.
    """
    if bit_length < 2:
        raise ValueError(f"Bit length must be at least 2, got {bit_length}")

    if bit_length == 2:
        # 2-bit primes are 2 and 3
        p = secrets.choice([2, 3])
        res = miller_rabin_test(p, iterations=iterations)
        return p, 1, 0.01, res

    start_time = time.perf_counter()
    candidates_tested = 0

    while True:
        candidates_tested += 1
        # Generate random bits
        candidate = secrets.randbits(bit_length)
        # Ensure exact bit length by setting the MSB, and make it odd by setting the LSB
        candidate |= (1 << (bit_length - 1)) | 1

        # Fast small primes divisibility sieve filter
        divisible_by_small = False
        for p in FIRST_100_PRIMES:
            if candidate == p:
                break
            if candidate % p == 0:
                divisible_by_small = True
                break

        if divisible_by_small:
            continue

        # Run Miller-Rabin primality test
        result = miller_rabin_test(
            candidate,
            iterations=iterations,
            use_custom_modpow=False,
            deterministic_for_small=True,
        )

        if result.is_prime:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 3)
            return candidate, candidates_tested, elapsed_ms, result
