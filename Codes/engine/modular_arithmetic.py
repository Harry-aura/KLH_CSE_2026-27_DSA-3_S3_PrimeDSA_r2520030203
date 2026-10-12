"""Modular Arithmetic Engine for Arbitrary-Precision Integers.

Provides fast bitwise decomposition, explicit square-and-multiply modular exponentiation,
and wrapper utilities for high-performance primality testing.
"""

from typing import Tuple


def decompose_n_minus_one(n: int) -> Tuple[int, int]:
    """Decompose an odd integer (n - 1) into 2^s * d where d is odd.

    Args:
        n: An odd integer greater than 2.

    Returns:
        A tuple (s, d) where:
            - s (int): Non-negative integer representing the highest power of 2 dividing n - 1.
            - d (int): Odd integer such that n - 1 == (2 ** s) * d.

    Raises:
        ValueError: If n <= 2 or n is even.
    """
    if n <= 2:
        raise ValueError(f"Decomposition requires n > 2, got {n}")
    if n % 2 == 0:
        raise ValueError(f"Decomposition requires odd n, got even number {n}")

    n_minus_1 = n - 1
    # Isolate lowest set bit using two's complement bitwise AND: (x & -x)
    lowest_bit = n_minus_1 & -n_minus_1
    s = lowest_bit.bit_length() - 1
    d = n_minus_1 >> s

    return s, d


def square_and_multiply(base: int, exponent: int, modulus: int) -> int:
    """Compute (base ** exponent) % modulus using square-and-multiply (binary exponentiation).

    Implemented from scratch for arbitrary-precision BigInt to prevent intermediate overflow
    and allow deep algorithmic inspection.

    Args:
        base: The base integer (BigInt).
        exponent: The non-negative exponent (BigInt).
        modulus: The positive modulus (BigInt).

    Returns:
        The integer result of (base ** exponent) % modulus in [0, modulus - 1].

    Raises:
        ValueError: If modulus <= 0 or exponent < 0.
    """
    if modulus <= 0:
        raise ValueError(f"Modulus must be positive, got {modulus}")
    if exponent < 0:
        raise ValueError(f"Exponent must be non-negative, got {exponent}")
    if modulus == 1:
        return 0

    result = 1
    base = base % modulus

    while exponent > 0:
        # If the current least significant bit is 1, multiply into result
        if exponent & 1:
            result = (result * base) % modulus
        # Square the base for the next bit
        base = (base * base) % modulus
        exponent >>= 1

    return result


def mod_exp(base: int, exponent: int, modulus: int, use_custom: bool = False) -> int:
    """Modular exponentiation dispatcher.

    Allows toggling between custom square-and-multiply implementation
    and Python's C-accelerated 3-argument pow(base, exponent, modulus).

    Args:
        base: Base integer.
        exponent: Exponent integer.
        modulus: Modulus integer.
        use_custom: If True, execute explicit pure-Python square-and-multiply.
                    If False, execute C-optimized 3-argument pow().

    Returns:
        (base ** exponent) % modulus.
    """
    if use_custom:
        return square_and_multiply(base, exponent, modulus)
    return pow(base, exponent, modulus)


def get_integer_metrics(n: int) -> dict:
    """Calculate integer metadata (bit length, byte length, decimal length, hex length).

    Args:
        n: Target integer.

    Returns:
        Dictionary with bit_length, decimal_length, byte_length, and hex_length.
    """
    if n == 0:
        return {
            "bit_length": 0,
            "decimal_length": 1,
            "byte_length": 0,
            "hex_length": 1,
        }
    abs_n = abs(n)
    bit_len = abs_n.bit_length()
    return {
        "bit_length": bit_len,
        "decimal_length": len(str(abs_n)),
        "byte_length": (bit_len + 7) // 8,
        "hex_length": len(hex(abs_n)[2:]),
    }
